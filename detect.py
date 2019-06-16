#!/usr/bin/python
# Lightning detection manager
# 27 May 2019

# do this to install mosquitto on Pi Zero computer
# sudo apt install mosquitto mosquitto-clients
# 
# pip install paho-mqtt

import pdb
import socket
import sys
from time import sleep
from datetime import datetime

import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt

import rules

debug = 0

if len(sys.argv) > 1:
   myStart = int(sys.argv[1])
else:
   myStart = 0

myLightning = 0
strikedelta = 0
arrStrikes = [0]
prob = 0

numSamples = 60/2  # 30 samples, 30 minutes

sameCnt = 0

testmode = 0

if testmode == 0:
   topic1 = "ha32163/lightning/strikes"
   topic2 = "ha32163/lightning/distance"
else:     
   topic1 = "ha32163/lightning/strikes/test"
   topic2 = "ha32163/lightning/distance/test"



hassHost = "192.168.2.6"

print("starting") 

PORT = 4700
srvName = "client-checkin"
myTimeout = 45.0

# for the watchdog function
def checkin():
    # create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = 'ha32163'
    port = 3008

    try:
       s.connect((host, port))
    except:
          if debug == 1:
            print('couldnt connect')
    else:        
       # Receive no more than 1024 bytes
       s.sendall(b'mysend')
       msg = s.recv(1024)
       s.close()
       if debug == 1:
         print (msg.decode('ascii'))


checkin()


################################################
def on_connect(client, userdata, rc, flags):
    print("Connected with result code "+str(rc))
    client.subscribe(topic1)
    print ("Subscribing to " + topic1)
    client.subscribe(topic2)
    print ("Subscribing to " + topic2)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global myLightning
    global stormDistance
    global arrStrikes
    global sameCnt
    global strikedelta
    global prob
    global numSamples
    global myStart
    
    print
    print datetime.now()
    print(msg.topic+" "+str(msg.payload))
    myPayload = msg.payload.decode('utf-8')
#    print("Payload= ", myPayload)

    if (msg.topic == topic2):
       stormDistance = int(myPayload)
       strikeevent = False
       print("Storm distance= " + str(stormDistance))

    if (msg.topic == topic1):
       myLightning = int(myPayload)
       strikeevent = True
       print("myLightning = " + str(myLightning)) 
       print("array length= " + str(len(arrStrikes)))
       print("mystart= " + str(myStart))

    if len(arrStrikes) == 1:
        if myStart < 0:
            arrStrikes = [(myLightning + myStart)] * 30      
            print(arrStrikes)
        else:
            arrStrikes = [(myLightning)] * 30
            print(arrStrikes)


    elif len(arrStrikes) < numSamples:
        arrStrikes.append((myLightning))
        print arrStrikes
        sameCnt = arrStrikes.count((myLightning))
        strikedelta = int(arrStrikes[-1]) - int(arrStrikes[0])
    else:
        if strikeevent:
           strikeevent = False
           arrStrikes[0:] = arrStrikes[1:]
           arrStrikes.append((myLightning))
           print(arrStrikes[:])
           sameCnt = arrStrikes.count((myLightning))
        # don't use 1 hour ago, use 20 minutes ago
        # now 30 minutes ago
           strikedelta = int(arrStrikes[-1]) - int(arrStrikes[0])
        # has strike counter rolled over?
           if strikedelta < 0:
              arrStrikes[0] = arrStrikes[-1] - 127
              strikedelta = int(arrStrikes[-1]) - int(arrStrikes[0])
        print("same strikes= " + str(sameCnt))
        print("strikedelta= " + str(strikedelta))
        print("stormdistance= " + str(stormDistance))


#          print type(sameCnt),type(strikedelta),type(stormDistance)

        prob = rules.myRules((strikedelta),(stormDistance))
                    
        print"Storm probability= " + str(prob)      
             
        try:

            if testmode == 0:
               publish.single("zero5/strikedelta" , strikedelta , hostname=hassHost, auth = {'username':"hass", 'password':"hass"})
               publish.single("zero5/stormprobability" , prob , hostname=hassHost, auth = {'username':"hass", 'password':"hass"})
        except:
             print("publish error encountered")

#pdb.set_trace()

######################################
client = mqtt.Client()
client.username_pw_set('hass', password='hass')
client.on_connect = on_connect
client.on_message = on_message

hassHost = "192.168.2.6"
ctr = 0
HOST = ''                # Symbolic name meaning all available interfaces
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
PORT = 4700

##########################
if testmode == 0:
   PORT = 4700
else:
   PORT = 4701
##########################
connected = 0
while connected == 0:
  try:
    s.bind((HOST, PORT))
    s.settimeout(45.0)
    s.listen(5)
    print "connected to port"
    connected = 1
  except:
    print "  Connection error, waiting..."
    sleep(5)

print "listening for " + srvName + " on port " + str(PORT) + " with timer = " + str(myTimeout)

timeouts = 0;
connects = 0;

#   client.loop_forever()
print("Connecting to HA")
client.connect_async(hassHost, 1883, 60)
client.loop_start()


oldmin =  datetime.now().minute

prob = 0
while True:

   if oldmin != datetime.now().minute:
     checkin()  # network watchdog
     oldmin =  datetime.now().minute

   try:
      conn, addr = s.accept()
   except KeyboardInterrupt:
      print('keyboard interrupt %s')
      conn.close()
      exit()
   except:
      # here if no connection
      timeouts += 1
      print('timeout ' + srvName )
   else:
    connects += 1
    myStr = 'Connection ' + str(ctr) + ' from ' + str(addr) + '(' + srvName + ') ' + str(timeouts) + "/" + str(connects)
    print myStr
    i = 1
    while i > 0:
      data = conn.recv(1024)
  
      if data=='reset':
         timeouts = 0
         connects = 0
         ctr = -1
         print data
     
      ctr += 1
  
      if data=='status': 

        conn.sendall('strikes ' + str(myLightning) + ' ' + str(strikedelta) 
           + ' ' + str(sameCnt) + ' ' + str(prob))


        # print "Length= " + str(len(arrStrikes))
        # print "Array " + str(arrStrikes)
        # print "mysameCnt " + str(sameCnt)
        # print "my matching " + str(arrStrikes.count(str(myLightning)))
        i = 0
      else:
        print ('Unknown request')  
        conn.sendall('Unknown request ' )
        i = 0
   

conn.close()
