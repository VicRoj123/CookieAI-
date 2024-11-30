import threading
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Listener, KeyCode
import cv2
import numpy as np
from time import time, sleep
import schedule
import win32gui
import win32ui
import win32con
import win32api
import sys



toggleKey = KeyCode(char= 'p')
offKey = KeyCode(char='o')
exitKey = KeyCode(char='l')
clicking = False
running = False

mouse = MouseController()


def upgradeClicker():
    mouse.position = (2275,110)
    mouse.click(Button.left,1)
    print('Upgrade clicked')


schedule.every(5).seconds.do(upgradeClicker)

def upgradeCapture():
    w = 2350
    h = 1080

    hwnd = None
    wDC = win32gui.GetWindowDC(hwnd)
    dcObj = win32ui.CreateDCFromHandle(wDC)
    cDC = dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()
    dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((2100, 0), (w, h), dcObj, (2250, 0), win32con.SRCCOPY)

    signedIntsArray = dataBitMap.GetBitmapBits(True)
    img = np.frombuffer(signedIntsArray, dtype='uint8')
    img.shape = (h, w, 4)

    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())
    return img

def clicker():
    from time import time
    loopTime = time()

    while True:
        schedule.run_pending()
        if clicking:
            #mouse.position = (mouse.position[0], mouse.position[1])
            mouse.position = (300,550)
            mouse.click(Button.left,1)


        upgradeDisplay = upgradeCapture()
        upgradeDisplay = cv2.resize(upgradeDisplay, (2250,1080))
        upgradeDisplay.setflags(write=True)

        #rgb_color = np.uint8([[[102, 255, 102]]])
        hsv = cv2.cvtColor(upgradeDisplay, cv2.COLOR_BGR2HSV)
        lower = np.array([45,150,20])
        upper = np.array([65,255,255])

        mask = cv2.inRange(hsv, lower, upper)
        #cv2.imshow('mask', mask)

        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


        if len(contours) != 0:
            for contour in contours:

                if cv2.contourArea(contour) > 0:
                    print("hello")
                    x, y, w, h = cv2.boundingRect(contour)
                    #print(f"upgradeDisplay shape: {upgradeDisplay.shape}, dtype: {upgradeDisplay.dtype}")
                    #print(f"x: {x}, y: {y}, w: {w}, h: {h}")

                    cv2.rectangle(upgradeDisplay, (x, y), (x + w, y + h), (0, 0, 255), 3)
                    M = cv2.moments(contour)


                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                    cv2.circle(upgradeDisplay, (int(cx), int(cy)), 7, (255, 0, 0), -1)
                    centerX = cx
                    centerY = cy
                    center = (cx,cy)
                    #print("hello")
                    mouse.position = (centerX+200, centerY)
                    mouse.click(Button.left,1)



        cv2.namedWindow('Upgrade_Image', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Upgrade_Image', 1280, 800)
        cv2.imshow('Upgrade_Image', upgradeDisplay)

        cv2.waitKey(1)
        print('FPS {}'.format(1/(time()-loopTime)))
        loopTime = time()
        sleep(0.01)

def toggle_event(key):
    if key == toggleKey:
        global clicking
        clicking = not clicking
    elif key == offKey:
        clicking = False
    if key == exitKey:
        sys.exit(0)






click_thread = threading.Thread(target=clicker)
click_thread.start()

with Listener(on_press=toggle_event) as listener:
    listener.join()