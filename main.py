from time import sleep
import network
import socket
from machine import Pin, PWM

#######GPIO SETUP#######
# LED
GREEN_LED = Pin(19, Pin.OUT)
RED_LED = Pin(18, Pin.OUT)
GREEN_LED.value(0)
RED_LED.value(0)

#ACTIVATE ENGINES
ENG12_ON = Pin(12, Pin.OUT)
ENG34_ON = Pin(13, Pin.OUT)
ENG12_ON.value(1)
ENG34_ON.value(1)

# DECLARE ENGINES PWM
R_ENGIN_1 = PWM(Pin(14))
R_ENGIN_1.freq(1000)
R_ENGIN_1.duty_u16(0)
R_ENGIN_2 = PWM(Pin(15))
R_ENGIN_2.freq(1000)
R_ENGIN_2.duty_u16(0)

L_ENGIN_1 = PWM(Pin(16))
L_ENGIN_1.freq(1000)
L_ENGIN_1.duty_u16(0)
L_ENGIN_2 = PWM(Pin(17))
L_ENGIN_2.freq(1000)
L_ENGIN_2.duty_u16(0)


## ENGINE FUNCTIONS
def MoveForward():
    R_ENGIN_2.duty_u16(0)
    L_ENGIN_2.duty_u16(0)
    R_ENGIN_1.duty_u16(65535)
    L_ENGIN_1.duty_u16(65535)
    sleep(0.2)

def MoveLeft():
    R_ENGIN_2.duty_u16(0)
    L_ENGIN_1.duty_u16(0)
    L_ENGIN_2.duty_u16(65535)
    R_ENGIN_1.duty_u16(65535)
    sleep(0.2)

def MoveRight():
    L_ENGIN_2.duty_u16(0)
    R_ENGIN_1.duty_u16(0)
    R_ENGIN_2.duty_u16(65535)
    L_ENGIN_1.duty_u16(65535)
    sleep(0.2)

def MoveBack():
    L_ENGIN_1.duty_u16(0)
    R_ENGIN_1.duty_u16(0)
    R_ENGIN_2.duty_u16(65535)
    L_ENGIN_2.duty_u16(65535)
    sleep(0.2)

# Network credentials
ssid = '983B67CCD665-2G'
password = '7f9ebg8rebprxa'

# Connect to WLAN
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

print('Connecting to network...')
wlan.connect(ssid, password)

# Wait for connect or fail
max_wait = 20
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print(f'waiting for connection... ({10 - max_wait}s)')
    if max_wait % 2 != 0:
        RED_LED.value(1)
    else:
        RED_LED.value(0)
    sleep(1)

# Handle connection error
if wlan.status() != 3:
    print('Network connection failed with status:', wlan.status())
    raise RuntimeError('network connection failed')
else:
    RED_LED.value(0)
    GREEN_LED.value(1)
    print('Connected')
    status = wlan.ifconfig()
    print('IP address:', status[0])

# HTML template
def read_html_template(file_path):
    with open(file_path, 'r') as file:
        return file.read()

html_index = """<!DOCTYPE html>
<html>
<head>
    <title>Arrow Buttons</title>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
        }
        .container {
            display: grid;
            grid-template-rows: repeat(3, 100px);
            grid-template-columns: repeat(3, 100px);
            gap: 10px;
        }
        .button {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 200px;
            height: 100px;
            background-color: #4CAF50;
            color: white;
            font-size: 24px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .button:active {
            background-color: #45a049;
        }
        .up {
            grid-row: 1 / 2;
            grid-column: 2 / 3;
        }
        .left {
            grid-row: 2 / 3;
            grid-column: 1 / 2;
        }
        .right {
            grid-row: 2 / 3;
            grid-column: 3 / 4;
        }
        .down {
            grid-row: 3 / 4;
            grid-column: 2 / 3;
        }
    </style>
    <script>
        function sendCommand(command) {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', '/' + command, true);
            xhr.send();
        }
    </script>
</head>
<body>
    <div class="container">
        <button class="button up" onmousedown="sendCommand('forward')" onmouseup="sendCommand('stop')"></button>
        <button class="button left" onmousedown="sendCommand('left')" onmouseup="sendCommand('stop')"></button>
        <button class="button right" onmousedown="sendCommand('right')" onmouseup="sendCommand('stop')"></button>
        <button class="button down" onmousedown="sendCommand('backward')" onmouseup="sendCommand('stop')"></button>
    </div>
</body>
</html>"""

# Open socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print('Listening on', addr)

# Listen for connections
while True:
    try:
        cl, addr = s.accept()
        print('client connected from', addr)
        request = cl.recv(1024)
        print("action:")
        request = str(request)
        command = request.split()[1][1:]
        print(command)


        if command == "stop":
            L_ENGIN_1.duty_u16(0)
            R_ENGIN_1.duty_u16(0)
            R_ENGIN_2.duty_u16(0)
            L_ENGIN_2.duty_u16(0)
        elif command == "forward":
            MoveForward()
            print("im driving")
        elif command == "left":
            MoveLeft()
            print("im lefting")
        elif command == "right":
            MoveRight()
            print("im righting")
        elif command == "backward":
            MoveBack()
            print("im backing")


        response = html_index
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()

    except OSError as e:
        cl.close()
        print('connection closed')
        R_ENGIN_1.deinit()
        R_ENGIN_2.deinit()
