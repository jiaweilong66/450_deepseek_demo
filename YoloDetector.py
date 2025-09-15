import cv2
import numpy as np

class YoloDetector:
    def __init__(self, 
                 model_path='yolov8s-seg.onnx', 
                 classes_path='coco.names',
                 conf_threshold=0.5,
                 mask_threshold=0.5,
                 inp_size=(640, 640),
                 use_gpu=False):
        """
        初始化实例分割器
        :param model_path: ONNX模型路径
        :param classes_path: 类别文件路径
        :param conf_threshold: 检测置信度阈值
        :param mask_threshold: 分割掩码阈值
        :param inp_size: 模型输入尺寸 (W, H)
        :param use_gpu: 是否启用GPU加速
        """
        # 初始化参数
        self.conf_threshold = conf_threshold
        self.mask_threshold = mask_threshold
        self.inp_width, self.inp_height = inp_size
        self.classes = self._load_classes(classes_path)
        self.num_classes = len(self.classes)

        self.target_name=["banana","apple","orange"]
        
        # 加载模型
        self.net = cv2.dnn.readNet(model_path)
        if use_gpu:
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        else:
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            
        # 缓存参数
        self.scale = None
        self.pads = None
        self.orig_size = None

    def _load_classes(self, path):
        with open(path, 'r') as f:
            return f.read().splitlines()

    def _preprocess(self, frame):
        """预处理输入帧"""
        h, w = frame.shape[:2]
        scale = min(self.inp_width/w, self.inp_height/h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # 创建填充后的画布
        resized = cv2.resize(frame, (new_w, new_h))
        canvas = np.full((self.inp_height, self.inp_width, 3), 114, dtype=np.uint8)
        start_x = (self.inp_width - new_w) // 2
        start_y = (self.inp_height - new_h) // 2
        canvas[start_y:start_y+new_h, start_x:start_x+new_w] = resized
        
        # 保存预处理参数
        self.scale = scale
        self.pads = (start_x, start_y)
        self.orig_size = (w, h)
        return canvas

    def _postprocess(self, frame, outputs):
        """后处理检测结果"""
        orig_w, orig_h = self.orig_size
        pad_x, pad_y = self.pads
        
        detections = outputs[0].squeeze().T
        mask_proto = outputs[1].squeeze()
        
        boxes, confidences, class_ids, mask_coeffs = [], [], [], []
        
        # 解析检测结果
        for det in detections:
            scores = det[4:4+self.num_classes]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            
            if confidence < self.conf_threshold:
                continue
                
            # 坐标转换
            cx = (det[0] - pad_x) / self.scale
            cy = (det[1] - pad_y) / self.scale
            w = det[2] / self.scale
            h = det[3] / self.scale
            
            x1 = int(max(0, cx - w/2))
            y1 = int(max(0, cy - h/2))
            x2 = int(min(orig_w, cx + w/2))
            y2 = int(min(orig_h, cy + h/2))
            
            boxes.append([x1, y1, x2, y2])
            confidences.append(float(confidence))
            class_ids.append(class_id)
            mask_coeffs.append(det[4+self.num_classes:])
        
        # 应用NMS
        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.conf_threshold, 0.5)
        results = []
        
        if len(indices) > 0:
            indices = indices.flatten()
            
            for idx in indices:
                x1, y1, x2, y2 = boxes[idx]
                class_id = class_ids[idx]
                mask_coeff = mask_coeffs[idx]
                
                # 生成分割掩码
                coeff = np.array(mask_coeff).reshape(1, -1)
                masks = coeff @ mask_proto.reshape(32, -1)
                masks = 1 / (1 + np.exp(-masks))
                
                # 全图尺寸mask处理
                mask = cv2.resize(masks.reshape(160, 160), (orig_w, orig_h),
                                interpolation=cv2.INTER_LINEAR)
                mask = (mask > self.mask_threshold).astype(np.uint8) * 255
                roi_mask = mask[y1:y2, x1:x2]
                
                # 轮廓检测与旋转框计算
                contours, _ = cv2.findContours(roi_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if contours:
                    max_contour = max(contours, key=cv2.contourArea)
                    if cv2.contourArea(max_contour) < 100:
                        continue
                    
                    global_contour = max_contour + (x1, y1)
                    rect = cv2.minAreaRect(global_contour)
                    (cx, cy), (w, h), angle = rect
                    
                    # 角度校正
                    if w < h:
                        angle += 90
                    
                    # 转换旋转框坐标
                    box_pts = cv2.boxPoints(rect)
                    box_pts = np.intp(box_pts)

                    if self.classes[class_id] in self.target_name:

                    
                        # 收集结果
                        results.append([self.classes[class_id],(int(cx), int(cy)),int(angle)])
                        # results.append({
                        #     'class': self.classes[class_id],
                        #     'confidence': confidences[idx],
                        #     'center': (int(cx), int(cy)),
                        #     'angle': float(angle),
                        #     'bbox': (x1, y1, x2, y2),
                        #     'rotated_box': box_pts.tolist()
                        # })
                        
                        # 绘制结果
                        
                        self._draw_detections(frame, x1, y1, x2, y2, 
                                            self.classes[class_id], confidences[idx],
                                            global_contour, box_pts)
        
        return frame, results

    def _draw_detections(self, frame, x1, y1, x2, y2, class_name, confidence, contour, rot_box):
        """绘制检测结果"""
        # 绘制原始检测框
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
        
        # 绘制类别标签
        label = f'{class_name} '
        # label = f'{class_name} {confidence:.2f}'
        cv2.putText(frame, label, (x1, y1-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
        
        # 绘制实际轮廓
        # cv2.drawContours(frame, [contour], -1, (0,255,255), 1)
        
        # 绘制旋转框
        # cv2.drawContours(frame, [rot_box], 0, (0,0,255), 2)
        
        # 绘制中心点和角度
        center = rot_box.mean(axis=0).astype(int)
        cv2.circle(frame, tuple(center), 3, (255,0,0), -1)
        # cv2.putText(frame, f'{self.classes.index(class_name)}:{confidence:.1f}°', 
        #            (center[0]+10, center[1]), 
        #            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1)

    def process_frame(self, frame):
        """
        处理单帧图像
        :param frame: 输入BGR图像
        :return: 处理后的帧，检测结果列表
        """
        # 预处理
        blob = cv2.dnn.blobFromImage(self._preprocess(frame), 1/255.0, swapRB=True)
        
        # 推理
        self.net.setInput(blob)
        outputs = self.net.forward(self.net.getUnconnectedOutLayersNames())
        
        # 后处理
        return self._postprocess(frame.copy(), outputs)

    def release(self):
        """释放资源"""
        pass  # OpenCV模型会自动释放

# 使用示例
if __name__ == "__main__":
    # 初始化分割器
    segmenter = YoloDetector(
        model_path='./yolo11n-seg.onnx',
        classes_path='./coco.names',
        conf_threshold=0.5,
        mask_threshold=0.3,
        use_gpu=True
    )
    
    # 初始化摄像头
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 处理帧
        processed_frame, results = segmenter.process_frame(frame)
        
        # 显示结果
        cv2.imshow('Instance Segmentation', processed_frame)
        print(f"检测到 {len(results)} 个对象: {results}")
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()