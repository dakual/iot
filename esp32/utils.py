import os

def del_dir(dir_name):
	for item in os.listdir(dir_name):
		if '.' in item:
			os.remove(dir_name+'/'+item)
		else:
			del_dir(dir_name+'/'+item)
	os.rmdir(dir_name)
