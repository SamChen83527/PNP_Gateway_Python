import requests, json
# https://codertw.com/%E7%A8%8B%E5%BC%8F%E8%AA%9E%E8%A8%80/395321/
# https://blog.gtwang.org/programming/python-requests-module-tutorial/

class HTTPManager():
    def __init__(self, url):
        self.url = url
    
    def sendPOST(self, target, POST_data):
        url = self.url + "/" + target
        if "http://" not in url:
            url = "http://" + url
        print ('Send POST:')
        print ('url: ' + url)
        print ('message body: ' + POST_data)
        r = requests.post(url, data = POST_data)
        print ('status code: {statusCode}'.format(statusCode = r.status_code))
        print ('created at: ' + r.headers["location"])
        print ('\n')
        return r.headers["location"]
    
    def sendGET(self, url):
        if "http://" not in url:
            url = "http://" + url
        print ('Send GET:')
        print ('url: ' + url)
        r = requests.get(url)

        print (r.text)
        print ('status code: {statusCode}'.format(statusCode = r.status_code))
        if r.status_code == requests.codes.ok:
            print("OK")
        print ('\n')
        return r.text

    def sendPatch(self, target, PATCH_data):
        url = self.url + "/" + target
        if "http://" not in url:
            url = "http://" + url
        print ('Send PATCH:')
        print ('url: ' + url)
        print ('message body: ' + PATCH_data)
        
        r = requests.patch(url, data = PATCH_data)
        print ('status code: {statusCode}'.format(statusCode = r.status_code))





