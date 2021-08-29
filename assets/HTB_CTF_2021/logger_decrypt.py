from Crypto.Cipher import AES
import base64, os

key = 'w0MrV1vBmZi1Z17v'
iv = 'Kh54H8JTmOYq5mre'
cipher = AES.new(key.encode('utf-8'), AES.MODE_CFB, iv.encode('utf-8'))
with open('anvzdgfuw1l.txt', 'r') as f:
        enc_txt = f.readlines()

try:
    for line in enc_txt:
        pt = cipher.decrypt(base64.b64decode(line.split("'")[1]))
        print(pt)    
except:
    print("Incorrect decryption")
