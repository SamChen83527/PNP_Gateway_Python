from . import SerialPortManager_module
from . import PNP_procedure
import json

# loop
while True:
    
    msg = ''
    
    # read msg from XBee
    while True:
        msg = SerialPortManager_module().readMsg()
        if msg != '' and msg.endswith('<CR>'):
            msg = msg.replace('<CR>','').strip()
            # print (msg)
            break
    
    # doRequest
    PNP_procedure(msg)