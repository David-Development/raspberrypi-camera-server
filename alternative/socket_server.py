import picamera
import threading
import socket
import select
from threading import Thread
import sys
import time
from datetime import datetime, timedelta
import multiprocessing
import queue
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from wifi_monitor import ConnectionMonitor
from iwconfig import iwconfig

#from gpiozero import CPUTemperature
import os
import io
import psutil

running = True

'''
The RaspberryStreamingServer accepts websocket connections on which it'll return the video stream on.
Once the connection is established, a "file" like object will be created into which the picamera can output it's camera stream.
This "file" like object is actually a representation of the websocket stream.
Therefore the data will be send via the websocket stream.

This example was heavily inspired by https://github.com/waveform80/pistreaming where single mjpeg frames were streamed via websockets to the browser where the were decoded and displayed. However for a h264 video stream the decoding is not trivial and requires a lot of work.
'''


CAMERA_MODE = 0
FRAMERATE = 25

WS_INFO_PORT = 8082
WS_PORT = 8084
ROTATION = 0
HOST = "0.0.0.0"
print("Host: ", HOST, " Port: ", WS_INFO_PORT)

def getCpuLoad():
    return psutil.cpu_percent()

def getRamUsagePercent():
    ram = psutil.virtual_memory()
    return  ram.percent

def getCpuTemperature():
    with io.open("/sys/class/thermal/thermal_zone0/temp", 'r') as f:
        return float(f.readline().strip()) / 1000

def getGpuTemperature():
    ret = os.popen('vcgencmd measure_temp').readline();
    temperature = ret.replace("temp=","").replace("'C\n","");
    return(float(temperature))


class SimpleEcho(WebSocket):

    #def __init__(self, *args, **kwargs):
    #    print("Calling init here!!")
    #    super(SimpleEcho, self).__init__(*args, **kwargs)

    def handleMessage(self):
        # echo message back to client
        #self.sendMessage(self.data)
        print("Message received: ", self.data)

    def handleConnected(self):
        print(self.address, 'connected')
        try:
            self.rss = RaspberryStreamingServer()
            rssThread = Thread(target=self.rss.start)
            rssThread.start()
        except Exception as e:
            print(e)
        clients.append(self)

    def handleClose(self):
        print(self.address, 'closed')
        self.rss.stop()
        clients.remove(self)

class RaspberryStreamingServer(object):
    stopFlag = False
    def start(self):
        print("Started Socket!!")
        self.server_socket = socket.socket()
        self.server_socket.bind((HOST, WS_PORT))
        print("Bind Host: ", HOST, " PORT: ", WS_PORT)
        self.server_socket.listen(0)

        conn, addr = self.server_socket.accept()
        # conn - socket to client
        # addr - clients address

        print("Accepted connection!")
        print("Parse websocket header")

        data = conn.recv(1024) #receive data from client
        header = bytes.decode(data) #decode it to header
        header_params = [s.strip() for s in header.splitlines()]
        #print("Header Params: ", header_params)

        # Default Resolutio
        WIDTH = 320
        HEIGHT = 240
        # Parse resolution from header
        for item in header_params:
            if item.startswith('Camera-Width:'):
                WIDTH = int(item[14:])
            elif item.startswith('Camera-Height:'):
                HEIGHT = int(item[15:])

        print("Requested Camera Format: Width=", WIDTH, " - Height=", HEIGHT)

        # Accept a single connection and make a file-like object out of it
        self.connection = conn.makefile('wb', buffering=0)
        print("Accepted camera connection!")
        self.connection.write(bytes('''
            HTTP/1.1 101 Web Socket Protocol Handshake\r
            Upgrade: WebSocket\r
            Connection: Upgrade\r
            WebSocket-Origin: http://localhost:8888\r
            WebSocket-Location: ws://localhost:9876/\r
            WebSocket-Protocol: sample
        '''.strip() + '\r\n\r\n', 'UTF-8'))
        self.connection.flush()

        with picamera.PiCamera(sensor_mode=CAMERA_MODE) as camera:
        #with picamera.PiCamera() as camera:
            camera.resolution = (WIDTH, HEIGHT)
            camera.framerate = FRAMERATE
            camera.rotation = ROTATION
            camera.vflip = 0
            camera.hflip = 0

            # Wait to let the auto-exposure figure out good settings
            time.sleep(1)

            #camera.sharpness = 0
            #camera.contrast = -10
            #camera.saturation = 0
            #camera.video_stabilization = False
            #camera.exposure_compensation = 0
            #camera.exposure_mode = 'off'
            #time.sleep(1)
            #camera.awb_mode = 'off'
            #camera.awb_gains = (1.45, 1.45)


            #camera.start_recording(connection, format='h264', resize=(640, 480))
            camera.start_recording(self.connection, format='h264')
            #camera.start_recording(self.connection, format='h264', quality=22, bitrate=2000000) # 2Mbps of bitrate

            while not self.stopFlag:
                try:
                    time.sleep(1)
                    #print("Frame: ", camera.frame)
                    #print("ISO: ", camera.iso)
                    #print("Resolution: ", camera.resolution)
                    #print("Sensor Mode: ", camera.sensor_mode)
                    #print("ShutterSpeed: ", camera.shutter_speed)
                    #print("ExposureSpeed: ", camera.exposure_speed)
                    #print("ExposureMode: ", camera.exposure_mode)
                except KeyboardInterrupt:
                    print("KeyboardInterrupted")
                    print("Stopping server.")
                    self.stopFlag = True

            print("Starting cleanup!")
            try:
                 camera.stop_recording()
            except BrokenPipeError as e:
                 print("BrokenPipeError")
            except ConnectionResetError as cre:
                 print("ConnectionResetError")
            self.connection.close()
            self.server_socket.close()
            print("Cleanup complete!")

    def stop(self):
        self.stopFlag = True
        print("Stop requested!")






# Info Websocket variables
clients = []
cm = ConnectionMonitor("wlan0")
iwconf = iwconfig()

def sendInfo():
    #print("Sending Info..")
    cm.update()
    text =  "CPU: " + "%.1f" % getCpuTemperature() + "°C" + "\n"
    text += "GPU: " + "%.1f" % getGpuTemperature() + "°C" + "\n"
    text += "CPU: " + "%.1f" % getCpuLoad() + "%" + "\n"
    text += "RAM: " + "%.1f" % getRamUsagePercent() + "%" + "\n"
    #text += "_____________ \n"
    #text += "Read kb/s: "  + "%.1f" % (cm.readBps / 1000) + "\n"
    #text += "Packets: "   + str(cm.readPackets)   + "\n"
    #text += "_____________ \n"
    #text += "Write kb/s: " + "%.1f" % (cm.writeBps / 1000) + "\n"
    #text += "Packets: "   + str(cm.writePackets) + "\n"
    text += iwconf.getIwconfig()

    #self.cm.output()
    #print(text)
    for client in clients:
        client.sendMessage(text)
    threading.Timer(1.0, sendInfo, []).start()

sendInfo()








print("Create info server instance")
server = SimpleWebSocketServer('', WS_INFO_PORT, SimpleEcho)
print("Start websocket")
server.serveforever()
