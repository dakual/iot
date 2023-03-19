from _thread import start_new_thread
from time import sleep
from machine import Pin
from machine import Timer
import telegram
import os
import gc

class Seismograph():
  calibrationSampleSize = 1000
  calibrationAvarage    = 0
  alarmThreshold        = 30
  alarmPercentage       = 2
  alarmSampleSize       = 100
  alarmState            = 0
  
  def __init__(self, accelerator):
    self.tmr    = Timer(1)
    self.acc    = accelerator
    self.calibrate()

  def start(self):
    start_new_thread(self.run, ())

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

      sleep(0.01)

  def calibrate(self):
    for num in range(0, self.calibrationSampleSize):
      self.calibrationAvarage += self.acc.getData()
      sleep(0.01)
    self.calibrationAvarage /= self.calibrationSampleSize

    return self.calibrationAvarage

  def alarm(self, state):
    if state == 1:
      print("Alarm active!")
      if self.alarmState == 0:
        self.tmr.init(period=100, callback=lambda timer: Seismograph.flashlight())
        # telegram.telegram_send("[ALARM] active")
    else:
      print("Alarm inactive")
      self.tmr.deinit()
      # telegram.telegram_send("[ALARM] inactive")
  
  @staticmethod
  def flashlight():
    led = Pin(4, Pin.OUT, value=1)
    sleep(0.01)
    led.value(0)

  def getValue(self):
    return self.value
