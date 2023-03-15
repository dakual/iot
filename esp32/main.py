from microWebSrv import MicroWebSrv
from machine import I2C
from machine import Pin
from machine import sleep
from machine import Timer
from machine import SDCard
from machine import RTC
from machine import idle
import network
import random
import json
import secrets
import gc
import os
import ntptime
import time
import utils
import mpu6050


tmr = Timer(0)
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
mpu = mpu6050.accel(i2c)


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
  print('Synchronizing NTP data time')
  UTC_OFFSET = 2 * 60 * 60
  rtc = RTC()
  ntptime.settime()
  rtc.init (
    time.localtime (
      ntptime.time() + UTC_OFFSET
    )
  )
  print(utils.get_datetime())

def initSD():
  print('Mounting SD card')
  try:
    if 'sd' not in os.listdir('/'):
      sd = SDCard()
      os.mount(sd, "/sd")
  except:
    return False
  return True


def getData():   
    acc    = mpu.get_values()
    xValue = acc["x"] + 2
    yValue = acc["y"] + 2
    zValue = acc["z"] + 2

    total  = xValue * yValue * zValue
    total  = round(total * 10000)
    
    return total

def rtm(timer, websocket):
  dict = {} 
  dict['value'] = getData() # random.randint(5000, 15000)
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
  gc.collect()



    
    
if __name__ == "__main__":
  print("initializing...")
  initWIFI()
  initRTC()
  initSD()

  print("Starting server")
  srv = MicroWebSrv(webPath='www/')
  srv.MaxWebSocketRecvLen = 256
  srv.WebSocketThreaded = True
  srv.AcceptWebSocketCallback = _acceptWebSocketCallback
  srv.Start()
