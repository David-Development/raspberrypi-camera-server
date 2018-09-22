from iwconfig import iwconfig

iwconf = iwconfig()
print(iwconf.getIwconfig())

#wifi = open("/proc/net/wireless",'r')
#wifi.readline()
#wifi.readline()
#wlan0 = wifi.readline()
#wifiArr = wlan0.strip().split()
#print(wifiArr)
#linkQuality = wifiArr[2]
#wifiLevel = wifiArr[3]
#noise = wifiArr[4]
#retryCount = wifiArr[8]
#print(linkQuality)
#print(wifiLevel + " dBm")
#print(noise)
#print(retryCount)
#wifi.close()
