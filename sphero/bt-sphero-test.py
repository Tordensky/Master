import bluetooth
import time

target_name = "Sphero-RWO"
target_address = None


nearby_devices = bluetooth.discover_devices()
for bdaddr in nearby_devices:
    current_name = bluetooth.lookup_name(bdaddr, timeout=20)
    if target_name == current_name:
        target_address = bdaddr
        print "Found Sphero with name:", target_name
        port = 1
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

        sock.connect((target_address, port))
        time.sleep(10)
        sock.close()


        break
    else:
        print "not the device you are looking for", current_name




