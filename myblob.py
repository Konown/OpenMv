import image
import globalvar

# 获取平均数
def Get_Average(list):
    sum = 0

    if len(list) == 0:
        return 0
    for item in list:
        sum += item
    return int(sum / len(list))


# 获取最大可能色块函数
def get_maxsize_color(srcImg):
    R_MAXpixels = 0
    G_MAXpixels = 0
    B_MAXpixels = 0

    # 寻找red最大连通域
    for blob in srcImg.find_blobs([globalvar.red_threshold], pixels_threshold=10, area_threshold=20, merge=True, margin=0):
        pixels = blob.pixels()  # 获取像素个数，用来判断大小
        R_MAXpixels = max(pixels, R_MAXpixels)
    # 寻找green最大连通域
    for blob in srcImg.find_blobs([globalvar.green_threshold], pixels_threshold=10, area_threshold=20, merge=True, margin=0):
        pixels = blob.pixels()  # 获取像素个数，用来判断大小
        G_MAXpixels = max(pixels, G_MAXpixels)
    # 寻找blue最大连通域
    for blob in srcImg.find_blobs([globalvar.blue_threshold], pixels_threshold=10, area_threshold=20, merge=True, margin=0):
        pixels = blob.pixels()  # 获取像素个数，用来判断大小
        B_MAXpixels = max(pixels, B_MAXpixels)
    maxpixels = max(R_MAXpixels, G_MAXpixels, B_MAXpixels)
    if R_MAXpixels == maxpixels:
        return globalvar.red_threshold
    elif G_MAXpixels == maxpixels:
        return globalvar.green_threshold
    else:
        return globalvar.blue_threshold


def My_find_blobs(img, threshold, Limit_area, Limit_pixels, isBinary=False, show=False):

    if isBinary:
        img.binary([threshold], invert=True, zero=True)
        img.erode(1)
        img.dilate(2)
        img.mean(1)
        blobs = img.find_blobs([(90, 100)], area_threshold=Limit_area, pixels_threshold=Limit_pixels,
                               merge=False)
    else:
        img.mean(1)
        blobs = img.find_blobs([threshold], area_threshold=Limit_area, pixels_threshold=Limit_pixels,
                               merge=False)

    if blobs:
        largest_blob = max(blobs, key=lambda b: b.pixels())
        center_x = largest_blob[5]
        center_y = largest_blob[6]
        print("pixels", largest_blob.pixels())
        print("area", largest_blob.area())
        if show:
            img.draw_cross(center_x, center_y, thickness=3, color=(0, 0, 0))
            #img.draw_rectangle(largest_blob.rect(), thickness=3)
        return largest_blob


def Detect_Focal_length(img, threshold):
    blobs = img.find_blobs([threshold], area_threshold=100, pixels_threshold=200, merge=True)
    if blobs:
        largest_blob = max(blobs, key=lambda b: b.pixels())
        if True:
            img.draw_rectangle(largest_blob.rect(), thickness=3, color=(0, 0, 0))
            print(largest_blob.w())
        return largest_blob

