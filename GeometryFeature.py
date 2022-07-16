import image
import globalvar

imgWidth = 320
imgHeight = 240
roiLen = 30  # 扫描区域宽度

ROIS = {
    'down': (0, imgHeight - roiLen - 1, imgWidth, roiLen),  # 横向取样_下方 1
    'middle': (0, int(imgHeight / 2) - roiLen, imgWidth, roiLen),  # 横向取样_中间 2
    'up': (0, 0, imgWidth, roiLen),  # 横向取样_上方 3
    'left': (0, 0, roiLen, imgHeight),  # 纵向取样_左侧 4
    'right': (imgWidth - roiLen - 1, 0, roiLen, imgHeight)  # 纵向取样_右侧 5
}


# 将原来由两点坐标确定的直线，转换为 y=ax+b 的格式
def trans_line_format(line):
    x1 = line.x1()
    y1 = line.y1()
    x2 = line.x2()
    y2 = line.y2()

    if x1 == x2:  # 避免完全垂直，x坐标相等的情况
        x1 += 0.1
    a = (y2 - y1) / (x2 - x1)  # 计算斜率 a
    # y = a*x + b -> b = y - a*x
    b = y1 - a * x1  # 计算常数项 b
    return a, b


# 利用四边形的角公式， 计算出直线夹角
def calculate_angle(line1, line2):
    angle = (180 - abs(line1.theta() - line2.theta()))
    if angle > 90:
        angle = 180 - angle
    return angle


# 寻找相互垂直的两条线
def find_verticle_lines(lines, angle_threshold=(70, 90)):
    return find_interserct_lines(lines, angle_threshold=angle_threshold)


# 根据夹角阈值寻找两个相互交叉的直线，且交点需要存在于画面中
def find_interserct_lines(lines, angle_threshold=(10, 90), window_size=None):
    line_num = len(lines)
    for i in range(line_num - 1):
        for j in range(i + 1, line_num):
            # 判断两个直线之间的夹角是否为直角
            angle = calculate_angle(lines[i], lines[j])
            # 判断角度是否在阈值范围内
            if not (angle_threshold[0] <= angle <= angle_threshold[1]):
                continue

            # 判断交点是否在画面内
            if window_size is not None:
                # 获取串口的尺寸 宽度跟高度
                win_width, win_height = window_size
                # 获取直线交点
                intersect_pt = calculate_intersection(lines[i], lines[j])
                if intersect_pt is None:  # 没有交点
                    continue
                x, y = intersect_pt
                if not (0 <= x < win_width and 0 <= y < win_height):  # 交点没有在画面中
                    continue
            return lines[i], lines[j]
    return None


# 计算两条线的交点
def calculate_intersection(line1, line2):
    a1 = line1.y2() - line1.y1()
    b1 = line1.x1() - line1.x2()
    c1 = line1.x2() * line1.y1() - line1.x1() * line1.y2()

    a2 = line2.y2() - line2.y1()
    b2 = line2.x1() - line2.x2()
    c2 = line2.x2() * line2.y1() - line2.x1() * line2.y2()

    if (a1 * b2 - a2 * b1) != 0 and (a2 * b1 - a1 * b2) != 0:
        cross_x = int((b1 * c2 - b2 * c1) / (a1 * b2 - a2 * b1))
        cross_y = int((c1 * a2 - c2 * a1) / (a1 * b2 - a2 * b1))
        return cross_x, cross_y
    return None


def find_blobs_in_rois(img, line_color, is_debug=True):
    globalvar.FLAG_VerLine = 0
    globalvar.FLAG_AcrLine = 0

    roi_blobs_result = {}  # 在各个ROI中寻找色块的结果记录
    for roi_direct in ROIS.keys():
        roi_blobs_result[roi_direct] = {
            'cx': -1,
            'cy': -1,
            'blob_flag': False
        }
    for roi_direct, roi in ROIS.items():
        blobs = img.find_blobs([line_color], roi=roi, merge=True, pixels_area=10)
        if len(blobs) == 0:
            continue

        largest_blob = max(blobs, key=lambda b: b.pixels())
        x, y, width, height = largest_blob[:4]

        # 根据色块的宽度进行过滤
        if not (25 <= width <= 75 and 18 <= height <= 56):
            continue

        roi_blobs_result[roi_direct]['cx'] = x
        roi_blobs_result[roi_direct]['cy'] = y
        roi_blobs_result[roi_direct]['blob_flag'] = True

        if is_debug:
            img.draw_rectangle(x, y, width, height)

    if roi_blobs_result[0]['blob_flag'] and roi_blobs_result[1]['blob_flag'] and roi_blobs_result[2]['blob_flag']:
        globalvar.FLAG_VerLine = 1
    if roi_blobs_result[3]['blob_flag'] and roi_blobs_result[4]['blob_flag']:
        globalvar.FLAG_AcrLine = 1

    return roi_blobs_result


last_cx = 0
last_cy = 0


def check_geometry(img, lines, line_color, show=False):
    global last_cx, last_cy

    intersect_pt = find_interserct_lines(lines, angle_threshold=(45, 90), window_size=(imgWidth, imgHeight))
    # 直线与直线之间的夹角不满足阈值范围
    if intersect_pt is None:
        intersect_x = 0
        intersect_y = 0
    else:
        intersect_x, intersect_y = intersect_pt

    result = find_blobs_in_rois(img, line_color, is_debug=True)

    globalvar.geometry_type = globalvar.NONE
    if (not result['up']['blob_flag']) and result['down']['blob_flag']:
        if result['left']['blob_flag'] and (not result['right']['blob_flag']):
            globalvar.geometry_type = globalvar.IS_Left
        elif result['right']['blob_flag'] and (not result['left']['blob_flag']):
            globalvar.geometry_type = globalvar.IS_Right

    if globalvar.geometry_type == globalvar.NONE:
        cnt = 0
        for roi_direct in ['up', 'down', 'left', 'right']:
            if result[roi_direct]['blob_flag']:
                cnt += 1
        if cnt == 3:
            globalvar.geometry_type = globalvar.IS_T
        elif cnt == 4:
            globalvar.geometry_type = globalvar.IS_Cross

    cx = 0
    cy = 0
    if globalvar.geometry_type == globalvar.IS_T or globalvar.geometry_type == globalvar.IS_Cross:
        cnt = 0
        for roi_direct in ['up', 'down']:
            if result[roi_direct]['blob_flag']:
                cnt += 1
                cx += result[roi_direct]['cx']
        if cnt == 0:
            cx = last_cx
        else:
            cx /= cnt

        cnt = 0
        for roi_direct in ['left', 'right']:
            if result[roi_direct]['blob_flag']:
                cnt += 1
                cy += result[roi_direct]['cy']
        if cnt == 0:
            cy = last_cy
        else:
            cy /= cnt

    if show:
        visualize_result(img, lines, globalvar.geometry_type)

    last_cx = cx
    last_cy = cy


# 可视化结果
def visualize_result(img, lines, geometry_type):
    for l in lines:
        img.draw_line(l.line(), color=(255, 255, 0), thickness=5)

    if globalvar.geometry_type == globalvar.NONE:
        print('不是特殊性状')
    elif globalvar.geometry_type == globalvar.IS_Left:
        print('左直角')
    elif globalvar.geometry_type == globalvar.IS_Right:
        print('右直角')
    elif globalvar.geometry_type == globalvar.IS_T:
        print('T字形')
    elif globalvar.geometry_type == globalvar.IS_Cross:
        print('十字形')


verticle_pixels_threshold = [200, 300]   #像素最大和最小阈值
track_line_threshold = [100, 200]


def count_pixels_with_movement(img):
    global x_width, y_height

    x_pos = 0
    y_pos = 0
    total_white_pixels = 0
    for x_pos in range(x_width):
        for y_pos in range(y_height):
            if img.get_pixel(x_pos, y_pos) == 255:
                total_white_pixels += 1  # 利用get_pixel()方法，计算当前图像中白色色块所占的像素大小

    print("total white pixels are", total_white_pixels)
    if total_white_pixels >= verticle_pixels_threshold[0] and total_white_pixels <= verticle_pixels_threshold[1]:
        globalvar.geometry_type = globalvar.IS_Cross
    elif total_white_pixels >= track_line_threshold[0] and total_white_pixels <= track_line_threshold[1]:
        globalvar.geometry_type = globalvar.IS_T
    else:
        globalvar.geometry_type = globalvar.NONE

