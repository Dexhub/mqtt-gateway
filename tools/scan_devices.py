#!/usr/bin/env python3
# coding=utf-8

from bluepy.btle import Scanner, DefaultDelegate, UUID, Peripheral

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print("Discovered device", dev.addr)
        elif isNewData:
            print("Received new data from", dev.addr)


scanner = Scanner().withDelegate(ScanDelegate())
devices = scanner.scan(10.0)

dev_name_uuid = UUID(0x2A00)
for dev in devices:
    print("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
    for (adtype, desc, value) in dev.getScanData():
        print("  %s = %s" % (desc, value))
    if dev.addrType == 'public':
        p = None
        try:
            p = Peripheral(dev.addr, dev.addrType)
            ch = p.getCharacteristics(uuid=dev_name_uuid)[0]
            if (ch.supportsRead()):
                print("Get Complete Local Name = %s" % ch.read())
        except Exception as _:
            pass
        finally:
            if p is not None:
                p.disconnect()
