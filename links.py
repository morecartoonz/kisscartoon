import re
import base64
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
import binascii


class Link(object):
    def __init__(self, link, quality, rsk=None):
        self.link = link
        self.quality = quality
        self.rsk = rsk

    def is_valid(self):
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(regex, self.link)

    def is_encoded(self):
        raise NotImplementedError()

    def decode(self):
        raise NotImplementedError()

    def __repr__(self):
        return '<quality : {quality}, link : {link}>'.format(quality=self.quality, link=self.link)


class PlainLink(Link):
    def is_encoded(self):
        return False

    def decode(self):
        return self.link


class Base64Link(Link):
    def is_encoded(self):
        return True

    def decode(self):
        try:
            decoded = base64.b64decode(self.link)
        except TypeError:
            return None
        self.link = decoded
        if not self.is_valid():
            return None
        if decoded is None:
            return None
        return PlainLink(decoded, self.quality)

class AESLink(Link):
    def is_encoded(self):
        return True

    def decode(self):
        a = "a5e8d2e9c1721ae0e84ad660c472c1f3"

        #Hash rsk key to get decryption key
        sha = SHA256.new()
        sha.update(self.rsk)
        encKey = sha.digest()
        AES_KEY = AES.new(encKey, AES.MODE_CBC, a.decode('hex'))
        val = AES_KEY.decrypt(base64.b64decode(self.link))
        unpad = lambda s: s[:-ord(s[len(s) - 1:])]
        val = unpad(val)
        self.link = val
        if self.is_valid():
            return PlainLink(self.link, self.quality)
        else:
            return None

    def unpad(self, text, k=16):
        '''
        Remove the PKCS#7 padding from a text string

        Made by https://gist.github.com/chrix2
        '''
        nl = len(text)
        val = int(binascii.hexlify(text[-1]), 16)
        if val > k:
            raise ValueError('Input is not padded or padding is corrupt')

        l = nl - val
        return text[:l]

    def ensure_unicode(self, v):
        if isinstance(v, str):
            v = v.decode('utf8')
        return unicode(v)
