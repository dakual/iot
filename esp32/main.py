from microWebSrv import MicroWebSrv
from machine import Pin
from machine import Timer
from machine import SDCard
from machine import RTC
from machine import idle
from machine import I2C
from seismic import Seismograph
from seismic import Logger
from mpu6050 import Accelerator
import network
import ntptime
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

def initRTC():
  print('Synchronizing NTP date time')
  UTC_OFFSET = 2 * 60 * 60
  rtc = RTC()
  try:
      time.sleep(0.1)
      ntptime.settime()
      
      rtc.init (
        time.localtime (
          ntptime.time() + UTC_OFFSET
        )
      )      
  except:
      print('NTP could not Synchronized!')
      
def initSD():
  print('Mounting SD card')
  try:
    if 'sd' not in os.listdir('/'):
      sd = SDCard()
      os.mount(sd, "/sd")
  except:
    print('SD Card could not mounted!')

def rtm(timer, websocket):
  dict = {} 
  dict['value'] = ses.getValue()
  dict['date']  = "2023"
  websocket.SendText(json.dumps(dict))

def _acceptWebSocketCallback(webSocket, httpClient):
  print("New client connected!")
  webSocket.ClosedCallback = _closedCallback
  cb = lambda timer: rtm(timer, webSocket)
  tmr.init(period=10, callback=cb)

def _closedCallback(webSocket):
  print("Cliend disconnected!")
  tmr.deinit()


if __name__ == "__main__":
  print("initializing...")
  initWIFI()
  initRTC()
  initSD()

  print("Starting seismic sensor")
  ses.start()

  # print("Starting web server")
  # srv = MicroWebSrv(webPath='www/')
  # srv.MaxWebSocketRecvLen = 64
  # srv.WebSocketThreaded = True
  # srv.AcceptWebSocketCallback = _acceptWebSocketCallback
  # srv.Start()

