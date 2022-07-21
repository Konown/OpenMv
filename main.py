import image, sensor, time
import usocket, network
from pyb import LED

import myblob
import myLine
import myuart
import globalvar
import GeometryFeature

SSID ='OPENMV1'    # Network SSID
KEY  ='1234567890'    # Network key (must be 10 chars)
HOST = ''           # Use first available interface
PORT = 8080         # Arbitrary non-privileged port

sensor.reset()
sensor.set_framesize(sensor.QVGA)  # 320*240
sensor.set_pixformat(sensor.RGB565)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking

wlan = network.WINC(mode=network.WINC.MODE_AP)
wlan.start_ap(SSID, key=KEY, security=wlan.WEP, channel=2)

clock = time.clock()

led1 = LED(1)
led2 = LED(2)
led3 = LED(3)
led1.off()
led2.off()
led3.off()


def start_streaming(s):
    print ('Waiting for connections..')
    client, addr = s.accept()
    # set client socket timeout to 2s
    client.settimeout(2.0)
    # Read request from client
    data = client.recv(1024)
    # Should parse client request here

    # Send multipart header
    client.send("HTTP/1.1 200 OK\r\n" \
                "Server: OpenMV\r\n" \
                "Content-Type: multipart/x-mixed-replace;boundary=openmv\r\n" \
                "Cache-Control: no-cache\r\n" \
                "Pragma: no-cache\r\n\r\n")
    sensor.reset()
    sensor.set_framesize(sensor.QVGA)  # 320*240
    sensor.set_pixformat(sensor.RGB565)
    sensor.skip_frames(time = 2000)
    sensor.set_auto_gain(False) # must be turned off for color tracking
    sensor.set_auto_whitebal(False) # must be turned off for color tracking

    while True:
        clock.tick()
        myuart.uart_read_buf()
        globalvar.fps_cnt += 1
        uart_send = 0
        blobs_R = 0
        blobs_G = 0

        img = sensor.snapshot()
        if globalvar.ctr.work_mode & globalvar.Color_Red == globalvar.Color_Red:
            blobs_R = myblob.My_find_blobs(img, globalvar.red_threshold, 500, 500, isBinary=False, show=False)
            GeometryFeature.find_blobs_in_rois(img, globalvar.red_threshold, is_debug=False)
            if blobs_R and globalvar.FLAG_VerLine:
                uart_send = 1
                myuart.send_blob(globalvar.CHECK_Blob, blobs_R.cx(), blobs_R.cy())

        img = sensor.snapshot()
        if globalvar.ctr.work_mode & globalvar.Color_Green == globalvar.Color_Green:
            blobs_G = myblob.My_find_blobs(img, globalvar.green_threshold, 500, 500, isBinary=False, show=False)
            GeometryFeature.find_blobs_in_rois(img, globalvar.green_threshold, is_debug=False)
            if blobs_G and globalvar.FLAG_VerLine:
                uart_send = 1
                myuart.send_circle(globalvar.CHECK_Circle, blobs_G.cx(), blobs_G.cy())

        if blobs_R:
            img.draw_cross(blobs_R.cx(), blobs_R.cy(), thickness=3, color=(0, 255, 0))
        if blobs_G:
            img.draw_cross(blobs_G.cx(), blobs_G.cy(), thickness=3, color=(255, 0, 0))

        if uart_send == 0:
            myuart.send_online(globalvar.CHECK_Online)


        cframe = img.compressed(quality=35)
        header = "\r\n--openmv\r\n" \
                 "Content-Type: image/jpeg\r\n"\
                 "Content-Length:"+str(cframe.size())+"\r\n\r\n"
        client.send(header)
        client.send(cframe)


dt = 0
while True:
    # Create server socket
    s = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
    try:
        # Bind and listen
        s.bind([HOST, PORT])
        s.listen(5)

        # Set server socket timeout
        # NOTE: Due to a WINC FW bug, the server socket must be closed and reopened if
        # the client disconnects. Use a timeout here to close and re-create the socket.
        s.settimeout(3)
        start_streaming(s)
    except OSError as e:
        dt=dt+1
        s.close()
        print("socket error: ", e)
        #sys.print_exception(e)
    if dt>=10:
        break

sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)   # Set frame size to QVGA (320x240)
sensor.skip_frames(time = 2000)     # Wait for settings take effect.
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
while True:
    clock.tick()
    myuart.uart_read_buf()
    globalvar.fps_cnt += 1
    uart_send = 0
    blobs_R = 0
    blobs_G = 0

    img = sensor.snapshot()
    if globalvar.ctr.work_mode & globalvar.Color_Red == globalvar.Color_Red:
        blobs_R = myblob.My_find_blobs(img, globalvar.red_threshold, 500, 500, isBinary=False, show=False)
        GeometryFeature.find_blobs_in_rois(img, globalvar.red_threshold, is_debug=False)
        if blobs_R and globalvar.FLAG_VerLine:
            uart_send = 1
            myuart.send_blob(globalvar.CHECK_Blob, blobs_R.cx(), blobs_R.cy())

    img = sensor.snapshot()
    if globalvar.ctr.work_mode & globalvar.Color_Green == globalvar.Color_Green:
        blobs_G = myblob.My_find_blobs(img, globalvar.green_threshold, 500, 500, isBinary=False, show=False)
        GeometryFeature.find_blobs_in_rois(img, globalvar.green_threshold, is_debug=False)
        if blobs_G and globalvar.FLAG_VerLine:
            uart_send = 1
            myuart.send_circle(globalvar.CHECK_Circle, blobs_G.cx(), blobs_G.cy())

    if blobs_R:
        img.draw_cross(blobs_R.cx(), blobs_R.cy(), thickness=3, color=(0, 255, 0))
    if blobs_G:
        img.draw_cross(blobs_G.cx(), blobs_G.cy(), thickness=3, color=(255, 0, 0))

    if uart_send == 0:
        myuart.send_online(globalvar.CHECK_Online)

