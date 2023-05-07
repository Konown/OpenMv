import binascii, os
import sensor, image, time, math, pyb, json, lcd
from pyb import LED

import myuart
import globalvar

CHECK_Send = 0x22
CHECK_Change_Thresh = 0x31
CHECK_Negative = 0x30

CHECK_Write_To_File1 = 0x23
CHECK_Remove_Files1 = 0x24
CHECK_Read_From_Files1 = 0x25

key0 = []

def send_threshold(thresholds):
    list(thresholds)
    end = bytearray([0xff, 0xff, 0xff])
    myuart.uart.write("h0.val=%d" % thresholds[0])
    myuart.uart.write(end)
    myuart.uart.write("h1.val=%d" % thresholds[1])
    myuart.uart.write(end)
    myuart.uart.write("h2.val=%d" % (thresholds[2] + 128))
    myuart.uart.write(end)
    myuart.uart.write("h3.val=%d" % (thresholds[3] + 128))
    myuart.uart.write(end)
    myuart.uart.write("h4.val=%d" % (thresholds[4] + 128))
    myuart.uart.write(end)
    myuart.uart.write("h5.val=%d" % (thresholds[5] + 128))
    myuart.uart.write(end)


def change_threshold():
    global key0
    try:
        thresholds = [0, 0, 0, 0, 0, 0]
        for i in range(1, 3):
            thresholds[i - 1] = key0[i]
        for i in range(4, 11, 2):
            thresholds[i // 2] = key0[i]
            if key0[i - 1] == CHECK_Negative:
                thresholds[i // 2] -= 128
    except Exception as e:
        pass

    return tuple(thresholds)


def receive_threshold(f):
    i = 0
    thresholds = [0]*6
    line = f.readline().strip().strip('[]').split(',')
    for n in line:
        thresholds[i] = int(n)
        i += 1
    return tuple(thresholds)


def Threshold_Debugger():
    global key0

    sensor.set_windowing((96, 40, 130, 128))
    lcd.init()

    while True:
        img = sensor.snapshot()
        key = 0
        key0 = []
        try:
            pixformat = len(img.get_pixel(0, 0))
        except Exception as e:
            pixformat = 2   # 灰度返回的是像素值，不是列表
        if pixformat == 3:
            img.binary([globalvar.red_threshold])
        elif pixformat == 2:
            img.binary([globalvar.ctr.thresholds])

        lcd.display(img)
        if myuart.uart.any():
            i = 0
            buf_size = myuart.uart.any()
            while i < buf_size:
                key = myuart.uart.readchar()
                key0.append(key)
                i += 1
            if key0[0] == 0xaa and key0[-1] == 0xbb:
                key0.pop()
                key0.pop(0)
                key = key0[0]
                print(key)
            else:
                key = 0


        if key == CHECK_Send:  # 发送阈值
            LED(1).off()
            LED(2).on()
            if pixformat == 3:
                send_threshold(globalvar.red_threshold)
            LED(2).off()

        elif key == CHECK_Change_Thresh:  # 更改阈值
            LED(1).off()
            LED(3).on()
            if pixformat == 3:
                globalvar.red_threshold = change_threshold()
            LED(3).off()

        elif key == CHECK_Remove_Files1:  # 删除文件1
            LED(2).on()
            os.remove("color1.txt")
            LED(2).off()

        elif key == CHECK_Write_To_File1:  # 写入文件1
            LED(3).on()
            try:
                with open("color1.txt", "x") as f:
                    if pixformat == 3:
                        f.write(json.dumps(globalvar.red_threshold))
                        f.write('\n')
            except OSError:
                os.remove("color1.txt")
                with open("color1.txt", "x") as f:
                    if pixformat == 3:
                        f.write(json.dumps(globalvar.red_threshold))
                        f.write('\n')
            LED(3).off()

        elif key == CHECK_Read_From_Files1:  # 从文件1读取阈值
            LED(2).on()
            try:
                with open("color1.txt", "r") as f:
                    if pixformat == 3:
                        globalvar.red_threshold = receive_threshold(f)
                print(globalvar.red_threshold)
            except Exception as e:
                print(e)
                pass

            LED(2).off()
