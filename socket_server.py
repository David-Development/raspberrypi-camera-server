import picamera
import threading
import socket
import select
from threading import Thread
import subprocess
import signal
import sys
import time
from datetime import datetime, timedelta
import multiprocessing
import queue
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from wifi_monitor import ConnectionMonitor
from iwconfig import iwconfig
import re

#from alternative.raspberry_streaming_server import RaspberryStreamingServer

#from gpiozero import CPUTemperature
import os
import io
import psutil

running = True


CAMERA_MODE = 0
FRAMERATE = 25
ROTATION = 0

WS_INFO_PORT = 8082
HOST = "0.0.0.0"
print("Host: ", HOST, " Port: ", WS_INFO_PORT)

regexCameraResolution = r"Camera-Width: (\d+) Camera-Height: (\d+)"

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

    def handleMessage(self):
        # echo message back to client
        #self.sendMessage(self.data)
        print("Message received: ", self.data)

        matches = re.search(regexCameraResolution, self.data)

        if matches:
            print("Starting camera!")
            width = matches.group(1)
            height = matches.group(2)

            try:
                self.rss = RaspberryRaspiVidServer(self.address[0], width, height)
                rssThread = Thread(target=self.rss.start)
                rssThread.start()
            except Exception as e:
                print(e)
        else:
            print("Can't handle that message.. Invalid format")


    def handleConnected(self):
        print(self.address, 'connected')
        #try:
        #    self.rss = RaspberryStreamingServer()
        #    rssThread = Thread(target=self.rss.start)
        #    rssThread.start()
        #except Exception as e:
        #    print(e)
        clients.append(self)

    def handleClose(self):
        print(self.address, 'closed')
        self.rss.stop()
        clients.remove(self)


class RaspberryRaspiVidServer(object):
    def __init__(self, ip, cameraWidth, cameraHeight):
        self.ip = ip
        self.cameraWidth = cameraWidth
        self.cameraHeight = cameraHeight
        #print("init raspivid")

    def start(self):
        extraParams = "-b 2000000"
        # 2  MBits/s = 2000000
        # https://www.modmypi.com/blog/raspberry-pi-camera-board-raspivid-command-list
        command = "raspivid -n -t 0 -w {} -h {} {} -o - | nc -k -l -p 2222".format(self.cameraWidth, self.cameraHeight, extraParams)
        print(command)
        self.proc1 = subprocess.Popen("exec " + command, shell=True, preexec_fn=os.setsid)

    def stop(self):
        print("Stop requested!")
        if self.proc1:
            #self.proc1.kill()
            os.killpg(os.getpgid(self.proc1.pid), signal.SIGTERM)  # Send the signal to all the process groups
            print("Stopped raspivid")


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
