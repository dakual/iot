from microWebSrv import MicroWebSrv
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
import seismic

tmr = Timer(0)
ses = seismic.Seismograph()

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
  dict['value'] = ses.getData() # random.randint(5000, 15000)
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

  print("Starting seismic sensor")
  ses.start()

  print("Starting web server")
  srv = MicroWebSrv(webPath='www/')
  srv.MaxWebSocketRecvLen = 256
  srv.WebSocketThreaded = True
  srv.AcceptWebSocketCallback = _acceptWebSocketCallback
  srv.Start()
