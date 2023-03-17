import os
import machine
import time

def rmdir(d): 
	try:
		if os.stat(d)[0] & 0x4000:
			for f in os.ilistdir(d):
				if f[0] not in ('.', '..'):
					rmdir("/".join((d, f[0])))
			os.rmdir(d)
		else:
			os.remove(d)
	except:
		print("rm of '%s' failed" % d)

def lsdir(path, tabs=0):
  for file in os.listdir(path):
    stats = os.stat(path + "/" + file)
    filesize = stats[6]
    isdir = stats[0] & 0x4000
    if filesize < 1000:
        sizestr = str(filesize) + " by"
    elif filesize < 1000000:
        sizestr = "%0.1f KB" % (filesize / 1000)
    else:
        sizestr = "%0.1f MB" % (filesize / 1000000)
    prettyprintname = ""
    for _ in range(tabs):
        prettyprintname += " "
    prettyprintname += file
    if isdir:
        prettyprintname += "/"
    print('{0:<40} Size: {1:>10}'.format(prettyprintname, sizestr))
    if isdir:
        lsdir(path + "/" + file, tabs + 1)

def flash_led():
  led = Pin(4, Pin.OUT)
  led.on()
  time.sleep(0.3)
  led.off()
  time.sleep(0.1)
  led.on()
  time.sleep(0.2)
  led.off()