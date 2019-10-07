from SerialPortManager_module import SerialPortManager
while True:
    serialportmanager = SerialPortManager()
    msg = serialportmanager.readMsg()
    if msg != '' and msg.endswith('<CR>'):
        msg = msg.replace('<CR>','').strip()
        print (msg)
        break
    

# test ok