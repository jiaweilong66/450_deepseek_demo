import cv2
import numpy as np
from paddleocr import PaddleOCR
from PIL import Image, ImageDraw, ImageFont
# import math
import logging
logging.getLogger('ppocr').setLevel(logging.WARNING)

class OcrDetector():
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang="ch", use_gpu=True)
        self.target_name=["盐酸苯环壬酯片","感冒灵颗粒","布洛芬缓释胶囊","云南白药创可贴"]
        self.font_path = "./SIMFANG.TTF"  # Windows系统字体
        self.pillow_font = ImageFont.truetype(self.font_path, 20)

    def detect(self,frame):
        ocr_result = self.ocr.ocr(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), cls=True)
    
        # 当检测到结果时进行处理
        if ocr_result[0]:
            processed_frame,res = self.process_ocr_results(frame, ocr_result[0])
            print(res)
        else:
            processed_frame = frame
        return processed_frame,res
    
    def process_ocr_results(self,image, results):
        ocr_results = []
        """使用Pillow处理标注绘制"""
        # 转换OpenCV图像到Pillow格式
        pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)

        for line in results:
            box = np.array(line[0], dtype=np.int32)
            text = line[1][0]
            confidence = line[1][1]


            if text in self.target_name:

                # 计算最小外接矩形
                rect = cv2.minAreaRect(box.reshape(-1, 1, 2))
                (cx, cy), (w, h), angle = rect

                # 绘制外接矩形（Pillow多边形）
                draw.polygon([tuple(point) for point in box], outline=(0, 255, 0), width=2)

                # 绘制中心点
                center = (int(cx), int(cy))
                draw.ellipse([(center[0]-3, center[1]-3), 
                            (center[0]+3, center[1]+3)],
                            fill=(255, 0, 0))

                # 构造显示信息
                info_text = f"{text}"
                # info_text = f"{text} {confidence:.2f}\n({cx:.1f},{cy:.1f}) {angle:.1f}°"
                
                # 计算文字绘制位置（避开边界）
                text_y = box[0][1] - 30 if box[0][1] > 40 else box[0][1] + 10
                draw.text((box[0][0], text_y), 
                        info_text, 
                        font=self.pillow_font,
                        fill=(0, 0, 255))
                ocr_results.append([text,center,angle])
        cv_img=cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        return cv_img,ocr_results


if __name__=="__main__":
    ocr=OcrDetector()
    cap=cv2.VideoCapture(1)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        processed_frame,res=ocr.detect(frame)
        print(res)

       
        cv2.imshow('Enhanced OCR Demo', processed_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()