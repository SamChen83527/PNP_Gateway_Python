from PNP.Main.HTTPManager_module import HTTPManager

url = 'http://140.115.110.69:8080/SensorThingsAPIPart2/v1.0'
httpManager = HTTPManager(url)

post_thing_request = '''{
  "name": "MY_DEVICE0001",
  "description": "CSRSR's sensor",
  "properties": {
    "UID": "MY_DEVICE0001"
  }
}'''

createdLocation = httpManager.sendPOST('Things', post_thing_request)

httpManager.sendGET(createdLocation)

# test ok

# Questions:
# self argument issue
# import issue: function, module, class http://www.codedata.com.tw/python/python-tutorial-the-2nd-class-3-function-module-class-package