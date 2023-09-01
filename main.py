import socket
import random
import uasyncio
from machine import I2C
from machine import Pin
from machine import sleep
import mpu6050

i2c = I2C(scl=Pin(22), sda=Pin(21))
mpu = mpu6050.accel(i2c)

UDP_IP = "172.16.1.120"
UDP_PORT = 5000
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("Hello !")

last_gx = 0
last_gy = 0
last_gz = 0
raw_gx = 0
raw_gy = 0
raw_gz = 0
gx = 0
gy = 0
gz = 0

def low_pass_filter(prev_val, new_val, alpha):
    return alpha * prev_val + (1 - alpha) * new_val

async def readGyro():
    global gx, gy, gz, last_gx, last_gy, last_gz, raw_gx, raw_gy, raw_gz
    while True:
        last_gx = gx
        last_gy = gy
        last_gz = gz

        g_data = mpu.get_values()

        raw_gx = g_data['GyX']
        raw_gy = g_data['GyY']
        raw_gz = g_data['GyZ']
        gx = low_pass_filter(last_gx, raw_gx, 0.9)
        gy = low_pass_filter(last_gy, raw_gy, 0.9)
        gz = low_pass_filter(last_gz, raw_gz, 0.9)
        
        print(g_data)
        await uasyncio.sleep_ms(500)
        
async def telemetry():
    global gx, gy, gz
    while True:
        msg = str(gx)+","+str(gy)+","+str(gz)+","+"\n"
#         print(msg)
        sock.sendto(msg.encode(), (UDP_IP, UDP_PORT))    
#     sock.close()
        await uasyncio.sleep_ms(10)

async def main_task():
    task_1 = uasyncio.create_task(readGyro())
    task_2 = uasyncio.create_task(telemetry())
    await uasyncio.gather(task_1, task_2)

uasyncio.run(main_task()) 