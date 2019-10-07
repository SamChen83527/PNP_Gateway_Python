from ..\SerialPortManager_module import*
while True:
    msg = SerialPortManager_module().readMsg()
    if msg != '' and msg.endswith('<CR>'):
        msg = msg.replace('<CR>','').strip()
        print (msg)
        break
