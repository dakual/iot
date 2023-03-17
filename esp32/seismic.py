from _thread import start_new_thread, allocate_lock
from mpu6050 import accel
from time import sleep
from machine import I2C
from machine import Pin
from machine import RTC
import gc

class Seismograph():
  calibrationSampleSize = 1000
  calibrationAvarage    = 0
  alarmThreshold        = 50
  alarmPercentage       = 1
  alarmSampleSize       = 200
  alarmState            = 0

  def __init__(self):
    self.i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    self.mpu = accel(self.i2c)
    self.rtc = RTC()
    self.led = Pin(4, Pin.OUT, value=0)
    self.calibrate()

  def start(self):
    start_new_thread(self.run, ())

  def run(self):
    samples = []
    counter = 0
    while True:
      sensorValue = self.getData()
      self.sdlogger(sensorValue)

      minVal = self.calibrationAvarage - round((self.calibrationAvarage * self.alarmPercentage) / 100)
      maxVal = self.calibrationAvarage + round((self.calibrationAvarage * self.alarmPercentage) / 100)
      counter += 1 if sensorValue < minVal or sensorValue > maxVal else 0
      
      samples.append(sensorValue)
      if len(samples) >= self.alarmSampleSize:
        if(counter >= self.alarmThreshold):
          self.alarm(1)
        else:
          if self.alarmState == 1: self.alarm(0)

        samples = []
        counter = 0
    
      gc.collect()
      sleep(0.01)

  def calibrate(self):
    for num in range(0, self.calibrationSampleSize):
      self.calibrationAvarage += self.getData()
      sleep(0.01)
    self.calibrationAvarage /= self.calibrationSampleSize

    return self.calibrationAvarage

  def getData(self):
    accVal = self.mpu.get_values()
    xValue = accVal["x"] + 2
    yValue = accVal["y"] + 2
    zValue = accVal["z"] + 2

    total  = xValue * yValue * zValue
    total  = round(total * 10000)

    return total

  @staticmethod
  def startAlarm(func, args=()):
    try:
        gc.collect()
        start_new_thread(func, args)
        return True
    except:
        pass

  def alarm(self, state):
    self.alarmState = state
    logState = "active" if state == 1 else "inactive"
    
    Seismograph.startAlarm(self.flashlight, (state, ))
    print(f"Alarm ({logState})")

  def flashlight(self, state):
    self.alarmState = state
    while self.alarmState == 1:
      self.led.value(1)
      sleep(0.3)
      self.led.value(0)
      sleep(0.1)

  def sdlogger(self, value):
    y,m,d,_,h,mi,s,_ = self.rtc.datetime()
    date = '%d%d%d-%d' % (y,m,d,h)
    file = "/sd/{}-seismic.log".format(date)
    with open(file, "a") as f:
      date = '%d-%d-%d %d:%d:%d' % (y,m,d,h,mi,s)
      f.write(f"{date} - {value}\r\n")
