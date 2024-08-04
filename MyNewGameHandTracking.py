import cv2
import time
import HandTrackingMoudle as htm

pTime = 0
cTime = 0

video_path = r"C:\Users\Administrator\GestureVolumeControl\TestVideo.mp4"

cap = cv2.VideoCapture(video_path)
detector = htm.handDetector()
while True:
    success, img = cap.read()
    img = detector.findHands(img, draw=True)
    lmList = detector.findPosition(img, handNo=0, personDraw=False)
    if len(lmList) != 0:
        print(lmList[4])

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.imshow("Image", img)
    cv2.waitKey(1)
