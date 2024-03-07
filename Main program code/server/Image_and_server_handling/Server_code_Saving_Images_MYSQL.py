import mysql.connector
import datetime
from Image_and_server_handling.Ai_handling import Ai
import numpy as np



class sql_server_image_handling():
    """
    Class for SQL image handling.

    Args:
        None

    Attributes:
        Password (str): The password for MySQL server.
        Ai (Ai): An instance of the Ai class for object detection.
        Connector (mysql.connector.connect): The connection to the MySQL server.

    Methods:
        Private:
        __connect(): Connects to the MySQL server.
        __update_movement(image_location, image_name, date, hour, minutes_seconds): Updates the movement table in the database.

        Public:
        save_images(name, file_location): Saves the image to the database.
    """
    
    def __init__(self):
        self.__Password = "rabbit42!"
        self.Ai = Ai()
        self.__connect()
        
    def __connect(self):
        """
        Connects to the MySQL server.
        """
        
        try:
            self.Connector = mysql.connector.connect(user="root", password=self.__Password, host="localhost", database="RabbitHealth")
        except Exception as Error:
            print(Error)

    def __update_movement(self, image_location, image_name, date, hour, minutes_seconds):
        """
        Updates the movement table in the database with the image details.

        Args:
            image_location (str): The location of the image.
            image_name (str): The name of the image.
            date (datetime.date): The date of the image time taken.
            hour (datetime.time): The hour of the image time taken.
            minutes_seconds (datetime.time): The minutes and seconds of when the image was taken.
        """

        Cinny_xyxy, Cleo_xyxy, human = self.Ai.find_rabbits(image_location)
        Cinny_xyxy = np.split(Cinny_xyxy, 2)
        Cinny_x = (Cinny_xyxy[0][0] + Cinny_xyxy[1][0]) // 2
        Cinny_y = (Cinny_xyxy[0][1] + Cinny_xyxy[1][1]) // 2
        Cleo_xyxy = np.split(Cleo_xyxy, 2)
        Cleo_x = (Cleo_xyxy[0][0] + Cleo_xyxy[1][0]) // 2
        Cleo_y = (Cleo_xyxy[0][1] + Cleo_xyxy[1][1]) // 2
        if 0 <= Cinny_x <= 4922 or 0 <= Cinny_y <= 2110 or 0 <= Cleo_x <= 4922 or 0 <= Cleo_y <= 2110:
            pass
        else:
            raise "Incorrect coordinates from AI"
        date = date.strftime("%Y-%m-%d")
        hour = hour.strftime("%H:%M:%S")
        minutes_seconds = minutes_seconds.strftime("%H:%M:%S")
        if human == True:
            person = 1
        else:
            person = 0
        statement = "INSERT INTO Movement (Date, Hour, Minutes_Seconds, Pet1_X_Coord, Pet1_Y_Coord, Pet2_X_Coord, Pet2_Y_Coord, Image_Name, Person) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (date, hour, minutes_seconds, Cinny_x.item(), Cinny_y.item(), Cleo_x.item(), Cleo_y.item(), image_name, person,)
        Cursor = self.Connector.cursor()
        Cursor.execute(statement, values)
        self.Connector.commit()
        Cursor.close()

    def save_images(self, name, file_location):
        """
        Saves the image details to the database.

        Args:
            name (str): The name of the image.
            file_location (str): The location of the image.
        """

        Cursor = self.Connector.cursor()
        statement = "INSERT INTO image_storage (Image_Name, File_Location, File_Exists) VALUES (%s, %s, %s)"
        values = (name, file_location, 1,)
        Cursor.execute(statement, values)
        self.Connector.commit()
        Cursor.close()
        temp_name = name
        temp_name = temp_name.split("_")
        time = temp_name[0].split("-")
        date = temp_name[1]
        date = date.split("-")
        date = datetime.date(int(date[0]), int(date[1]), int(date[2]))
        hour = datetime.time(int(time[0]), 0, 0)
        minutes_seconds = datetime.time(0, int(time[1]), int(time[2]))
        self.__update_movement(file_location, name, date, hour, minutes_seconds)
