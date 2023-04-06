from time import sleep, ticks_ms
from machine import Pin, PWM
from machine import Timer
# import uasyncio as asyncio
# from machine import RTC
from telegram import telegram_send
# import os
import gc

tmr    = Timer(1)
light  = Pin(4, Pin.OUT, value=0)
buzzer = PWM(Pin(16), freq=1, duty=0)


class Seismograph():
  calibrationSampleSize = 1000
  calibrationAvarage    = 0
  alarmState            = 0
  cnf                   = {}
  
  def __init__(self, accelerator, config):
    # self.logger = Logger("/sd/seismic.log", 5242880, 10)
    self.acc    = accelerator
    self.cnf    = config
    self.calibrate()

  def run(self):
    samples = 0
    counter = 0
    timestamp_acc = 0
    
    while True:
      self.value = self.acc.getData()
      minVal     = self.calibrationAvarage - round((self.calibrationAvarage * self.cnf.ALARM["average"]) / 100)
      maxVal     = self.calibrationAvarage + round((self.calibrationAvarage * self.cnf.ALARM["average"]) / 100)
      counter   += 1 if self.value < minVal or self.value > maxVal else 0
      samples   += 1

      if samples >= self.cnf.ALARM["samples"]:
        if counter >= self.cnf.ALARM["threshold"]:
          self.alarm(1)
          self.alarmState=1
        else:
          if self.alarmState == 1:
            self.alarm(0)
            self.alarmState=0
              
        samples = 0
        counter = 0

      if ticks_ms() - timestamp_acc > (10 * 6000):
        timestamp_acc = ticks_ms()
        if self.alarmState != 1:
          gc.collect()
          self.calibrate()
      else:
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
      if self.alarmState == 0:
        print("Alarm active!")
        if self.cnf.ALARM["telegram"] == 1:
          telegram_send("[ALARM] active", self.cnf)
        tmr.init(period=100, mode=Timer.PERIODIC, callback=lambda t:self.notify())
          # asyncio.run(telegram.telegram_send("[ALARM] active", self.cnf))
    else:
      print("Alarm inactive")
      tmr.deinit()
      buzzer.duty(0)
      light.value(0)
 
  def notify(self):
    if self.cnf.ALARM["flashlight"] == 1:
      light.value(1)
    if self.cnf.ALARM["sound"] == 1:
      buzzer.duty_u16(9000)
      buzzer.freq(659)
    sleep(0.02)
    if self.cnf.ALARM["flashlight"] == 1:
      light.value(0)
    if self.cnf.ALARM["sound"] == 1:
      buzzer.duty_u16(9000)
      buzzer.freq(831)

  def getValue(self):
    return self.value
