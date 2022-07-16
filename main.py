import image, sensor, time
from pyb import LED

import myblob
import myLine
import myuart
import globalvar
import GeometryFeature

sensor.reset()
sensor.set_framesize(sensor.QVGA)  # 320*240
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking

clock = time.clock()

led1 = LED(1)
led2 = LED(2)
led3 = LED(3)
led1.off()
led2.off()
led3.off()

while True:
    clock.tick()
    myuart.uart_read_buf()
    globalvar.fps_cnt += 1
    uart_send = 0

    img = sensor.snapshot()

    if globalvar.ctr.isGrayscale:
        # 计算最优灰度阈值（如果希望使用自定义阈值，请把该函数注释掉）
        globalvar.ctr.thresholds[1] = int(img.get_statistics().mean() * 0.4)

    # 线检测
    if globalvar.ctr.work_mode == globalvar.CHECK_VerLine or globalvar.ctr.work_mode == globalvar.CHECK_AcrLine:
        line = myLine.check_dotLine(img, thresholds=globalvar.ctr.thresholds, show=globalvar.ctr.check_show)
        uart_send = 1
        # uart.wrte(pack_line_data(line))  # 发送数据

    if uart_send == 0:
        myuart.send_online(globalvar.CHECK_Online)