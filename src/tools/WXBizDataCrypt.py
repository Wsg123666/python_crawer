import base64
import json
from Crypto.Cipher import AES
import requests


class WXBizDataCrypt:
    def __init__(self, appId, sessionKey):
        self.appId = appId
        self.sessionKey = sessionKey

    def decrypt(self, encryptedData, iv):
        # base64 decode
        sessionKey = base64.b64decode(self.sessionKey)
        encryptedData = base64.b64decode(encryptedData)
        iv = base64.b64decode(iv)
        cipher = AES.new(sessionKey, AES.MODE_CBC, iv)
        decrypted_str = str(self._unpad(cipher.decrypt(encryptedData)), encoding="UTF-8")
        print(decrypted_str)
        return json.dumps(decrypted_str)

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]


def run_crypt(js_code, encrypted_data, iv):
    appid = 'wx9d50f997541dfbe3'
    data = {
        "appid": appid,
        "secret": "b2857c18c84ab273b0a903a649a3275d",
        "js_code": js_code,
        "grant_type": "authorization_code"
    }
    resp = requests.get(url="https://api.weixin.qq.com/sns/jscode2session", params=data)
    if resp.status_code == 200:
        try:
            # session_key = json.loads(resp.text)["session_key"]
            session_key = "Bqpjn5qHCoCrleJ5u3eclA=="
            encrypted_data = encrypted_data
            iv = iv
            pc = WXBizDataCrypt(appid, session_key)
            return pc.decrypt(encrypted_data, iv)
        except KeyError:
            return json.dumps({"state": -1})   # code error
    else:
        return json.dumps({"state": -2})   # wechat server error
