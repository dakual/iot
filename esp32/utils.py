import os
import machine

def del_dir(dir_name):
	for item in os.listdir(dir_name):
		if '.' in item:
			os.remove(dir_name+'/'+item)
		else:
			del_dir(dir_name+'/'+item)
	os.rmdir(dir_name)

def get_datetime():
	rtc = machine.RTC()
	y,m,d,_,h,mi,s,_ = rtc.datetime ()
	return '%d-%d-%d %d:%d:%d' % (y,m,d,h,mi,s)