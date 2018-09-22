import re
import subprocess as sp


class iwconfig():
    def __init__(self):
        self.regex = r".*IEEE\s(.*?)\sESSID:\"(.*?)\".*Frequency:(.*?)Acc.*Bit Rate=(.*?)Tx-Power=(.*?)Ret.*Link Quality=(.*?)Signal level=(.*?)Rx.*retries:(\d*)"

    def getIwconfig(self):
        p = sp.Popen(["iwconfig"],stdin=sp.PIPE,stdout=sp.PIPE,stderr=sp.PIPE)
        out,err = p.communicate()
        input = out.decode()
        matches = re.search(self.regex, input, re.DOTALL)
        if matches:
            ieee = matches.group(1).strip()
            essid = matches.group(2).strip()
            frequency = matches.group(3).strip()
            bitRate = matches.group(4).strip()
            txPower = matches.group(5).strip()
            linkQuality = matches.group(6).strip()
            signalLevel = matches.group(7).strip()
            txExcessiveRetries = matches.group(8).strip()

            result = ""
            #result  = "IEEE: " + ieee + "\n"
            #result += "ESSID: " + essid + " "
            #result += "Frq: " + frequency + "\n"
            #result += "Bit-Rate: " + bitRate + "\n"
            #result += "TxPower: " + txPower + "\n"
            result += "LinkQuality: " + linkQuality + "\n"
            result += "SignalLevel: " + signalLevel + "\n"
            result += "TxExRet: " + txExcessiveRetries

            return result
