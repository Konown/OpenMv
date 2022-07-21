import binascii
import sensor, image, time, math, pyb, json, lcd
from pyb import UART
from pyb import LED

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_windowing((50, 70, 130, 140))
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
lcd.init()

uart = UART(3, 115200)
uart.init(115200, bits=8, parity=None, stop=1)  # 八数据位，无校验位，1停止位

clock = time.clock()

threshold_red = (5, 91, 17, 124, -30, 70)
key0 = [0] * 11


def send_threshold(thresholds):
    list(thresholds)
    end = bytearray([0xff, 0xff, 0xff])
    uart.write("h0.val=%d" % thresholds[0])
    uart.write(end)
    uart.write("h1.val=%d" % thresholds[1])
    uart.write(end)
    uart.write("h2.val=%d" % (thresholds[2] + 127))
    uart.write(end)
    uart.write("h3.val=%d" % (thresholds[3] + 127))
    uart.write(end)
    uart.write("h4.val=%d" % (thresholds[4] + 127))
    uart.write(end)
    uart.write("h5.val=%d" % (thresholds[5] + 127))
    uart.write(end)


def change_threshold():
    thresholds = [0, 0, 0, 0, 0, 0]
    for i in range(1, 3):
        string = key0[i]
        string_thresholds = string.encode('utf-8')
        thresholds[i - 1] = int(binascii.hexlify(string_thresholds), 16)
    for i in range(4, 11, 2):
        string = key0[i]
        string_thresholds = string.encode('utf-8')
        thresholds[i // 2] = int(binascii.hexlify(string_thresholds), 16)
        if key0[i - 1] == '0':
            thresholds[i // 2] -= 127

    return tuple(thresholds)


def receive_threshold():
    i = 0
    thresholds = [0]*6
    line = f.readline().strip().strip('[]').split(',')
    for n in line:
        thresholds[i] = int(n)
        i += 1
    return tuple(thresholds)


while True:
    clock.tick()

    key = 0

    img = sensor.snapshot()
    lcd.display(img)

    if uart.any():
        key = uart.read().decode().strip()

    if key == '!':
        while True:
            LED(1).on()
            key = 0

            img = sensor.snapshot()
            img.binary([threshold_red])
            lcd.display(img)

            if uart.any():
                key0 = uart.readline().decode().strip()
                key = key0[0]

            if key == '"':  # 发送阈值
                LED(1).off()
                LED(2).on()
                send_threshold(threshold_red)
                LED(2).off()

            elif key == '1':  # 更改阈值
                LED(1).off()
                LED(3).on()
                threshold_red = change_threshold()
                LED(3).off()

            elif key == '$':  # 删除文件1
                import os

                LED(2).on()
                os.remove("color1.txt")
                LED(2).off()

            elif key == '#':  # 计入文件1
                import os

                LED(3).on()
                try:
                    with open("color1.txt", "x") as f:
                        f.write(json.dumps(threshold_red))
                        f.write('\n')
                except OSError:
                    os.remove("color1.txt")
                    with open("color1.txt", "x") as f:
                        f.write(json.dumps(threshold_red))
                        f.write('\n')
                LED(3).off()

            elif key == '%':  # 从文件1读取阈值
                LED(1).off()
                LED(2).on()
                with open("color1.txt", "r") as f:
                    threshold_red = receive_threshold()
                print(threshold_red)
                LED(2).off()
