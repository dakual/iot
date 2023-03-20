# from microWebSrv import MicroWebSrv
from _thread import start_new_thread
from machine import Pin
from machine import Timer
# from machine import SDCard
# from machine import RTC
from machine import idle
from machine import I2C
from seismic import Seismograph
# from seismic import Logger
from mpu6050 import Accelerator
from configs import Configs
import network
from microdot import Microdot
# import ntptime
import json
# import os
# import time
import gc

tmr = Timer(0)
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
cnf = Configs()
mpu = Accelerator(i2c)
ses = Seismograph(mpu, cnf)
app = Microdot()

def initWIFI():
  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)
  if not wlan.isconnected():
    print('Connecting to WiFi Network Name:', cnf.WLAN["ssid"])
    wlan.connect(cnf.WLAN["ssid"], cnf.WLAN["password"])
    while not wlan.isconnected():
      idle()

  print('Connected. IP Address:', wlan.ifconfig()[0])
  led = Pin(33, Pin.OUT)

# def initRTC():
#   print('Synchronizing NTP date time')
#   UTC_OFFSET = 2 * 60 * 60
#   rtc = RTC()
#   try:
#       time.sleep(0.1)
#       ntptime.settime()
      
#       rtc.init (
#         time.localtime (
#           ntptime.time() + UTC_OFFSET
#         )
#       )      
#   except:
#       print('NTP could not Synchronized!')
      
# def initSD():
#   print('Mounting SD card')
#   try:
#     if 'sd' not in os.listdir('/'):
#       sd = SDCard()
#       os.mount(sd, "/sd")
#   except:
#     print('SD Card could not mounted!')

# def rtm(timer, websocket):
#   dict = {} 
#   dict['value'] = ses.getValue()
#   dict['date']  = "2023"
#   websocket.SendText(json.dumps(dict))

# def _acceptWebSocketCallback(webSocket, httpClient):
#   print("New client connected!")
#   webSocket.ClosedCallback = _closedCallback
#   cb = lambda timer: rtm(timer, webSocket)
#   tmr.init(period=10, callback=cb)

# def _closedCallback(webSocket):
#   print("Cliend disconnected!")
#   tmr.deinit()

@app.route('/')
def hello(request):
  print(gc.mem_free())
  gc.collect()
  print(gc.mem_free())
  return "OK", 200, {'Content-Type': 'text/html'}

if __name__ == "__main__":
  print("initializing...")
  initWIFI()
  # initRTC()
  # initSD()

  print("Starting seismic sensor")
  start_new_thread(ses.run, ())

  gc.collect()
  print(gc.mem_free())


  print("Starting web server")
  # srv = MicroWebSrv(webPath='www/')
  # # srv.MaxWebSocketRecvLen = 128
  # # srv.WebSocketThreaded = False
  # # srv.AcceptWebSocketCallback = _acceptWebSocketCallback
  # srv.Start()
  app.run(port=80)

