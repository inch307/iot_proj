import serial
import time
import signal
import threading
import numpy as np
import cv2

line = [] #라인 단위로 데이터 가져올 리스트 변수
img = []

port = 'COM4' # 시리얼 포트
baud = 1000000 # 시리얼 보드레이트(통신속도)

exitThread = False   # 쓰레드 종료용 변수

#쓰레드 종료용 시그널 함수
def handler(signum, frame):
     exitThread = True

def YUV2RGB( yuv ):
    rgb = [[],[],[]]
    for yuv_line in yuv:
        line_r = []
        line_g = []
        line_b = []
        for i in range(320):
            U = yuv_line[i*4]
            Y0 = yuv_line[i*4+1]
            V = yuv_line[i*4+2]
            Y1 = yuv_line[i*4+3]

            R0 = int(Y0)
            G0 = int(Y0)
            B0 = int(Y0)

            R1 = int(Y1)
            G1 = int(Y1)
            B1 = int(Y1)

            # R0 = int(Y0 + 1.14*V)
            # G0 = int(Y0 - 0.395*U - 0.581*V)
            # B0 = int(Y0 + 2.032*U)

            # R1 = int(Y1 + 1.14*V)
            # G1 = int(Y1 - 0.395*U - 0.581*V)
            # B1 = int(Y1 + 2.032*U)

            # R0 = int(Y0 + 1.4075*(V-128))
            # G0 = int(Y0 - 0.3455*(U-128) - 0.7169*(V-128))
            # B0 = int(Y0 + 1.7790*(U-128))

            # R1 = int(Y1 + 1.4075*(V-128))
            # G1 = int(Y1 - 0.3455*(U-128) - 0.7169*(V-128))
            # B1 = int(Y1 + 1.7790*(U-128))

            line_r.append(R0)
            line_r.append(R1)
            line_g.append(G0)
            line_g.append(G1)
            line_b.append(B0)
            line_b.append(B1)
        rgb[0].append(line_r)
        rgb[1].append(line_g)
        rgb[2].append(line_b)
    rgb = np.array(rgb) # (c, y, x) => (y, x ,c)
    rgb = np.transpose(rgb, (1, 2, 0))
    print(rgb.shape)
    return rgb

#본 쓰레드
def readThread(ser):
    global line
    global exitThread
    global img
    file_n = 0
    while not exitThread:
        #데이터가 있다면
        for c in ser.read():
            line.append(c)
            if (len(line) == 1280):
                line_cp = line[:]
                img.append(line_cp)
                print(len(img))
                del line[:]
            if (len(img) == 480):
                img_cp = img[:]
                rgb_img = YUV2RGB(img_cp)
                cv2.imwrite('testgray.png',rgb_img)
                file_n += 1
                del img[:]        

if __name__ == "__main__":
    #종료 시그널 등록
    signal.signal(signal.SIGINT, handler)

    ser = serial.Serial(port, baud, timeout=0)

    thread = threading.Thread(target=readThread, args=(ser,))

    thread.start()