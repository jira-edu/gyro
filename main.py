import socket
import random
import uasyncio

UDP_IP = "172.16.1.111"
UDP_PORT = 5000
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("Hello !")

new_gx = 0
gx = 0
gy = 0
gz = 0

def low_pass_filter(prev_val, new_val, alpha):
    return alpha * prev_val + (1 - alpha) * new_val

async def readGyro():
    global gx, gy, gz, new_gx
    while True:
        last_gx = gx
        new_gx = random.randint(0, 360)
        gx = low_pass_filter(last_gx, new_gx, 0.9)
        gy = random.randint(0, 360)
        gz = random.randint(0, 360)
        await uasyncio.sleep_ms(100)
        
async def telemetry():
    global gx, gy, gz, new_gx
    while True:
        msg = str(gx)+","+str(gy)+","+str(gz)+","+str(new_gx)+"\n"
#         print(msg)
        sock.sendto(msg.encode(), (UDP_IP, UDP_PORT))    
#     sock.close()
        await uasyncio.sleep_ms(100)

async def main_task():
    task_1 = uasyncio.create_task(readGyro())
    task_2 = uasyncio.create_task(telemetry())
    await uasyncio.gather(task_1, task_2)

uasyncio.run(main_task()) 