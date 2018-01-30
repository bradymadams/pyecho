import os
import sys
import time
import datetime
import threading
import usb.core

class DecibelMeter(object):
    class Record(object):
        def __init__(self, decibels):
            self.decibels = decibels
            self.date = datetime.datetime.now()

        def __str__(self):
            return str(self.date) + ' -- %4.1f' % self.decibels

    def __init__(self):
        self.dev = usb.core.find(idVendor=0x16c0, idProduct=0x5dc)

        assert self.dev is not None

    def details(self):
        s = self.dev
        s += hex(dev.idVendor) + ', ' + hex(dev.idProduct)
        return s

    def retrieve(self):
        ret = self.dev.ctrl_transfer(0xC0, 4, 0, 0, 200)
        dB = (ret[0] + ((ret[1] & 3) * 256)) * 0.1 + 30
        return DecibelMeter.Record(dB)

class DecibelHistory(object):
    def __init__(self, meter, recorder, delta):
        self.meter = meter
        self.recorder = recorder
        self.delta = delta
        self._keep_recording = False

    def start(self):
        self._keep_recording = True
        t = threading.Thread(None, self._record)
        t.start()

        return t

    def stop(self):
        self._keep_recording = False

    def _record(self):
        while self._keep_recording:
            t1 = datetime.datetime.now()
            
            rec = self.meter.retrieve()

            #print(rec)
            self.recorder.store_measurement(rec)

            t2 = datetime.datetime.now()

            time.sleep((self.delta - (t2 - t1)).total_seconds())

class DecibelHistoryRecorder(object):
    def store_measurement(self, rec):
        raise NotImplementedError()

class DecibelHistoryRecorderText(DecibelHistoryRecorder):
    def __init__(self, text_file):
        self._file = open(text_file, 'a')

    def __del__(self):
        self._file.close()

    def store_measurement(self, rec):
        self._file.write('%s, %4.1f\n' % (rec.date, rec.decibels))
        self._file.flush()

def main():
    meter = DecibelMeter()
    recorder = DecibelHistoryRecorderText(sys.argv[1])
    hist = DecibelHistory(meter, recorder, datetime.timedelta(seconds=1))
    hist.start()

    while not os.path.exists('STOP'):
        True

    hist.stop()

if __name__ == '__main__':
    main()

