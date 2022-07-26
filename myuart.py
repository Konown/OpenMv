import sensor
from pyb import UART
import globalvar

SEND_Start1 = 0xAA
SEND_Start2 = 0xBB

uart = UART(3, 115200)
uart.init(115200, bits=8, parity=None, stop=1)  # 八数据位，无校验位，1停止位


# 不进位和校验
def check_sum(data, lens):
    check = 0
    i = 0

    while i <= lens - 1:
        check = check + data[i]
        i = i + 1
    check = check % 256
    data.append(check)


# ACK应答
def send_ack(mode):
    buf_data = [SEND_Start1, SEND_Start2, mode, 0x00, globalvar.ctr.work_mode]
    buf_data[3] = len(buf_data) - 4
    check_sum(buf_data, len(buf_data))
    pack_data = bytearray(buf_data)
    uart.write(pack_data)


# 在线检测
def send_online(mode):
    buf_data = [SEND_Start1, SEND_Start2, mode, 0x00]
    buf_data[3] = len(buf_data) - 4
    check_sum(buf_data, len(buf_data))
    pack_data = bytearray(buf_data)
    uart.write(pack_data)


# 竖线检测
def send_line_vertical(mode, angle, x):
    buf_data = [SEND_Start1, SEND_Start2, mode, 0x00, angle, x // 256, x % 256]
    buf_data[3] = len(buf_data) - 4
    check_sum(buf_data, len(buf_data))
    pack_data = bytearray(buf_data)
    uart.write(pack_data)


# 横线检测
def send_line_across(mode, angle, y):
    buf_data = [SEND_Start1, SEND_Start2, mode, 0x00, angle, y]
    buf_data[3] = len(buf_data) - 4
    check_sum(buf_data, len(buf_data))
    pack_data = bytearray(buf_data)
    uart.write(pack_data)


# 圆形检测
def send_circle(mode, x, y):
    buf_data = [SEND_Start1, SEND_Start2, mode, 0x00, x // 256, x % 256, y]
    buf_data[3] = len(buf_data) - 4
    check_sum(buf_data, len(buf_data))
    pack_data = bytearray(buf_data)
    uart.write(pack_data)


# 色块检测
def send_blob(mode, x, y):
    buf_data = [SEND_Start1, SEND_Start2, mode, 0x00, x // 256, x % 256, y]
    buf_data[3] = len(buf_data) - 4
    check_sum(buf_data, len(buf_data))
    pack_data = bytearray(buf_data)
    uart.write(pack_data)


class Receive(object):
    uart_buf = []
    data_len = 0
    data_cnt = 0
    state = 0


R = Receive()


# 数据类型转换
def int8(byte):
    if byte > 127:
        return byte - 256
    else:
        return byte


# 阈值读取处理
def receive_threshold(f):
    i = 0
    thresholds = [0]*6
    line = f.readline().strip().strip('[]').split(',')
    for n in line:
        thresholds[i] = int(n)
        i += 1
    return tuple(thresholds)


# 串口通信协议处理
def Receive_Analysis(data_buf, lens):
    # 不进位和校验
    sum = 0
    i = 0
    while i <= lens - 2:
        sum = sum + data_buf[i]
        i += 1
    sum = sum % 256
    if sum != data_buf[lens - 1]:
        return

    # 设置色彩模式
    if data_buf[2] == globalvar.Receive_mode_Setpixformat:
        if data_buf[4] == globalvar.Pix_RGB:
            sensor.reset()
            sensor.set_framesize(sensor.QVGA)  # 320*240
            sensor.set_pixformat(sensor.RGB565)
            sensor.skip_frames(time=2000)
            sensor.set_auto_gain(False)  # must be turned off for color tracking
            sensor.set_auto_whitebal(False)  # must be turned off for color tracking
        elif data_buf[4] == globalvar.Pix_Gray:
            sensor.reset()
            sensor.set_framesize(sensor.QVGA)  # 320*240
            sensor.set_pixformat(sensor.GRAYSCALE)
            sensor.skip_frames(time=2000)
            sensor.set_auto_gain(False)  # must be turned off for color tracking
            sensor.set_auto_whitebal(False)  # must be turned off for

    # 设置曝光度
    elif data_buf[2] == globalvar.Receive_mode_Exposure:
        globalvar.ctr.work_mode = globalvar.Receive_mode_Exposure
        if data_buf[4] == 0x01:
            sensor.set_auto_exposure(True)

    # 设置追踪颜色
    elif data_buf[2] == globalvar.Receive_mode_SetColor:
        # 设置为寻找红色
        if data_buf[4] == 0x01:
            globalvar.ctr.work_mode = globalvar.Color_Red
        # 设置为寻找绿色
        elif data_buf[4] == 0x02:
            globalvar.ctr.work_mode = globalvar.Color_Green

    # 进入阈值调试模式
    elif data_buf[2] == globalvar.Receive_Thresh_Debugger:
        globalvar.flag_thresh_debugger = 1

    elif data_buf[2] == globalvar.Receive_Set_RGB_Thresh:
        try:
            if data_buf[4] == 0x01: # 红色阈值
                with open("color1.txt", "r") as f:
                    globalvar.red_threshold = receive_threshold(f)
                print(globalvar.red_threshold)
        except Exception as e:
            print(e)
            pass

    globalvar.ctr.work_mode = data_buf[2]
    send_ack(globalvar.CHECK_ACK)


# 串口通信协议接收
def Receive_Prepare(data):
    print(data)
    if R.state == 0 and data == SEND_Start1:
        R.state = 1
        R.uart_buf.append(data)
    elif R.state == 1 and data == SEND_Start2:
        R.state = 2
        R.uart_buf.append(data)
    elif R.state == 2:  # 功能帧
        R.state = 3
        R.uart_buf.append(data)
    elif R.state == 3:  # 有效数据长度
        R.uart_buf.append(data)
        R.data_len = data
        if 0 < R.data_len <= 0x14:
            R.state = 4
        elif R.data_len == 0:
            R.state = 5
        else:
            R.state = 0
            R.uart_buf = []
    elif R.state == 4:
        if R.data_len > 0:
            R.data_len -= 1
            R.uart_buf.append(data)
            if R.data_len == 0:
                R.state = 5
    elif R.state == 5:
        R.state = 0
        R.uart_buf.append(data)
        Receive_Analysis(R.uart_buf, len(R.uart_buf))
        R.uart_buf = []
    else:
        R.state = 0
        R.uart_buf = []


# 读取串口缓存
def uart_read_buf():
    i = 0
    buf_size = uart.any()
    while i < buf_size:
        Receive_Prepare(uart.readchar())
        i += 1

