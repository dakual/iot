# from imu import MPU6050
# from machine import Pin, I2C
# import time

# i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
# imu = MPU6050(i2c)

# while True:
#   print(imu.accel.xyz,imu.gyro.xyz,imu.temperature,end='\r')
#   time.sleep(0.5) .
from microdot import Microdot
from microdot import send_file
from machine import Pin
from machine import Timer
from machine import idle
from machine import reset
from machine import freq
from Configs import Configs
import network
import gc

freq(240000000) 

tmr = Timer()
cnf = Configs()
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
  led = Pin("LED", Pin.OUT)
  led.on()


@app.route('/')
def hello(request):
    return send_file('www/index.html')


@app.route('/save', methods=['POST'])
def save(request):
  alarm_threshold = request.form["alarm_threshold"]
  alarm_average   = request.form["alarm_average"]
  alarm_samples   = request.form["alarm_samples"]
  alarm_telegram  = request.form["alarm_telegram"]
  
  config = { 
    "ALARM" : {
      "threshold": int(alarm_threshold), 
      "average": float(alarm_average), 
      "samples": int(alarm_samples),
      "telegram": int(alarm_telegram)
    }
  } 

  cnf.update(config)
  # tmr.init(period=2000, callback=lambda timer: reset())

  return "OK", 200, {'Content-Type': 'text/html'}

  

if __name__ == "__main__":
  print("initializing...")
  initWIFI()
  print(gc.mem_free())
  print("Starting web server")
  app.run(port=80, debug=True)


import sys
import gc
dir()
sys.modules

import micropython
micropython.mem_info()