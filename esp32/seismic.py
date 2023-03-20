from time import sleep
from machine import Pin
from machine import Timer
import uasyncio as asyncio
# from machine import RTC
import telegram
# import os
import gc

class Seismograph():
  calibrationSampleSize = 1000
  calibrationAvarage    = 0
  alarmThreshold        = 30
  alarmPercentage       = 2
  alarmSampleSize       = 100
  alarmState            = 0
  
  def __init__(self, accelerator, config):
    self.tmr    = Timer(1)
    # self.logger = Logger("/sd/seismic.log", 5242880, 10)
    self.acc    = accelerator
    self.cnf    = config
    self.calibrate()

  def run(self):
    samples = 0
    counter = 0
    minVal  = self.calibrationAvarage - round((self.calibrationAvarage * self.alarmPercentage) / 100)
    maxVal  = self.calibrationAvarage + round((self.calibrationAvarage * self.alarmPercentage) / 100)
    
    while True:
      self.value = self.acc.getData()
      counter += 1 if self.value < minVal or self.value > maxVal else 0
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

      # self.logger.emit(self.value)
      # gc.collect()
      sleep(0.01)

  def calibrate(self):
    for num in range(0, self.calibrationSampleSize):
      self.calibrationAvarage += self.acc.getData()
      sleep(0.01)
    self.calibrationAvarage /= self.calibrationSampleSize

    return self.calibrationAvarage

  def alarm(self, state):
    gc.collect()

    if state == 1:
      print("Alarm active!")
      if self.alarmState == 0:
        self.tmr.init(period=100, callback=lambda timer: Seismograph.flashlight())
        asyncio.run(telegram.telegram_send("[ALARM] active", self.cnf))
    else:
      print("Alarm inactive")
      self.tmr.deinit()
 
  @staticmethod
  def flashlight():
    led = Pin(4, Pin.OUT, value=1)
    sleep(0.01)
    led.value(0)

  def getValue(self):
    return self.value


# class Logger():

#   def __init__(self, filename, maxBytes=0, backupCount=0):
#     self.rtc          = RTC()
#     self.filename     = filename
#     self.maxBytes     = maxBytes
#     self.backupCount  = backupCount
#     self._counter     = self.get_filesize(self.filename)

#   def emit(self, record):
#     y,m,d,_,h,mi,s,_ = self.rtc.datetime()
#     record   = f"%d-%d-%d %d:%d:%d - {record}" % (y,m,d,h,mi,s)
#     s_len    = len(record)

#     if self.maxBytes and self.backupCount and self._counter + s_len > self.maxBytes:
#       self.try_remove(self.filename + ".{0}".format(self.backupCount))

#       for i in range(self.backupCount - 1, 0, -1):
#         if i < self.backupCount:
#           self.try_rename(self.filename + ".{0}".format(i), self.filename + ".{0}".format(i + 1))

#       self.try_rename(self.filename, self.filename + ".1")
#       self._counter = 0

#     with open(self.filename, "a") as f:
#       f.write(record + "\n")

#     self._counter += s_len

#   def try_remove(self, fn: str) -> None:
#     try:
#       os.remove(fn)
#     except OSError:
#       pass

#   def get_filesize(self, fn: str) -> int:
#     try:
#       return os.stat(fn)[6]
#     except OSError:
#       return 0

#   def try_rename(fn: str) -> None:
#     try:
#       os.rename(fn)
#     except OSError:
#       pass
