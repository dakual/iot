from microWebSrv import MicroWebSrv
from machine import I2C
from machine import Pin
from machine import sleep
from machine import Timer
from machine import SDCard
from machine import RTC
import network
import random
import json
import secrets
import gc
import os
import ntptime
import time
import utils


tm = Timer(0)


def initWIFI():
  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)
  if not wlan.isconnected():
    print('Connecting to WiFi Network Name:', secrets.SSID)
    wlan.connect(secrets.SSID, secrets.PASSWORD)
    while not wlan.isconnected():
      pass

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


def rtm(timer, websocket):
  dict = {} 
  dict['value'] = random.randint(5000, 15000)
  dict['date']  = "2023"
  websocket.SendText(json.dumps(dict))

def _acceptWebSocketCallback(webSocket, httpClient):
  print("New client connected!")
  webSocket.ClosedCallback = _closedCallback
  cb = lambda timer: rtm(timer, webSocket)
  tm.init(period=10, callback=cb)

def _closedCallback(webSocket):
  print("Cliend disconnected!")
  tm.deinit()
  gc.collect()



if __name__ == "__main__":
  print("initializing...")
  initWIFI()
  initRTC()
  initSD()

  print("Starting server")
  srv = MicroWebSrv(webPath='www/')
  srv.MaxWebSocketRecvLen = 256
  srv.WebSocketThreaded		= True
  srv.AcceptWebSocketCallback = _acceptWebSocketCallback
  srv.Start()