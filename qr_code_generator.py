import pyqrcode

url = pyqrcode.create("https://fairportrobotics.org/")
url.svg("qr.svg", scale=8)
