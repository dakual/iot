import machine

class accel():

    def __init__(self, i2c, addr=0x68):
        self.iic = i2c
        self.addr = addr
        self.iic.writeto(self.addr, bytearray([107, 0]))

    def get_raw_values(self):
        a = self.iic.readfrom_mem(self.addr, 0x3B, 14)
        return a

    def get_ints(self):
        b = self.get_raw_values()
        c = []
        for i in b:
            c.append(i)
        return c

    def bytes_toint(self, firstbyte, secondbyte):
        if not firstbyte & 0x80:
            return firstbyte << 8 | secondbyte
        return - (((firstbyte ^ 255) << 8) | (secondbyte ^ 255) + 1)

    def get_values(self):
        raw_ints = self.get_raw_values()
        vals = {}
        vals["x"] = self.bytes_toint(raw_ints[0], raw_ints[1])
        vals["y"] = self.bytes_toint(raw_ints[2], raw_ints[3])
        vals["z"] = self.bytes_toint(raw_ints[4], raw_ints[5])

        return vals  # returned in range of Int16 -32768 to 32767

    def get_smoothed_values(self, n_samples=10):
        result = self.get_values()
        for _ in range(0, n_samples - 1):
            data = self.get_values()
            for key in data.keys():
                result[key] += data[key]
        for key in data.keys():
            result[key] /= n_samples
        return result

    def calibrate(self, threshold=50, n_samples=100):
        while True:
            v1 = self.get_smoothed_values(n_samples)
            v2 = self.get_smoothed_values(n_samples)
            if all(abs(v1[key] - v2[key]) < threshold for key in v1.keys()):
                return v1  # Calibrated.
