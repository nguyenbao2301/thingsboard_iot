print("IoT Gateway")
import paho.mqtt.client as mqttclient
import time
import json
import serial.tools.list_ports

BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
mess = ""

#TODO: Add your token and your comport
#Please check the comport in the device manager
THINGS_BOARD_ACCESS_TOKEN = "vQMcTxV3eOJG6fjvnuIH"

def getPort():
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    bbc_port = ""
    for i in range(0,N):
        port = ports[i]
        s = str(port)
        if "USB Serial Device" in s:
            s = s.split(" ")
            bbc_port = s[0]
    return bbc_port

bbc_port = getPort()

if len(bbc_port) > 0:
    try: 
        ser = serial.Serial(port=bbc_port, baudrate=115200)
    except Exception:
        ser = None

def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    # print(splitData)
    #TODO: Add your source code to publish data to the server
    if splitData[1] in ["temp","light"]:
        key = "temperature" if splitData[1] == "temp" else "light" #set key
        z = {key: splitData[2]}  #pack to form {key: value}
        payload = json.dumps(dict(z)) # to json
        # print(payload)
        client.publish('v1/devices/me/telemetry', payload, 1)

def readSerial():
    bytesToRead = ser.inWaiting()
    if (bytesToRead > 0):
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start:end + 1])
            if (end == len(mess)):
                mess = ""
            else:
                mess = mess[end+1:]


def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")

def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))
    temp_data = {'value': True}
    cmd = -1
    #TODO: Update the cmd to control 2 devices
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setLed":
            temp_data['value'] = jsonobj['params']
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
            cmd = 0 if jsonobj['params'] else 1
        elif jsonobj['method'] == "setFan":
            temp_data['value'] = jsonobj['params']
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
            cmd = 2 if jsonobj['params'] else 3
        else:
            cmd= -1
    except:
        pass

    if len(bbc_port) > 0:
        ser.write((str(cmd) + "#").encode())

def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection is failed")


client = mqttclient.Client("Gateway_Thingsboard")
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message


while True:

    if len(bbc_port) >  0 and ser!= None:
        readSerial()

    time.sleep(1)