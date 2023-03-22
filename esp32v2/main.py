from _thread import start_new_thread
from machine import Pin
from machine import idle
from machine import I2C
from machine import reset
from machine import freq
from seismic import Seismograph
from mpu6050 import Accelerator
from configs import Configs
from time import sleep
from microWebSrv import MicroWebSrv
import network
import gc


freq(240000000)

# tmr = Timer(0)
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
cnf = Configs()
mpu = Accelerator(i2c)
ses = Seismograph(mpu, cnf)



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

def reboot():
    print("Resetting...")
    sleep(3)
    reset()


@MicroWebSrv.route('/settings')
def index(httpClient, httpResponse) :
	httpResponse.WriteResponsePyHTMLFile("www/test.pyhtml", vars=cnf.ALARM)

@MicroWebSrv.route('/save', 'POST')
def _httpHandlerTestPost(httpClient, httpResponse):
  formData        = httpClient.ReadRequestPostedFormData()
  alarm_threshold = formData["alarm_threshold"]
  alarm_average   = formData["alarm_average"]
  alarm_samples   = formData["alarm_samples"]
  alarm_telegram  = formData["alarm_telegram"]
  
  config = { 
    "ALARM" : {
      "threshold": int(alarm_threshold), 
      "average": float(alarm_average), 
      "samples": int(alarm_samples),
      "telegram": int(alarm_telegram)
    }
  } 

  cnf.update(config)
  #start_new_thread(reboot, ())

  httpResponse.WriteResponseOk(
      headers        = None,
      contentType	   = "text/html",
      contentCharset = "UTF-8",
      content 		   = "OK"
  )

  print("Resetting...")
  sleep(1)
  reset()

if __name__ == "__main__":
  print("initializing...")
  initWIFI()

  print("Starting seismic sensor")
  start_new_thread(ses.run, ())

  print("Starting web server")
  routeHandlers = [ ( "/", "GET",  index ) ] # routeHandlers=routeHandlers, 
  srv = MicroWebSrv(webPath='www/')
  srv.Start(threaded=True)