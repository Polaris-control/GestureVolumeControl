import cv2
import time
import HandTrackingMoudle as htm 
import numpy as np
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

cap = cv2.VideoCapture(0)  # 打开摄像头 / Open the webcam

wCam, hCam = 640, 480  # 设置摄像头宽高 / Set webcam width and height

cap.set(3, wCam)  # 设置视频帧宽度 / Set video frame width
cap.set(4, hCam)  # 设置视频帧高度 / Set video frame height

pTime = 0  # 初始化前一帧的时间 / Initialize previous frame time

detector = htm.handDetector(detectionCon=0.7)  # 初始化手部检测器，检测置信度为0.7 / Initialize hand detector with detection confidence of 0.7

# 初始化音量控制 / Initialize volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
volRange = volume.GetVolumeRange()

minVol = volRange[0] 
maxVol = volRange[1] 
volBar = 400  # 音量条的初始位置 / Initial position of volume bar
vol = 0  # 当前音量 / Current volume
volper = 0  # 音量百分比 / Volume percentage

if not cap.isOpened():  # 检查摄像头是否打开 / Check if the webcam is open
    print("Cannot open camera")
else:
    while True:
        ret, img = cap.read()  # 读取视频帧 / Read a video frame
        if not ret:  # 检查是否成功读取帧 / Check if frame reading was successful
            print("Cannot read image")
            break
        
        img = detector.findHands(img)  # 检测并标记手部 / Detect and mark hands
        lmList = detector.findPosition(img, draw=False)  # 获取手部关键点位置 / Get hand landmark positions
        
        if len(lmList) != 0:  # 检查是否检测到手部 / Check if any hand is detected
            print(lmList[4], lmList[8])

            x1, y1 = lmList[4][1], lmList[4][2]  # 获取大拇指指尖坐标 / Get the coordinates of the thumb tip
            x2, y2 = lmList[8][1], lmList[8][2]  # 获取食指指尖坐标 / Get the coordinates of the index finger tip

            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2  # 计算两个指尖的中点 / Calculate the midpoint between the two fingertips

            cv2.circle(img, (x1, y1), 15, (255, 0, 0), cv2.FILLED)  # 画出大拇指指尖的圆 / Draw a circle at the thumb tip
            cv2.circle(img, (x2, y2), 15, (255, 0, 0), cv2.FILLED)  # 画出食指指尖的圆 / Draw a circle at the index finger tip
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)  # 画出两指尖之间的线 / Draw a line between the two fingertips
            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)  # 画出中点的圆 / Draw a circle at the midpoint

            length = math.hypot(x2 - x1, y2 - y1)  # 计算两个指尖之间的距离 / Calculate the distance between the two fingertips

            # 手部范围 50 - 300 / Hand Range 50 - 300
            # 音量范围 -65 - 0 / Volume Range -65 - 0

            vol = np.interp(length, [50, 300], [minVol, maxVol])  # 将距离映射到音量范围 / Map the length to the volume range
            volBar = np.interp(length, [50, 300], [400, 150])  # 将距离映射到音量条位置 / Map the length to the volume bar position
            volper = np.interp(length, [50, 300], [0, 100])  # 将距离映射到音量百分比 / Map the length to the volume percentage
            print(int(length), vol)
            volume.SetMasterVolumeLevel(vol, None)  # 设置音量 / Set the volume

            if length < 50:  # 如果距离小于50，改变中点圆的颜色 / If the length is less than 50, change the color of the midpoint circle
                cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

        # 画出音量条 / Draw the volume bar
        cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, f'{int(volper)} %', (50, 430), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)

        # 计算并显示帧率 / Calculate and display the frame rate
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)

        cv2.imshow('img', img)  # 显示图像 / Display the image
        if cv2.waitKey(1) == 27:  # 按 'Esc' 键退出 / Press 'Esc' to exit
            break

    cap.release()  # 释放摄像头 / Release the webcam
    cv2.destroyAllWindows()  # 关闭所有窗口 / Close all windows
