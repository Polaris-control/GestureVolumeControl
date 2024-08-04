import cv2
import time
import numpy as np
import HandTrackingMoudle as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# 视频输入和图像尺寸设置
# Video input and image size settings
wCam, hCam = 640, 480
video_path = r"C:\Users\Administrator\GestureVolumeControl\TestVideo.mp4"

# 打开视频文件
# Open the video file
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"Error: Could not open video file at {video_path}.")
    # 视频文件无法打开，退出程序
    # Video file could not be opened, exit the program
    exit()

# 设置视频捕捉的宽度和高度
# Set the width and height of the video capture
cap.set(3, wCam)
cap.set(4, hCam)

pTime = 0  # 上一帧时间
# Previous frame time
pLength = 0  # 上一帧的手指距离
# Previous frame finger distance

# 创建手部检测对象
# Create hand detector object
detector = htm.handDetector()

# 设置音频控制
# Set up audio control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# 获取音量范围
# Get the volume range
volRange = volume.GetVolumeRange()
minVol, maxVol = volRange[0], volRange[1]

# 显示栏音量与系统音量转换规则
# Mapping of display volume to system volume
standard = {
    0: '100', -1: '94', -2: '88', -3: '82', -4: '77', -5: '72', -6: '67', -7: '63', -8: '59', -9: '55',
    -10: '51', -11: '48', -12: '45', -13: '42', -14: '39', -15: '36', -16: '34', -17: '32', -18: '30',
    -19: '30', -20: '26', -21: '24', -22: '22', -23: '21', -24: '20', -25: '18', -26: '17', -27: '16',
    -28: '15', -29: '14', -30: '13', -31: '12', -32: '11', -33: '10', -34: '9', -35: '9', -36: '8', -37: '8',
    -38: '7', -39: '6', -40: '6', -41: '5', -42: '5', -43: '5', -44: '4', -45: '4', -46: '4', -47: '3',
    -48: '3', -49: '3', -50: '2', -51: '2', -52: '2', -53: '2', -54: '2', -55: '1', -56: '1', -57: '1',
    -58: '1', -59: '1', -60: '1', -61: '0', -62: '0', -63: '0', -64: '0', -65: '0', -66: '0', -67: '0',
    -68: '0', -69: '0', -70: '0', -71: '0', -72: '0', -73: '0', -74: '0', -75: '0', -76: '0', -77: '0',
    -78: '0', -79: '0', -80: '0', -81: '0', -82: '0', -83: '0', -84: '0', -85: '0', -86: '0', -87: '0',
    -88: '0', -89: '0', -90: '0', -91: '0', -92: '0', -93: '0', -94: '0', -95: '0', -96: '0', -97: '0',
    -98: '0'
}

while True:
    # 读取视频帧
    # Read video frame
    success, img = cap.read()
    if not success:
        print("Error: Could not read frame from video.")
        # 无法读取视频帧，退出循环
        # Could not read frame, exit the loop
        break

    # 检测手部
    # Detect hands
    img = detector.findHands(img)
    # 检测手的标志，并返回标志点坐标
    # Detect hand landmarks and return landmark positions
    lmList = detector.findPosition(img, personDraw=False)

    if lmList:
        # 获取食指和大拇指的坐标
        # Get the coordinates of the index and thumb fingers
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        # 计算两点的中点坐标
        # Calculate the midpoint coordinates
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        # 在食指和大拇指的指尖绘制圆圈
        # Draw circles on the index and thumb fingertips
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        # 连接食指和大拇指的指尖绘制直线
        # Draw a line connecting the index and thumb fingertips
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

        # 计算手指之间的距离
        # Calculate the distance between the fingers
        cLength = math.hypot(x2 - x1, y2 - y1)
        # 计算当前帧与上一帧的距离差
        # Calculate the difference in distance between current and previous frame
        ranLength = abs(cLength - pLength)

        # 手指距离范围 50-300（根据实际情况自行调整）
        # Finger distance range 50-300 (adjust according to actual situation)
        vol = np.interp(cLength, [50, 300], [minVol, maxVol])
        volBar = np.interp(cLength, [50, 300], [400, 150])
        volPer = standard.get(int(vol), '0')

        # 仅当距离变化大于 10 时才改变音量
        # Only change the volume if the distance change is greater than 10
        if ranLength >= 10:
            volume.SetMasterVolumeLevel(int(vol), None)

        # 如果距离小于等于 50，绘制圆圈
        # If the distance is less than or equal to 50, draw a circle
        if int(cLength) <= 50:
            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        # 绘制音量图
        # Draw the volume bar
        cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)  # 外框
        # Draw the outer rectangle

        if ranLength >= 10:
            cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
            cv2.putText(img, str(int(volPer)) + "%", (50, 430), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
        else:
            # 显示当前系统音量
            # Display the current system volume
            fixVolume = volume.GetMasterVolumeLevel()
            fixLength = np.interp(fixVolume, [minVol, maxVol], [50, 300])
            fixVolBar = np.interp(fixLength, [50, 300], [400, 150])
            fixVolPer = standard.get(int(fixVolume), '0')
            cv2.rectangle(img, (50, int(fixVolBar)), (85, 400), (255, 0, 0), cv2.FILLED)
            cv2.putText(img, str(int(fixVolPer)) + "%", (50, 430), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)

        # 更新上一帧的距离
        # Update the previous frame distance
        pLength = cLength

    # 计算 FPS
    # Calculate FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    # 显示 FPS 信息
    # Display FPS information
    cv2.putText(img, "FPS:" + str(int(fps)), (20, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)

    # 显示图像
    # Show the image
    cv2.imshow("Image", img)
    # 按 'q' 键退出循环
    # Press 'q' key to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放视频捕捉对象和关闭所有 OpenCV 窗口
# Release the video capture object and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
