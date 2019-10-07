from SerialPortManager_module import SerialPortManager
from PNP_procedure import PNPRequest
import json

# loop
while True:
    
    msg = ''
    
    # read msg from XBee
    while True:
        msg = SerialPortManager.readMsg()
        if msg != '' and msg.endswith('<CR>'):
            msg = msg.replace('<CR>','').strip()
            # print (msg)
            break
    
    # doRequest
    PNP_procedure(msg)
    