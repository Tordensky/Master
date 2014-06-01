import time
import sphero

sphero_manager = sphero.SpheroManager()
device = sphero_manager.get_available_device()

device.connect()

def on_data(data):
    # print Gyro angle x in degrees
    print "GYRO", data.gyro.gyro_degrees.x

# set callback for data received from device
device.set_sensor_streaming_cb(on_data)

### Create streaming config
ssc = sphero.SensorStreamingConfig()

# Set streaming speed 10Hz
ssc.sample_rate = 10

# Number of packets to stream
ssc.num_packets = ssc.STREAM_FOREVER

# Activate streaming of GYRO
ssc.stream_gyro(True)

# Start streaming with this config
device.set_data_streaming(ssc)

time.sleep(60)

device.disconnect()

