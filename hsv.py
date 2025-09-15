import cv2
import numpy as np

def nothing(x):
    pass

# 创建一个窗口
cv2.namedWindow('HSV Thresholding')

# 创建滑块来调节HSV值
cv2.createTrackbar('H_min', 'HSV Thresholding', 0, 179, nothing)
cv2.createTrackbar('H_max', 'HSV Thresholding', 179, 179, nothing)
cv2.createTrackbar('S_min', 'HSV Thresholding', 0, 255, nothing)
cv2.createTrackbar('S_max', 'HSV Thresholding', 255, 255, nothing)
cv2.createTrackbar('V_min', 'HSV Thresholding', 0, 255, nothing)
cv2.createTrackbar('V_max', 'HSV Thresholding', 255, 255, nothing)

# 打开摄像头
cap = cv2.VideoCapture(0)

while True:
    # 读取摄像头的画面
    ret, frame = cap.read()
    if not ret:
        break

    # 转换到HSV颜色空间
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 获取滑块的值
    h_min = cv2.getTrackbarPos('H_min', 'HSV Thresholding')
    h_max = cv2.getTrackbarPos('H_max', 'HSV Thresholding')
    s_min = cv2.getTrackbarPos('S_min', 'HSV Thresholding')
    s_max = cv2.getTrackbarPos('S_max', 'HSV Thresholding')
    v_min = cv2.getTrackbarPos('V_min', 'HSV Thresholding')
    v_max = cv2.getTrackbarPos('V_max', 'HSV Thresholding')

    # 设置阈值范围并进行掩膜
    lower_bound = np.array([h_min, s_min, v_min])
    upper_bound = np.array([h_max, s_max, v_max])
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # 查找轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 在图像上绘制轮廓
    if contours:
        max_contour = max(contours, key=cv2.contourArea)
        max_area = cv2.contourArea(max_contour)
        cv2.drawContours(frame, [max_contour], -1, (0, 255, 0), 3)
        print(f'Max Contour Area: {max_area}')


    cv2.imshow('HSV Thresholding', frame)

    # 按下 'q' 键退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放摄像头并关闭窗口
cap.release()
cv2.destroyAllWindows()
