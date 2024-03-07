from picamera2 import Picamera2
import time
import socket
import multiprocessing
import concurrent.futures
import ftplib
import os



class camera():
    """
    Camera object for capturing images in a constant time.

    Args:
        None

    Attributes:
        picam: An instance of the Picamera2 class.
        time_between_pic: The time interval between capturing images.
        Queue: A multiprocessing Queue for storing captured image names.

    Methods:
        Public:
        Capture_timer: Captures images at regular intervals based on the time_between_pic attribute.
        image_capture: Captures an image and adds its name to the Queue.
    """

    def __init__(self):
        """
        Creates an instance of Picamera2 and configures settings.
        Starts the camera and timer.
        """
        self.picam = Picamera2()
        config = self.picam.create_still_configuration(main={"size": (2592, 1944)})
        self.picam.configure(config)
        self.picam.options["quality"] = 20
        self.picam.start()
        temp_timer = 60 - int(time.strftime("%S", time.localtime()))
        time.sleep(temp_timer)
        self.__Past_Time = 0
        self.Capture_timer()

    def Capture_timer(self):
        """
        Captures images at regular intervals based on the time_between_pic.
        """
        while True:
            time.sleep(0.2)
            Current_Time = time.strftime("%S", time.localtime())
            Current_Time = int(Current_Time) % self.time_between_pic
            if self.__Past_Time == Current_Time:
                self.__Past_Time = Current_Time
                self.image_capture()
                time.sleep(self.time_between_pic / 2)

    def image_capture(self):
        """
        Captures an image and adds its name to the Queue.
        """
        name = time.strftime("%H-%M-%S_%F", time.localtime()) + ".jpg"
        self.picam.capture_file(name)
        self.Queue.put(name)

class network():
    """
    Represents a network object for handling FTP and socket connections.

    Args:
        None

    Attributes:
        ftp: An instance of the FTP_TLS class for FTP connections.
        server: A socket object for socket connections.
        Queue: A multiprocessing Queue for storing image names.

    Methods:
        Public:
        move_image: Moves an image to the FTP server.
        ping: Pings the server for image transfer.

        Private:
        __ftp_connect: Connects to the FTP server.
        __ftp_move_image: Moves an image to the FTP server.
        __failed_ftp: Handles failed FTP connections.
        __socket_connect: Connects to the socket server.
        __recovery: Recovers image names from the local directory.
        __send: Sends a message to the server.
        __recieve: Receives a message from the server.
        __failed_socket: Handles failed socket connections.
    """

    def __init__(self):
        """
        Connects to the FTP server, socket server.
        Sets up regular communication with the server for image transfer.
        """
        self.ftp = ftplib.FTP_TLS()
        self.__ftp_connect()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)     
        self.__socket_connect()
        self.ping()

    def __ftp_connect(self):
        """
        Connects to the FTP server.
        """
        try:
            self.ftp.connect("192.168.137.1", 21)
            self.ftp.login("RabbitServer", "CinnyCleo1000")
            self.ftp.prot_p()
        except Exception as Error:
            print(Error, "\n   Error in FTP connecting")

    def move_image(self, name):
        """
        Preps image for move to the FTP server.

        Args:
            name (str): The filename of the image to move
        """
        image = open(name, "rb")
        name = name[:-4] + "L.jpg"
        print(name)
        try:
            self.__ftp_move_image(name, image)
        except Exception as Error:
            self.__failed_ftp(Error)

    def __ftp_move_image(self,name,image):
        """
        Moves an image to the FTP server.

        Args:
            name (str): The filename of the image to send to FTP
            image (PIL.Image): The image file being sent
        """
        self.ftp.storbinary("STOR " + name, image, 524288)
        name = name[:-5] + ".jpg"
        os.remove(name)           

    def __failed_ftp(self, Error):
        """
        Handles failed FTP connections by attempting to reconnect to the FTP server.
        If reconnection fails, adds the image back to the Queue.

        Args:
            Error: The exception that occurred during the FTP connection.
        """
        print(Error)
        print("Failed to send")
        print("Attempting to reconnect to FTP server")
        try:
            self.__ftp_connect()
            print("Reconnected to FTP server")
        except Exception as Error:
            print(Error)
            print("Failed to reconnect to FTP server")
            name = name[:-5] + ".jpg"
            self.Queue.put(name)

    def __socket_connect(self):
        """
        Connects to the socket server.
        """
        try:
            host = "192.168.137.1"  # Server IP
            port = 50000  # Server port
            self.server.connect((host, port))
        except Exception as Error:
            print(Error, "\n   Error in socket connecting")

    def __recovery(self):
        """
        Retrieves all image files in the local directory feeding them back to the queue.

        Returns:
            list: A list of image files which are the local directory waiting to be sent.
        """
        Queue = []
        files = os.listdir()
        for file in files:
            if file.endswith(".jpg"):
                Queue.append(file)
        return Queue

    def ping(self):
        """
        Takes image names from global Queue and sends them to the server.
        If the server responds to the text, it is moved to the FTP server.
        """
        try:
            Local_Queue = self.__recovery()
        except Exception as Error:
            print(Error)
            Local_Queue = []
        while True:
            time.sleep(1)
            if self.Queue.empty() == False:
                Local_Queue.append(self.Queue.get())
            if len(Local_Queue) != 0:
                name = Local_Queue[0]
                if self.__send(name) == False:
                    continue
                if self.__recieve() == "1":
                    concurrent.futures.ThreadPoolExecutor().submit(self.move_image, name=Local_Queue.pop(0))
                elif self.__recieve() == "0":
                    print("Bad image")
                    name = Local_Queue.pop(0)
                    print(name, " removed")
                    os.remove(name + ".jpg")

    def __send(self, message):
        """
        Sends a message to the server.
        
        Returns:
            bool: True if successful on send, False otherwise.
        """
        try:
            self.server.sendall(message.encode("ascii"))
            return True
        except Exception as Error:
            self.__failed_socket(Error)
            return False

    def __recieve(self):
        """
        Receives a message from the server.
        
        Returns:
            str: The message recieved or a 0 if socket fails connection.
        """
        try:
            received = self.server.recv(4096)
            received = received.decode("ascii")
            return received
        except Exception as Error:
            self.__failed_socket(Error)
            return "0"

    def __failed_socket(self,Error):
        """
        Handles failed socket connections by attempting to reconnect.
        If reconnection fails, adds the image back to the Queue.

        Args:
            Error: The exception that occurred during the socket connection.
        """
        print(Error)
        print("Failed to send")
        print("Attempting to reconnect to socket")
        try:
            self.__socket_connect()
            print("Reconnected to socket")
        except Exception as Error:
            print(Error)
            print("Failed to reconnect to socket")

class main(camera, network):
    """
    Represents the main program for capturing and transferring images.
    Inherits from the camera and network classes to join them together.
    """
    def __init__(self):
        """
        Sets the time interval between capturing images and starts the rest of the program on seperate cores.
        """
        self.time_between_pic = 2
        self.Queue = multiprocessing.Queue()
        Network = multiprocessing.Process(target=network.__init__, args=(self,)) 
        Network.start()
        camera.__init__(self)
        
if __name__=="__main__": # starts the program
    main()