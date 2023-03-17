import os

def try_remove(fn: str) -> None:
    try:
        os.remove(fn)
    except OSError:
        pass


def get_filesize(fn: str) -> int:
    return os.stat(fn)[6]


class RotatingLog():

    def __init__(self, filename, maxBytes=0, backupCount=0):
        super().__init__()
        self.filename = filename
        self.maxBytes = maxBytes
        self.backupCount = backupCount

        try:
            self._counter = get_filesize(self.filename)
        except OSError:
            self._counter = 0

    def emit(self, record):
        s_len = len(record)

        if self.maxBytes and self.backupCount and self._counter + s_len > self.maxBytes:
            try_remove(self.filename + ".{0}".format(self.backupCount))

            for i in range(self.backupCount - 1, 0, -1):
                if i < self.backupCount:
                    try:
                        os.rename(
                            self.filename + ".{0}".format(i),
                            self.filename + ".{0}".format(i + 1),
                        )
                    except OSError:
                        pass

            try:
                os.rename(self.filename, self.filename + ".1")
            except OSError:
                pass
            self._counter = 0

        with open(self.filename, "a") as f:
            f.write(record + "\n")

        self._counter += s_len
