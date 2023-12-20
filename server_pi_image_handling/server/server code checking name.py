#Task have some way to get the messages from both clients then compare names and work out how to splice images together
#**Then add entry to MYSQL database of that name** -phase two - *add to queue to run into tensorflow* - seperate class phase 3
#upgrade to automata down the line along with making into classes
import socket
import threading
import time
import os
import multiprocessing
from server_code_splicing import stitch
from Server_code_MYSQL import sql_server_handling
from getpass import getpass

class Server_Communication():
    def __init__(self):
        host=socket.gethostname()
        port=50000
        server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host,port))
        server.listen(2)
        self.Server=server
        self.MyEvent=threading.Event()

    def accept_connections(self):
        Client=self.Server.accept()
        x=threading.Thread(target=self.Pi1_recieve, args=(Client)) 
        x.start()
        time.sleep(0.1)
        Client2=self.Server.accept()
        y=threading.Thread(target=self.Pi2_recieve, args=(Client2)) 
        y.start()


    def Pi1_recieve(self,connection,address):
        global File_Names
        while True:
            data=connection.recv(4096)
            name=data.decode('ascii')
            File_Names[0]=name
            self.MyEvent.wait()
            time.sleep(0.01)
            connection.sendall(data)

    def Pi2_recieve(self,connection,address):
        global File_Names
        while True:
            data=connection.recv(4096)
            name=data.decode('ascii')
            File_Names[1]=name
            self.MyEvent.wait()
            time.sleep(0.01)
            connection.sendall(data)
#multiprocessed - could be in the stitching code file
def stitchs(queue,password):
    stitcher=stitch()
    SQL=sql_server_handling(password)
    SQL.connect()
    local_queue=[]
    fail=0
    while True:
        local_queue.append(queue.get())
        if len(local_queue)!=0:
            name=local_queue.pop(0)
            name=name[:-4]
            nameL="Recived_images\\"+ name +"L.jpg"
            nameR="Recived_images\\"+ name +"R.jpg"
            file_name="Stitched_images\\" + name + ".jpg"
            time.sleep(0.5)
            try:
                stitcher.stitch_and_save(nameL,nameR,file_name)
            except:
                time.sleep(10)
                try:
                    stitcher.stitch_and_save(nameL,nameR,file_name)
                except:
                    fail=fail+1
                    print("failed stitch ", fail," times")
                    local_queue.append(name)
                else:
                    os.remove(nameL)
                    os.remove(nameR)
                    save(SQL,name,file_name)
            else:
                os.remove(nameL)
                os.remove(nameR)
                save(SQL,name,file_name)

def save(SQL,name,file_name):
    SQL.save_images(name,file_name)

if __name__=="__main__":
    x=Server_Communication()
    password=getpass()
    time.sleep(1)
    x.accept_connections()
    File_Names=["",""]
    timer=0
    queue=multiprocessing.Queue()
    stitching=multiprocessing.Process(target=stitchs, args=(queue,password,))
    stitching.start()
    Past_Name=""
    while True:
        time.sleep(0.1)
        timer+=1
        if File_Names[0]==File_Names[1]!=Past_Name: #risk of error if raspberry pis get out of sync
            print(File_Names[0])
            timer=0
            Past_Name=File_Names[0]
            x.MyEvent.set()
            time.sleep(0.01)
            x.MyEvent.clear()
            queue.put(Past_Name)
        if timer==500:
            pass
            #send an email