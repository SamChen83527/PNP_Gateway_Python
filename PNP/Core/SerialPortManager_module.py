import time
import json
import serial
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class SerialPortManager():
    def __init__(self):
        self.ser = serial.Serial(
            port='/dev/ttyUSB0',
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )

    def readMsg(self):
        msg = str(self.ser.readline().strip(), 'utf-8')
        return msg

    def writeMsg(self, msg):
        self.ser.write(str.encode(msg))
        
    def sendRequ(self, request):
        request_json = json.loads(request)
        device_ID = request_json["device_ID"]

        # send request
        self.writeMsg(request)

        # read response from device
        break_count = 0
        while True:
            msg = self.readMsg()
            break_count = break_count + 1
            if msg != '' and msg.endswith('<CR>'):
                msg = msg.replace('<CR>','').strip()
                msg_json = json.load(msg)
                if msg_json["device_ID"] == device_ID:
                    break
            elif break_count == 10:
                msg = None
                break
            time.sleep(1)
        return msg
    
    def isOpen(self):
        serIsOpen = self.ser.isOpen()
        return serIsOpen
    
    def close(self):
        self.ser.close()
        
        