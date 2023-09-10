#wil work on pi
from picamera2 import Picamera2
import time
import socket
import multiprocessing
import concurrent.futures
import RPi.GPIO as GPIO
from PIL import Image,ImageOps
import ftplib
import os

#setup
def setup():
    global picam,Past_Time,ftp
    picam=Picamera2()
    config=picam.create_still_configuration(main={"size": (2592, 1944)})
    picam.configure(config)
    '''picam.start_preview(None)'''
    picam.options["quality"] = 20
    picam.start()
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(18,GPIO.OUT)
    ftp=ftplib.FTP_TLS()
    try:
        ftp.connect("192.168.137.1",21)
        ftp.login("RabbitServer","CinnyCleo1000")
        ftp.prot_p()
    except:
        raise ValueError("FTP server is not able to be contacted")
    temp_timer=60-int(time.strftime("%S",time.localtime()))
    time.sleep(temp_timer)
    Past_Time=int(time.strftime("%S",time.localtime()))%10

def get_time(Queue):
    global Past_Time
    while True:
        time.sleep(0.2)
        Current_Time=time.strftime("%S",time.localtime())
        Current_Time=int(Current_Time)%10
        if Past_Time==Current_Time:
            Past_Time=Current_Time
            image_capture(Queue)
            time.sleep(5)
    
def image_capture(Queue):
    name=time.strftime("%H-%M-%S_%F",time.localtime()) +".jpg"
    picam.capture_file(name)
    Queue.put(name)


#Networking - multiprocess
def move_image(name):
    global ftp
    image_r=Image.open(name)
    image_r=ImageOps.flip(image_r)
    image_r=ImageOps.mirror(image_r)
    image_r=image_r.save(name)
    image=open(name,"rb")
    name=name[:-4]+"R.jpg"
    print(name)
    try:
        ftp.storbinary("STOR "+name,image,524288)
        name=name[:-5]+".jpg"
        os.remove(name)
    except:
        try:
            ftp.connect("192.168.137.1",21)
            ftp.login("RabbitServer","CinnyCleo1000")
            ftp.prot_p()
        except:
            pass
        name=name[:-5]+".jpg"
        Queue.put(name)
        pass
    #add row on mySQL with location and file name - server should deal with this when it recives name

def ping(Queue):
    '''host='192.168.1.25' # Server IP
    port=50000 #Server port
    server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)'''
    Local_Queue=[]
    '''try:
        server.connect((host,port))
    except:
        #GPIO.output(18,GPIO.HIGH)
        pass'''
    while True:
        time.sleep(0.1)
        try:
            Local_Queue.append(Queue.get())
        except:
            time.sleep(1)
        if len(Local_Queue)!=0:
            name=Local_Queue[0]
            concurrent.futures.ThreadPoolExecutor().submit(move_image,name=Local_Queue.pop(0))
            '''server.send(name.encode('ascii'))
            if server.recv(1024).decode('ascii')==name:
                concurrent.futures.ThreadPoolExecutor().submit(move_image,name=Local_Queue.pop(0))
            else:
                server.close()
                time.sleep(1)
                try:
                    server.connect((host,port))
                except:
                    #GPIO.output(18,GPIO.HIGH)
                    pass
        else:
            time.sleep(0.5)'''




if __name__=="__main__":
    setup()
    Queue=multiprocessing.Queue()#Declares shared memory
    Network=multiprocessing.Process(target=ping,args=(Queue,)) 
    Network.start()
    get_time(Queue)
        

#make name into an array?