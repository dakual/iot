from _thread import start_new_thread
from machine import Pin
from machine import PWM
from machine import idle
from machine import I2C
from machine import Timer
from machine import reset
from machine import freq
# from machine import SDCard
# from machine import RTC
# from seismic import Logger
from seismic import Seismograph
from mpu6050 import Accelerator
from configs import Configs
from time import sleep
from microdot import Microdot, Response, Request
from microdot_utemplate import render_template
# import ntptime
import network
import gc

freq(240000000)

# tmr = Timer(0)
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
cnf = Configs()
mpu = Accelerator(i2c)
ses = Seismograph(mpu, cnf)
app = Microdot()

Response.default_content_type = 'text/html'
Request.socket_read_timeout   = None


def initWIFI():
  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)
  if not wlan.isconnected():
    print('Connecting to WiFi Network Name:', cnf.WLAN["ssid"])
    wlan.connect(cnf.WLAN["ssid"], cnf.WLAN["password"])
    while not wlan.isconnected():
      idle()

  print('Connected. IP Address:', wlan.ifconfig()[0])
  Pin(33, Pin.OUT, value=1)

@app.get('/')
def index(request):
  gc.collect()
  print(cnf.ALARM)
  return '<h1>Hello, World!</h1>', 200, {'Content-Type': 'text/html'}

@app.route('/settings')
def settings(request):
  gc.collect()
  return render_template('settings.html', args=cnf.ALARM)

@app.route('/save', methods=['POST'])
def save(request):
  alarm_threshold  = request.form["alarm_threshold"]
  alarm_average    = request.form["alarm_average"]
  alarm_samples    = request.form["alarm_samples"]
  alarm_telegram   = request.form["alarm_telegram"]
  alarm_flashlight = request.form["alarm_flashlight"]
  alarm_sound      = request.form["alarm_sound"]
  
  config = { 
    "ALARM" : {
      "threshold": int(alarm_threshold), 
      "average": float(alarm_average), 
      "samples": int(alarm_samples),
      "telegram": int(alarm_telegram),
      "flashlight": int(alarm_flashlight),
      "sound": int(alarm_sound)
    }
  }
  cnf.update(config)

  return "OK", 200, {'Content-Type': 'text/html'}



if __name__ == "__main__":
  print("initializing...")
  initWIFI()
  # initRTC()
  # initSD()

  print("Starting seismic sensor")
  start_new_thread(ses.run, ())

  print("Starting web server")
  app.run(port=80)