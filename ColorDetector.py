import cv2
import numpy as np
class ColorDetector:
    def __init__(self):
        # 初始化摄像头
        
        
        # 颜色阈值配置（HSV格式）
        self.color_ranges = {
            "red":    ((0, 100, 100), (10, 255, 255), (0, 0, 255)),
            "green":  ([60, 190, 130], [80, 255, 255], (0, 255, 0)),
            "blue":   ([90, 160, 160], [120, 255, 255], (255, 0, 0)),
            "yellow": ([0, 170, 230], [70, 255, 255], (0, 255, 255))
        }
        
        # 形态学操作核
        self.kernel = np.ones((5,5), np.uint8)
        
        # 检测结果缓存
        self.results = []

    def detect(self,frame):
        self.results = []
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        for color_name, (lower, upper, color) in self.color_ranges.items():
            # 确保所有阈值转换为NumPy数组
            lower = np.array(lower)
            upper = np.array(upper)
            
            if color_name == "red":
                # 红色特殊处理（0-10和160-180范围）
                lower1 = np.array([0, 100, 100])
                upper1 = np.array([10, 255, 255])
                lower2 = np.array([160, 100, 100])
                upper2 = np.array([180, 255, 255])
                mask = cv2.inRange(hsv, lower1, upper1) | cv2.inRange(hsv, lower2, upper2)
            else:
                mask = cv2.inRange(hsv, lower, upper)
            
            # 后续处理保持不变...
            mask = cv2.erode(mask, self.kernel, iterations=1)
            mask = cv2.dilate(mask, self.kernel, iterations=2)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                for cnt in contours:
                    # cnt = max(contours, key=cv2.contourArea)
                    # area = cv2.contourArea(cnt)
                    area = cv2.contourArea(cnt)
                    if area < 5000:
                        continue
                        
                    rect = cv2.minAreaRect(cnt)
                    box = cv2.boxPoints(rect)
                    # box = np.intr0(box)
                    box=np.intp(box)
                    
                    center = tuple(np.intp(rect[0]))
                    angle = rect[2]
                    if angle < -45:
                        angle += 90
                    cv2.circle(img=frame,center=center,radius=5,color=color, thickness=-1)
                    cv2.drawContours(frame, [box], 0, color, 2)
                    cv2.putText(frame, f"{color_name}", (center[0], center[1]-50),cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                    
                    self.results.append([color_name, center, angle])
        
        return frame, self.results
    

if __name__=="__main__":
    cap = cv2.VideoCapture(0)
    color=ColorDetector()
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 执行检测
        processed_frame, results = color.detect(frame)
        
        # 显示结果
        cv2.imshow('Color Detection', processed_frame)
        print("当前帧检测结果：", results)  # 返回结果列表
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()   