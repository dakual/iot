from _thread import start_new_thread, allocate_lock
from mpu6050 import accel
from time import sleep
from machine import I2C
from machine import Pin
from machine import RTC
from machine import Timer
from RotatingLog import RotatingLog
from telegram import telegram_send
import gc
import os
import utils

class Seismograph():
  calibrationSampleSize = 1000
  calibrationAvarage    = 0
  alarmThreshold        = 30
  alarmPercentage       = 0.7
  alarmSampleSize       = 100
  alarmState            = 0
  
  def __init__(self):
    self.i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    self.mpu = accel(self.i2c)
    self.rtc = RTC()
    self.tmr = Timer(1)
    self.calibrate()

  def start(self):
    start_new_thread(self.run, ())

  def run(self):
    samples = 0
    counter = 0

    minVal = self.calibrationAvarage - round((self.calibrationAvarage * self.alarmPercentage) / 100)
    maxVal = self.calibrationAvarage + round((self.calibrationAvarage * self.alarmPercentage) / 100)
    
    while True:
      sensorValue = self.getData()
      self.sdlogger(sensorValue)
      
      counter += 1 if sensorValue < minVal or sensorValue > maxVal else 0
      samples += 1
      
      if samples >= self.alarmSampleSize:
        if(counter >= self.alarmThreshold):
          self.alarm(1)
          self.alarmState=1
        else:
          if self.alarmState == 1:
            self.alarm(0)
            self.alarmState=0
              
        samples = 0
        counter = 0
        # gc.collect()
    
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

  def alarm(self, state):
    if state == 1:
      print("Alarm active!")
      if self.alarmState == 0:
        self.tmr.init(period=100, callback=lambda timer: Seismograph.flashlight())
        telegram_send("[ALERT] Alarm active!")
    else:
      print("Alarm inactive")
      self.tmr.deinit()
      telegram_send("Alarm inactive")
  
  @staticmethod
  def flashlight():
    led = Pin(4, Pin.OUT, value=1)
    sleep(0.01)
    led.value(0)

  def sdlogger(self, value):
    y,m,d,_,h,mi,s,_ = self.rtc.datetime()
    datetime = '%d-%d-%d %d:%d:%d' % (y,m,d,h,mi,s)
    record   = f"{datetime} - {value}"
    bacCount = 10
    filename = "/sd/seismic.log"
    maxBytes = 5242880

    try:
      filesize = utils.get_filesize(filename)
    except OSError:
      filesize = 0
    
    if filesize > maxBytes:
      utils.try_remove(filename + ".{0}".format(bacCount))

      for i in range(bacCount - 1, 0, -1):
        if i < bacCount:
          try:
            os.rename(
              filename + ".{0}".format(i),
              filename + ".{0}".format(i + 1),
            )
          except OSError:
            pass
      
      utils.try_rename(filename, filename + ".1")

    with open(filename, "a") as f:
      f.write(record + "\n")
    gc.collect()

