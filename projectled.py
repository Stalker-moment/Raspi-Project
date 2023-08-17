import RPi.GPIO as GPIO
import requests
import time
import threading
import drivers
from time import sleep

display = drivers.Lcd()

blynktoken = 'U8heNfW2a_j4PJMVev5QLEVtYtmfdSRF'
blynkserver = 'fra1.blynk.cloud'
VIRTUAL_MODE1 = 'V0'  
VIRTUAL_MODE2 = 'V1'  
VIRTUAL_MODE3 = 'V2'

valuev0 = 0
valuev1 = 0
valuev2 = 0

led1_pin = 2  
led2_pin = 3  

GPIO.setmode(GPIO.BCM)
GPIO.setup(led1_pin, GPIO.OUT)
GPIO.setup(led2_pin, GPIO.OUT)

stop_signalm11 = True
stop_signalm12 = True
stop_signalm21 = True
stop_signalm22 = True
stop_signalm31 = True
stop_signalm32 = True

def mode1():
    global stop_signalm11, stop_signalm12, stop_signalm21, stop_signalm22, stop_signalm31, stop_signalm32
    stop_signalm11 = False
    stop_signalm12 = False
    stop_signalm21 = True
    stop_signalm22 = True
    stop_signalm31 = True
    stop_signalm32 = True
    display.lcd_display_string("Index Mode :", 1)  # Write line of text to first line of display
    display.lcd_display_string("MODE 1", 2)  # Write line of text to second line of display
    
def mode2():
    global stop_signalm11, stop_signalm12, stop_signalm21, stop_signalm22, stop_signalm31, stop_signalm32
    stop_signalm11 = True
    stop_signalm12 = True
    stop_signalm21 = False
    stop_signalm22 = False
    stop_signalm31 = True
    stop_signalm22 = True
    display.lcd_display_string("Index Mode :", 1)  # Write line of text to first line of display
    display.lcd_display_string("MODE 2", 2)  # Write line of text to second line of display
    
def modeoff():
    global stop_signalm11, stop_signalm12, stop_signalm21, stop_signalm22, stop_signalm31, stop_signalm32
    stop_signalm11 = True
    stop_signalm12 = True
    stop_signalm21 = True
    stop_signalm22 = True
    stop_signalm31 = True
    stop_signalm32 = True
    display.lcd_display_string("Index Mode :", 1)  # Write line of text to first line of display
    display.lcd_display_string("MODE OFF", 2)  # Write line of text to second line of display
    
def mode3():
    global stop_signalm11, stop_signalm12, stop_signalm21, stop_signalm22, stop_signalm31, stop_signalm32
    stop_signalm11 = True
    stop_signalm12 = True
    stop_signalm21 = True
    stop_signalm22 = True
    stop_signalm31 = False
    stop_signalm32 = False
    display.lcd_display_string("Index Mode :", 1)  # Write line of text to first line of display
    display.lcd_display_string("MODE 3", 2)  # Write line of text to second line of display
    
    
def led1_thread():
    global stop_signalm11
    while not stop_signalm11:
        GPIO.output(led1_pin, GPIO.HIGH)
        time.sleep(2)  
        GPIO.output(led1_pin, GPIO.LOW)
        time.sleep(2)

def led2_thread():
    global stop_signalm12
    while not stop_signalm12:
        GPIO.output(led2_pin, GPIO.HIGH)
        time.sleep(2)  
        GPIO.output(led2_pin, GPIO.LOW)
        time.sleep(2)
        
def led1_thread2():
    global stop_signalm21
    while not stop_signalm21:
        GPIO.output(led1_pin, GPIO.HIGH)
        time.sleep(1)  
        GPIO.output(led1_pin, GPIO.LOW)
        time.sleep(1)

def led2_thread2():
    global stop_signalm22
    while not stop_signalm22:
        GPIO.output(led2_pin, GPIO.HIGH)
        time.sleep(0.5)  
        GPIO.output(led2_pin, GPIO.LOW)
        time.sleep(0.5)
        
def led1_thread3():
    global stop_signalm31
    while not stop_signalm31:
        GPIO.output(led1_pin, GPIO.HIGH)
        time.sleep(2)  
        GPIO.output(led1_pin, GPIO.LOW)
        time.sleep(2)

def led2_thread3():
    global stop_signalm32
    while not stop_signalm32:
        GPIO.output(led2_pin, GPIO.HIGH)
        time.sleep(0.2)  
        GPIO.output(led2_pin, GPIO.LOW)
        time.sleep(0.2)

def blynk_read():
    global valuev0, valuev1, valuev2
    url = f"https://{blynkserver}/external/api/get?token={blynktoken}&V0&V1&V2"
    response = requests.get(url)
    res = response.json()
    valuev0 = res['V0']
    valuev1 = res['V1']
    valuev2 = res['V2']
    #print(type(valuev1))
    print(res)

def blynk_write(pin, value):
    url = f"http://blynk-cloud.com/{BLYNK_AUTH}/update/{pin}?value={value}"
    requests.get(url)
    
activate_called = False

def activate():
    global activate_called
    if not activate_called:
        t1 = threading.Thread(target=led1_thread)
        t2 = threading.Thread(target=led2_thread)
        t3 = threading.Thread(target=led1_thread2)
        t4 = threading.Thread(target=led2_thread2)
        t5 = threading.Thread(target=led1_thread3)
        t6 = threading.Thread(target=led2_thread3)
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t5.start()
        t6.start()
        activate_called = True

try:
    while True:
        blynk_read()      
        if valuev0 == 1 and valuev1 == 0 and valuev2 == 0 :
            mode1()
            activate()
            print('mode1')
        elif valuev0 == 0 and valuev1 == 1 and valuev2 == 0:
            mode2()
            activate()
            print('mode2')
        elif valuev0 == 0 and valuev1 == 0 and valuev2 == 1:
            mode3()
            activate()
            print('mode3')
        else:
            modeoff()
            activate_called = False 
            print('modeoff')
        
        time.sleep(1)


except KeyboardInterrupt:
    GPIO.cleanup()
