# Raspberry Pi Video/Camera Streaming Server

This is a demonstration for low latency streaming of the Pi's camera module to
any client that can read raw h264 video streams via TCP Sockets (Such as [David-Development/raspberrypi-camera-android-client](https://github.com/David-Development/raspberrypi-camera-android-client/tree/master))
By developing this project I was inspired by some of the ideas from the great [waveform80/pistreaming](https://github.com/waveform80/pistreaming) project!

## Installation

Firstly make sure you've got a functioning Pi camera module (test it with
`raspistill / raspivid` to be certain). Then make sure you've got the following packages
installed:

```bash
sudo apt-get install libav-tools git
```

Next, clone this repository:

```bash
git clone https://github.com/David-Development/raspberrypi-camera-server.git
```


## Follow instructions given here: ...

