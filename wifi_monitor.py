#ConnectionMonitor 
#Author: Jon Parise jlparise@gmail.com 
#Date: 3/13/2008 
#Description:  Montiors the specified interface and stores it's current state.  This includes read/write bytes, bytes per second  
#and other information. 

import time 

class ConnectionMonitor(): 
    def __init__(self,name): 
        """Construct it based on a name like eth1, it will monitor that name""" 
        self.__netFile = open("/proc/net/dev",'r') 
         
        self.__name = name 
        self.__lastCheckTime = time.time() 
        self.__timeDiff = 0 
         
        self.__lastReadBytes = 0 
        self.readBytes = 0 
        self.readPackets = 0 
        self.readErrs = 0 
        self.readDrop = 0 
        self.reafFifo = 0 
        self.readFrames = 0 
        self.readCompressed = 0 
        self.readMulticast = 0   
        self.readBps = 0 
        #parse write info 
        self.__lastWriteBytes =0 
        self.writeBytes = 0 
        self.writePackets = 0 
        self.writeErrs = 0 
        self.writeDrop = 0 
        self.writeFifo = 0 
        self.writeFrames = 0 
        self.writeCompressed = 0 
        self.writeMulticast = 0    
        self.writeBps =0 
        #self.update() 
     
    """ 
    Update 
    Inputs - self - reference to this class instance 
    Description: Updates the state of the interface and calculates Bytes per second 
    """ 
    def update(self): 
        self.__netFile = open("/proc/net/dev",'r') 
        line =" " 
        found = False 
        #read all the lines till the right one is found 
        while not line == None and not found: 
            line = self.__netFile.readline() 
            #find only the line with this name 
            if line.find(self.__name) > 0: 
                self.__netLine = line 
                found = True 
                 
        if(found): 
            tempSplit = line.split(" ") 
             
            netSplit = [] 
            for item in tempSplit: 
                if len(item) >0: 
                    netSplit.append(item) 

            #update times 
            prevTime = self.__lastCheckTime 
            currTime = time.time() 
             
            self.__timeDiff = currTime - prevTime 
             
            self.__lastCheckTime = currTime 
            #update last read/write bytes 
            self.__lastReadBytes = self.readBytes 
            self.__lastWriteBytes = self.writeBytes 
             
            #parse read info 
            self.readBytes = int(netSplit[1])
            self.readPackets = int(netSplit[2]) 
            self.readErrs = int(netSplit[3]) 
            self.readDrop = int(netSplit[4]) 
            self.reafFifo = int(netSplit[5]) 
            self.readFrames = int(netSplit[6]) 
            self.readCompressed = int(netSplit[7]) 
            self.readMulticast = int(netSplit[8])    
             
            #parse write info 
            self.writeBytes = int(netSplit[9]) 
            self.writePackets = int(netSplit[10]) 
            self.writeErrs = int(netSplit[11]) 
            self.writeDrop = int(netSplit[12]) 
            self.writeFifo = int(netSplit[13]) 
            self.writeFrames = int(netSplit[14]) 
            self.writeCompressed = int(netSplit[15]) 
            self.writeMulticast = int(netSplit[16])
             
            #doe Kbs calcs 
            if self.__timeDiff > 0: 
                self.readBps = ((self.readBytes - self.__lastReadBytes) / self.__timeDiff) 
                self.writeBps = ((self.writeBytes - self.__lastWriteBytes) / self.__timeDiff) 
                 
        #Bad interface name     
        else: 
            print("Name:" + name + "Not in file!") 

    """Output 
        inputs - self - reference for this class instance 
        description - prints all the information currently stored in this instance. 
    """         
    def output(self): 
            print("Read information:\n") 
             
            print("b/s: ", self.readBps)
            print("Bytes: ", self.readBytes)
            print("Packets: ", self.readPackets)  
            print("Errs: ", self.readErrs)
            print("Drop: ", self.readDrop)
            print("FIFO: ", self.reafFifo)
            print("Frames: ", self.readFrames)
            print("Compressed: ", self.readCompressed) 
            print("Multicast: ", self.readMulticast)
             
            print("\n\nWrite information:\n") 
             
            print("b/s: ", self.writeBps)
            print("Bytes: ", self.writeBytes)
            print("Packets: ", self.writePackets)  
            print("Errs: ", self.writeErrs)
            print("Drop: ", self.writeDrop) 
            print("FIFO: ", self.reafFifo)
            print("Frames: ", self.writeFrames)
            print("Compressed: ", self.writeCompressed) 
            print("Multicast: ", self.writeMulticast)  
      
#test for eth1 just loops forever printing the b/s if it is greater than 0        
if __name__ == "__main__": 
    cm = ConnectionMonitor("eth1") 
     
    while True: 
        cm.update() 
         
        if cm.readBps > 0: 
            print("Read b/s: ", cm.readBps) 
            print("Bytes: ", cm.readBytes)
        if cm.writeBps > 0: 
            print("Write b/s: ", cm.writeBps) 
            print("Bytes: ", cm.writeBytes) 
        time.sleep(1)  
