CHECK_ACK = 0xFF
CHECK_Online = 0x00

CHECK_VerLine = 0x01
CHECK_AcrLine = 0x02
CHECK_Circle = 0x03
CHECK_Blob = 0x04

# 直线特征判断
NONE = 0xc0  # 192
IS_Left = 0xc1  # 193
IS_Right = 0xc2  # 194
IS_T = 0xc3  # 195
IS_Cross = 0xc4  # 196
geometry_type = NONE

# 接收宏定义
Receive_mode_Setpixformat = 0xd0
Pix_RGB = 0x01
Pix_Gray = 0x02

Receive_mode_Exposure = 0xd1

Receive_mode_SetColor = 0xd2
Color_Red = 0x01
Color_Green = 0x02

Receive_Thresh_Debugger = 0xd3
flag_thresh_debugger = 0

Receive_Set_RGB_Thresh = 0xd4
Receive_Set_GRAY_Thresh = 0xd5

fps_cnt = 0
fps_cnt_set = 10000
show_fps_set = 15


class Ctrl(object):
    work_mode = 0x03  # 工作模式
    check_show = 0  # 开显示，在线调试时可以打开，脱机使用请关闭，可提高计算速度
    isGrayscale = False  # True 灰度模式
    thresholds = (0, 90)  # 默认追踪黑色


ctr = Ctrl()

green_threshold = (5, 88, -73, -18, 9, 59)  # (57,95,-80,-20,-25,32)
red_threshold = (5, 91, 17, 124, -30, 70)  # (21,71,56,124,38,114)
blue_threshold = (5, 70, -54, 105, -80, -14)  # (20,73,-46,112,-128,-31)

LINE_BLACK = (0, 90)  # 灰度图，黑线
LINE_WHITE = (128, 255)  # 灰度图，白线

FLAG_VerLine = 0
FLAG_AcrLine = 0
