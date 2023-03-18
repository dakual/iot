import os

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

def get_filesize(fn: str) -> int:
    return os.stat(fn)[6]

def try_remove(fn: str) -> None:
    try:
        os.remove(fn)
    except OSError:
        pass

def try_rename(fn: str) -> None:
    try:
        os.rename(fn)
    except OSError:
        pass

def unquote_plus(s):
    # TODO: optimize
    s = s.replace("+", " ")
    arr = s.split("%")
    arr2 = [chr(int(x[:2], 16)) + x[2:] for x in arr[1:]]
    return arr[0] + "".join(arr2)

def parse_qs(s):
    res = {}
    if s:
        pairs = s.split("&")
        for p in pairs:
            vals = [unquote_plus(x) for x in p.split("=", 1)]
            if len(vals) == 1:
                vals.append(True)
            old = res.get(vals[0])
            if old is not None:
                if not isinstance(old, list):
                    old = [old]
                    res[vals[0]] = old
                old.append(vals[1])
            else:
                res[vals[0]] = vals[1]
    return res