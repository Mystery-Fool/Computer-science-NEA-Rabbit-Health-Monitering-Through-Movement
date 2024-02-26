import mysql.connector
import os
import datetime
from vector_handling import vectors
import time
from Gif_creation import create_gif



class sql_server_handling():
    """
    Class for handling SQL server operations.

    Args:
        None

    Attributes:
        __Password (str): The password for the MySQL server.
        __Connector (mysql.connector.connect): The connection to the MySQL server.
        __Gif_creator (create_gif): An instance of the create_gif class.
        __time_between_movements (int): The time between movements in microseconds.

    Methods:
        Private:
        __connect: Connects to the MySQL server.
        __collect_missing_data: Collects missing data from movement and inputs it into Hour and Daily.
        __automate_SQL_db_updates: Automates SQL database updates.
        __checker: Checks if the given date and hour have completed processing.
        __find_distance_and_avg_time: Finds the distance and average time moving for two rabbits.
        __Sum: Used in __find_distance_and_avg_time to calculate distance and average time for each object
        __update_hourly_movement: Updates the hourly movement table in the database.
        __update_daily_movement: Updates the daily movement table in the database.
        __make_gif: Creates a GIF from the given day and saves it to the specified location.
        __remove_images_day: Removes images from the given day.

        Public:
        None
    """
    
    def __init__(self):
        self.__Password = "rabbit42!"
        self.__Gif_creator = create_gif()
        self.__time_between_movements = 2000000  # in microseconds as mysql set up for integers
        self.__connect()
        self.__collect_missing_data()
        self.__automate_SQL_db_updates()

    def __connect(self):
        """
        Connects to the MySQL server.
        """
        try:
            self.Connector = mysql.connector.connect(user="root", password=self.__Password, host="localhost", database="RabbitHealth")
        except Exception as Error:
            print(Error)

    def __collect_missing_data(self):
        """
        Collects missing data from the SQL server.
        """
        hour_statement = "SELECT Movement.Date, Movement.Hour FROM Movement LEFT JOIN Hourly_Movement ON Movement.Date=Hourly_Movement.Date AND Movement.Hour=Hourly_Movement.Hour WHERE Hourly_Movement.Date IS NULL"
        date_statement = "SELECT Movement.Date FROM Movement LEFT JOIN Daily_Movement ON Daily_Movement.Date=Movement.Date WHERE Daily_Movement.Date IS NULL"
        Cursor = self.Connector.cursor()
        Cursor.execute(hour_statement)
        Past_Time = time.strftime("%H", time.localtime())
        hour = datetime.timedelta(hours=int(Past_Time))
        date = datetime.date.today()
        Hours = Cursor.fetchall()
        Hours = set(Hours)
        Hours = list(Hours)
        for row in Hours:
            if row[1] == hour and row[0] == date:
                continue
            try:
                self.__update_hourly_movement(row[0], row[1])
            except:
                pass
        Cursor.execute(date_statement)
        dates = Cursor.fetchall()
        self.days_running = 0
        dates = set(dates)
        dates = list(dates)
        for row in dates:
            if row[0] == datetime.date.today():
                continue
            self.days_running += 1
            if self.days_running > 2:
                temp_date = row[0] - datetime.timedelta(days=3)
                self.__remove_images_day(temp_date)
            try:
                self.__update_daily_movement(row[0])
                self.__make_gif(row[0])
            except:
                pass

    def __automate_SQL_db_updates(self):
        """
        Automates SQL database updates running onces an hour and once a day.
        """
        Time = int(time.strftime("%H", time.localtime()))
        date = datetime.date.today()
        check = False
        while True:
            if self.__checker(date, datetime.time(Time, 0, 0)):
                time.sleep(60) # delay to make sure information is finished processing
                self.__connect()
                hour = datetime.time(Time, 0, 0)
                if Time == 0 and check == False:
                    check = True
                    Time+=1
                    continue
                if Time == 23:
                    check = False
                self.__update_hourly_movement(date, hour)
                if Time == 0:
                    self.days_running += 1
                    self.__update_daily_movement(date)
                    self.__make_gif(date)
                    date = datetime.date.today()
                    if self.days_running > 2:
                        temp_date = date - datetime.timedelta(days=3)
                        self.__remove_images_day(temp_date)
                Time = (Time + 1) % 24
            else:
                time.sleep(10 * 60) # 10 minutes

    def __checker(self, date, hour):
        """
        Checks if the given date and hour have completed processing.

        Args:
            date (datetime.date): The date to check.
            hour (datetime.time): The hour to check.

        Returns:
            bool: True if the processing is completed, False otherwise.
        """
        self.__connect()
        statement = "SELECT Image_Name FROM Movement WHERE Date=%s AND Hour=%s AND Minutes_Seconds>%s"
        values = (date, hour, datetime.time(0, 59, 0),)
        Cursor = self.Connector.cursor()
        Cursor.execute(statement, values)
        general = Cursor.fetchall()
        Cursor.close()
        if len(general) != 0:
            return True
        else:
            return False

    def __find_distance_and_avg_time(self, Pet1_X_Coords, Pet1_Y_Coords, Pet2_X_Coords, Pet2_Y_Coords): # probably break into two functions
        """
        Finds the average distance and average time moving for two rabbits.

        Args:
            Pet1_X_Coords (list): List of X coordinates for rabbit 1.
            Pet1_Y_Coords (list): List of Y coordinates for rabbit 1.
            Pet2_X_Coords (list): List of X coordinates for rabbit 2.
            Pet2_Y_Coords (list): List of Y coordinates for rabbit 2.

        Returns:
            tuple: A tuple containing the average distance and average time moving for rabbit 1 and rabbit 2.
        """
        pet1_avg_distance, pet1_avg_time_moving = self.__Sum(Pet1_X_Coords,Pet1_Y_Coords)
        pet2_avg_distance, pet2_avg_time_moving = self.__Sum(Pet2_X_Coords,Pet2_Y_Coords)
        return pet1_avg_distance, pet1_avg_time_moving, pet2_avg_distance, pet2_avg_time_moving
    
    def __Sum(self, X_Coords, Y_Coords):
        """
        Finds the average distance and average time moving one object.

        Args:
            X_Coords (list): List of X coordinates for object.
            Y_Coords (list): List of Y coordinates for object.

        Returns:
            tuple: A tuple containing the average distance and average time moving for the object.
        """
        distance, time_moving = 0, 0
        Past_X_Coord, Past_Y_Coord = -1, -1
        counter = 1
        for iterator in range(len(X_Coords)):
            X_Coord, Y_Coord = X_Coords[iterator], Y_Coords[iterator]
            if X_Coord == Y_Coord == 0:
                continue
            elif Past_X_Coord == -1:
                Past_X_Coord = X_Coord
                Past_Y_Coord = Y_Coord
                continue
            else:
                counter += 1
                if X_Coord * 0.99 < Past_X_Coord < X_Coord * 1.01 and Y_Coord * 0.99 < Past_Y_Coord < Y_Coord * 1.01:  # rabbit moves a negligible amount-might be ai picking a slightly different midpoint therefore ignore
                    Past_X_Coord = X_Coord
                    Past_Y_Coord = Y_Coord
                else:
                    vectorx = abs(X_Coord - Past_X_Coord)
                    vectory = abs(Y_Coord - Past_Y_Coord)
                    distance += vectors.distance([vectorx, vectory])
                    Past_X_Coord = X_Coord
                    Past_Y_Coord = Y_Coord
                    time_moving += self.__time_between_movements
        avg_distance = distance // counter
        avg_time_moving = time_moving // counter
        return avg_distance, avg_time_moving

    def __update_hourly_movement(self, date, hour):
        """
        Updates the hourly movement table in the database based on the data in the movement table.

        Args:
            date (datetime.date): The date to update.
            hour (datetime.time): The hour to update.
        """
        print("updating hourly: ", date, "  ", hour)
        statement = "SELECT Pet1_X_Coord, Pet1_Y_Coord, Pet2_X_Coord, Pet2_Y_Coord FROM Movement WHERE Date=%s and Hour=%s"
        values = (date, hour,)
        Cursor = self.Connector.cursor()
        Cursor.execute(statement, values)
        Pet1_X_Coords, Pet1_Y_Coords, Pet2_X_Coords, Pet2_Y_Coords = [], [], [], [] # empty arrays to store the coordinates of the rabbits
        for row in Cursor.fetchall():
            Pet1_X_Coords.append(row[0])
            Pet1_Y_Coords.append(row[1])
            Pet2_X_Coords.append(row[2])
            Pet2_Y_Coords.append(row[3])
        pet1_d, pet1_t, pet2_d, pet2_t = self.__find_distance_and_avg_time(Pet1_X_Coords, Pet1_Y_Coords, Pet2_X_Coords, Pet2_Y_Coords)
        statement = "INSERT INTO Hourly_Movement (Date, Hour, Avg_Pet1_Time_Moving, Avg_Pet1_Magnitude_Movement_Pixel, Avg_Pet2_Time_Moving, Avg_Pet2_Magnitude_Movement_Pixel) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (date, hour, pet1_t, pet1_d, pet2_t, pet2_d,)
        Cursor.execute(statement, values)
        self.Connector.commit()
        Cursor.close()

    def __update_daily_movement(self, date):
        """
        Updates the daily movement table in the database based on the data in the hourly movement table.

        Args:
            date (datetime.date): The date to update.
        """
        print("updating daily: ", date)
        statement = "SELECT Avg_Pet1_Time_Moving, Avg_Pet1_Magnitude_Movement_Pixel, Avg_Pet2_Time_Moving, Avg_Pet2_Magnitude_Movement_Pixel FROM Hourly_Movement WHERE Date=%s"
        value = (date,)   
        Cursor = self.Connector.cursor()     
        Cursor.execute(statement, value)
        Avg_Pet1_Time_Moving_Day, Avg_Pet1_Magnitude_Movement_Pixel_Day, Avg_Pet2_Time_Moving_Day, Avg_Pet2_Magnitude_Movement_Pixel_Day = 0, 0, 0, 0
        for row in Cursor.fetchall():
            Avg_Pet1_Time_Moving_Day += row[0]
            Avg_Pet1_Magnitude_Movement_Pixel_Day += row[1]
            Avg_Pet2_Time_Moving_Day += row[2]
            Avg_Pet2_Magnitude_Movement_Pixel_Day += row[3]
        statement = "INSERT INTO Daily_Movement (Date, Avg_Pet1_Time_Moving, Avg_Pet1_Magnitude_Movement_Pixel, Avg_Pet2_Time_Moving, Avg_Pet2_Magnitude_Movement_Pixel) VALUES (%s, %s, %s, %s, %s)"
        values = (date, Avg_Pet1_Time_Moving_Day, Avg_Pet1_Magnitude_Movement_Pixel_Day, Avg_Pet2_Time_Moving_Day, Avg_Pet2_Magnitude_Movement_Pixel_Day,)
        Cursor.execute(statement, values)
        self.Connector.commit()
        Cursor.close()

    def __make_gif(self, date):
        """
        Retrieves file locations and human flag from the database for a given date, to create a GIF. Then produces GIF and stores it in the Gifs folder.

        Args:
            date (str): The date for which to retrieve the file locations and person checker.
        """
        statement = "SELECT File_Location, Person FROM Image_Storage INNER JOIN Movement ON Image_Storage.Image_Name=Movement.Image_Name WHERE Movement.Date=%s"
        value = (date,)
        Cursor = self.Connector.cursor()
        Cursor.execute(statement, value)
        File_locations, Person = [], []
        for row in Cursor.fetchall():
            File_locations.append(row[0])
            Person.append(row[1])
        Cursor.close()
        self.__Gif_creator.select_images_and_create(File_locations, date, Person)

    def __remove_images_day(self, date):
        """
        Removes images from the given day.

        Args:
            date (datetime.date): The date to remove images from.
        """
        statement = "SELECT File_Location FROM Image_Storage INNER JOIN Movement ON Image_Storage.Image_Name = Movement.Image_Name WHERE Movement.Date = %s"
        value = (date,)
        Cursor = self.Connector.cursor()
        Cursor.execute(statement, value)
        for File_Location in Cursor.fetchall():
            try:
                os.remove("..\\" + File_Location[0])
            except:
                print("file not found ", File_Location[0])
        value = (0, date,)
        statement = "UPDATE Image_Storage INNER JOIN Movement ON Image_Storage.Image_Name = Movement.Image_Name SET Image_Storage.File_Exists = %s  WHERE Movement.Date = %s"
        Cursor.execute(statement, value)
        self.Connector.commit()
        Cursor.close()


''' #Used for code testing
    def __remove_images_hours(self, date, hour):
        print(date, hour)
        statement = "DELETE FROM Hourly_Movement WHERE Date = %s and Hour = %s"
        values = (date, hour, )
        Cursor = self.Connector.cursor()
        Cursor.execute(statement, values)
        Cursor.close()'''

