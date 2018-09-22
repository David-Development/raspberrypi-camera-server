# Raspberry Pi Video/Camera Streaming Server

This is a demonstration for low latency streaming of the Pi's camera module to any client that can read raw h264 video streams via TCP Sockets (such as [David-Development/raspberrypi-camera-android-client](https://github.com/David-Development/raspberrypi-camera-android-client/tree/master))
The development of this project was inspired by some of the ideas from the great [waveform80/pistreaming](https://github.com/waveform80/pistreaming) project.


## Installation

Firstly make sure you've got a functioning Pi camera module (test it with
`raspistill / raspivid` to be certain). Then make sure you've got the following packages
installed:

```bash
sudo apt-get install libav-tools git
```

Next, download the repo, install the dependencies and run the server

```bash
# clone repo
git clone https://github.com/David-Development/raspberrypi-camera-server.git
cd raspberrypi-camera-server/

# install dependencies
pip3 install picamera
pip3 install git+https://github.com/dpallot/simple-websocket-server.git
pip3 install psutil

# start server
python3 socket_server.py
```
