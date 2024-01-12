import socket
import threading
import time

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