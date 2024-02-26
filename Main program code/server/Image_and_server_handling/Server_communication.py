import socket
import threading
import time
import os

class Server_Communication():
    """
    Class for handling server communication between the two Pis.

    Args:
        queue (Queue): The global queue storing matched file names.

    Attributes:
        Server (socket.socket): The server socket for communication.
        p1_array (list): The array for recieved names from Pi 1.
        p2_array (list): The array for recieved names from Pi 2.
        match_position_p1 (int): The position of the match in Pi 1 array.
        match_position_p2 (int): The position of the match in Pi 2 array.

    Methods:
        Private:
        __matcher(self, array1, array2): Matches file names between two arrays.
        __clear_array(self, array, stop_point): Clears the array up to the specified stop point saving memory.
        __send_message(self, connection, address, message): Sends a message to the specified client.
        __recieve_message(self, connection, address): Receives a message from the specified client.
        __reconnect(self, connection, address): Closes the current connection and reconnects to the client only used when sockets fail.
        __Accept_connections(self): Accepts connections from two clients and starts separate threads for receiving/transmitting data from each pi.        
        __Matcher_loop(self, queue): Continuously checks for matches between p1_array and p2_array and adds matched file names to the global queue allowing them to be stitched.
        __Pi1_recieve(self, connection, address): Receives file names from the first client and adds them to p1_array while communicating back to allow for file transfer.
        __Pi2_recieve(self, connection, address): Receives file names from the second client and adds them to p2_array while communicating back to allow for file transfer.
    """

    def __init__(self, queue):
        host = socket.gethostname()
        port = 50000
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(2)
        self.Server = server
        self.p1_array = []
        self.p2_array = []
        self.match_position_p1 = 0
        self.match_position_p2 = 0
        self.__Accept_connections()
        self.__Matcher_loop(queue)

    def __Matcher_loop(self, queue):
        """
        Continuously checks for matches between p1_array and p2_array and adds matched file names to the queue.
        Also wipes the arrays if no match is found after a certain time to save memory.

        Args:
            queue (Queue): The queue storing matched file names.
        """

        timer = 0
        while True:
            time.sleep(0.2)
            if len(self.p1_array) != 0 and len(self.p2_array) != 0:
                time.sleep(0.5)
                if self.__matcher(self.p1_array, self.p2_array):
                    file_name = self.p1_array.pop(self.match_position_p1)
                    self.p2_array.pop(self.match_position_p2)
                    if file_name == "":
                        continue
                    queue.put(file_name)
                    if timer > 6000 and self.match_position_p1 != 0 and self.match_position_p2 != 0:
                        self.__clear_array(self.p1_array, self.match_position_p1)
                        self.__clear_array(self.p2_array, self.match_position_p2)
                        timer = 0
            timer += 1

    def __matcher(self, array1, array2):
        """
        Matches file names between two arrays.

        Args:
            array1 (list): The first array of file names.
            array2 (list): The second array of file names.

        Returns:
            bool: True if a match is found, False otherwise.
        """

        self.match_position_p1 = 0
        self.match_position_p2 = 0
        for i in range(len(array1)):
            for j in range(len(array2)):
                if array1[i] == array2[j]:
                    self.match_position_p1 = i
                    self.match_position_p2 = j
                    return True

    def __clear_array(self, array, stop_point):
        """
        Clears the array up to the specified stop point.

        Args:
            array (list): The array to be cleared.
            stop_point (int): The index to stop clearing the array.
        """

        for counter in range(len(stop_point - 1)):
            try:
                os.remove(array.pop()[:-4] + "L.jpg")
            except:
                pass
            try:
                os.remove(array.pop()[:-4] + "R.jpg")
            except:
                pass

    def __Accept_connections(self):
        """
        Accepts connections from two clients and starts separate threads for receiving data from each client.
        """

        Client = self.Server.accept()
        x = threading.Thread(target=self.__Pi1_recieve, args=(Client))
        x.start()
        time.sleep(0.1)
        Client2 = self.Server.accept()
        y = threading.Thread(target=self.__Pi2_recieve, args=(Client2))
        y.start()

    def __send_message(self, connection, address, message):
        """
        Sends a message to the specified client.

        Args:
            connection (socket): The connection to the client.
            address (str): The address of the client.
            message (str): The message to be sent.

        Returns:
            bool: True if the message is sent successfully, False otherwise.
        """

        try:
            connection.sendall(message.encode('ascii'))
            return True
        except Exception as Error:
            print(Error)
            # self.__reconnect(connection, address)
            return False

    def __recieve_message(self, connection, address):
        """
        Receives a message from the specified client.

        Args:
            connection (socket): The connection to the client.
            address (str): The address of the client.

        Returns:
            str: The received message.
        """

        try:
            data = connection.recv(4096)
            return data.decode('ascii')
        except Exception as Error:
            print(Error)
            # self.__reconnect(connection, address)
            return False

    def __reconnect(self, connection, address):
        """
        Closes the current connection and reconnects to the client.

        Args:
            connection (socket): The current connection to be closed.
            address (str): The address of the client.

        Returns:
            tuple: The new connection and address.
        """

        connection.close()
        connection, address = self.Server.accept()
        return connection, address

    def __Pi1_recieve(self, connection, address):
        """
        Receives file names from the first client and adds them to p1_array then responds to send file via FTP.

        Args:
            connection (socket): The connection to the first client.
            address (str): The address of the first client.
        """

        past_name = ""
        while True:
            match name := self.__recieve_message(connection, address):
                case False:
                    continue
                case "":
                    continue
                case _ if past_name == name:
                    self.__send_message(connection, address, "0")
                    continue
            if self.__send_message(connection, address, "1"):
                self.p1_array.append(name)
                past_name = name
                continue
            self.__send_message(connection, address, "0")

    def __Pi2_recieve(self, connection, address):
        """
        Receives file names from the second client and adds them to p2_array then responds to send file via FTP..

        Args:
            connection (socket): The connection to the second client.
            address (str): The address of the second client.
        """
        
        past_name = ""
        while True:
            match name := self.__recieve_message(connection, address):
                case False:
                    continue
                case "":
                    continue
                case _ if past_name == name:
                    self.__send_message(connection, address, "0")
                    continue
            if self.__send_message(connection, address, "1"):
                self.p2_array.append(name)
                past_name = name
                continue
            self.__send_message(connection, address, "0")
