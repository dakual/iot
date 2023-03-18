# import os
# import machine


# class Log():

#     def __init__(self, filename, maxBytes=0, backupCount=0):
#         self.rtc = machine.RTC()
#         self.filename = filename
#         self.maxBytes = maxBytes
#         self.backupCount = backupCount
#         self._counter = self.get_filesize(self.filename)

#     def emit(self, record):
#         y,m,d,_,h,mi,s,_ = self.rtc.datetime()
#         record   = f"%d-%d-%d %d:%d:%d - {record}" % (y,m,d,h,mi,s)
#         s_len    = len(record)

#         if self.maxBytes and self.backupCount and self._counter + s_len > self.maxBytes:
#             self.try_remove(self.filename + ".{0}".format(self.backupCount))

#             for i in range(self.backupCount - 1, 0, -1):
#                 if i < self.backupCount:
#                     self.try_rename(self.filename + ".{0}".format(i), self.filename + ".{0}".format(i + 1))

#             self.try_rename(self.filename, self.filename + ".1")
#             self._counter = 0

#         with open(self.filename, "a") as f:
#             f.write(record + "\n")

#         self._counter += s_len

#     def try_remove(self, fn: str) -> None:
#         try:
#             os.remove(fn)
#         except OSError:
#             pass

#     def get_filesize(self, fn: str) -> int:
#         try:
#             return os.stat(fn)[6]
#         except OSError:
#             return 0

#     def try_rename(fn: str) -> None:
#         try:
#             os.rename(fn)
#         except OSError:
#             pass