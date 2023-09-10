#Task have some way to get the messages from both clients then compare names and work out how to splice images together
#**Then add entry to MYSQL database of that name** -phase two - *add to queue to run into tensorflow* - seperate class phase 3
#upgrade to automata down the line along with making into classes
import socket
import threading
import time
import os
import multiprocessing
from server_code_splicing import stitch

class Server_Communication():
    def __init__(self):
        host=socket.gethostname()
        port=50000
        server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host,port))
        server.listen(2)
        self.server=server
        self.MyEvent=threading.Event()

    def accept_connections(self):
        Client=self.Server.accept()
        x=threading.Thread(target=Pi1_recieve, args=(self.MyEvent,Client)) 
        x.start()
        time.sleep(0.1)
        Client=self.Server.accept()
        y=threading.Thread(target=Pi2_recieve, args=(self.MyEvent,Client)) 
        y.start()


    def Pi1_recieve(event,connection):
        global File_Names
        while True:
            data=connection.recv(1024)
            name=data.decode('ascii')
            File_Names[0]=name
            event.wait()
            time.sleep(0.01)
            connection.sendall(data)

    def Pi2_recieve(event,connection):
        global File_Names
        while True:
            data=connection.recv(1024)
            name=data.decode('ascii')
            File_Names[1]=name
            event.wait()
            time.sleep(0.01)
            connection.sendall(data)
#multiprocessed - could be in the stitching code file
def stitch(queue):
    stitcher=stitch()
    while True:
        local_queue=queue.get()
        if len(local_queue)!=0:
            name=local_queue.pop(0)
            nameL=name+"L.jpg"
            nameR=name+"R.jpg"
            name="..\\Stitched images" + name + ".jpg"
            stitcher.stitch_and_save(nameL,nameR,name)
            os.remove(nameL)
            os.remove(nameR)


if __name__=="__main__":
    x=Server_Communication()
    time.sleep(1)
    x.accept_connections()
    File_Names=["",""]
    timer=0
    queue=multiprocessing.Queue()
    stitching=multiprocessing.Process(target=stitch, args=(queue,))
    stitching.start()
    while True:
        time.sleep(0.1)
        timer+=1
        if File_Names[0]==File_Names[1]!=Past_Name: #risk of error if raspberry pis get out of sync
            timer=0
            Past_Name=File_Names[0]
            threading.Event.set()
            time.sleep(0.01)
            x.MyEvent.clear()
            queue.put(Past_Name)
        if timer==500:
            pass
            #send an email