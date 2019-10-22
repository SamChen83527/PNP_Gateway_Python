# -*- coding: UTF-8 -*-
from SerialPortManager_module import SerialPortManager
from PNP_procedure import PNPRequest
import json
import sys
import traceback

# loop
while True:

    try:
        msg = ''
        
        # read msg from XBee
        while True:
            serialportmanager = SerialPortManager()
            msg = serialportmanager.readMsg()
            if msg != '' and msg.endswith('<CR>'):
                msg = msg.replace('<CR>','').strip()
                print (msg)
                break
    
        # doRequest
        PNPRequest(msg)
        print ('\nPrcedure finished\n\n')
    except Exception as e:
        error_class = e.__class__.__name__ #取得錯誤類型
        detail = e.args[0] #取得詳細內容
        cl, exc, tb = sys.exc_info() #取得Call Stack
        lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
        fileName = lastCallStack[0] #取得發生的檔案名稱
        lineNum = lastCallStack[1] #取得發生的行號
        funcName = lastCallStack[2] #取得發生的函數名稱
        errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
        print(errMsg)