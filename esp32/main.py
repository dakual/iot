from microWebSrv import MicroWebSrv
from machine import Pin
from machine import Timer
from machine import idle
from machine import I2C
from seismic import Seismograph
from mpu6050 import Accelerator
import network
import json
import secrets
import os
import time
import gc

tmr = Timer(0)
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
mpu = Accelerator(i2c)
ses = Seismograph(mpu)


def initWIFI():
  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)
  if not wlan.isconnected():
    print('Connecting to WiFi Network Name:', secrets.SSID)
    wlan.connect(secrets.SSID, secrets.PASSWORD)
    while not wlan.isconnected():
      idle()

  print('Connected. IP Address:', wlan.ifconfig()[0])
  led = Pin(33, Pin.OUT)

@MicroWebSrv.route('/save', 'POST')
def _httpHandlerTestPost(httpClient, httpResponse):
  formData  = httpClient.ReadRequestPostedFormData()
  f1 = formData["f1"]
  f2 = formData["f2"]
  f3 = formData["f3"]
  
  httpResponse.WriteResponseOk(
    headers        = None,
    contentType	   = "text/html",
    contentCharset = "UTF-8",
    content 		   = "saved"
  )

if __name__ == "__main__":
  print("initializing...")
  initWIFI()

  print("Starting seismic sensor")
  ses.start()

  print("Starting web server")
  srv = MicroWebSrv(webPath='www/')
  srv.Start(threaded=True)

