# lightning
Programs to read Acurite Lightning sensor data and transmit an opinion about the likelihood of a close-by lightning strike.

detect.py:
   The main decision making program. Copy to detect-test.py and edeit the testmode flag to do parallel testing.
   
rules.py:
   Thresholds as currently calculated.

## testing subsystem:
These should be in a separate folder.

MQTTRecorder:
   This program will record MQTT transmissions from the HA server and store them in a database.  You can record a real lightning storm event (max two hours real time) and record the data in a SQLite database.
   
MQTTPlayer:
    Program will replay a storm event.  A command line parameter selects which storm from the database.
    
run_test:
   A shell script to replay multiple recordings from the database.
   
events.sql:
   A database dump of a storm event
   
## client software
