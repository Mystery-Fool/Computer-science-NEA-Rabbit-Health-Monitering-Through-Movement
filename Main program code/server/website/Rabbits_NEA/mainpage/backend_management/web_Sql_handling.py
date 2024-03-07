import mysql.connector
from random import shuffle

class Website_SQL:
    """
    Class for handling MYSQL website operations.

    Args:
        data_range (int): The number of days to consider for average movement and time moving (default=7).

    Attributes:
        __Password (str): The password for the MySQL server.
        __Connector (mysql.connector.connect): The connection to the MySQL server.
        __data_range (int): The number of days to consider for average movement and time moving.
        __time_factor (int): The time factor for converting time to microseconds.
        __rounding_factor (int): The number of significant figures for rounding movement values.
    
    Methods:
        Private:
        __connect: Connects to the MySQL server.

        Public:
        select_most_recent_image: Selects the file location of the most recent image stored in the database.
        select_random_day_image: Selects a random image from the most recent full day of data (yesterday unless code stops running).
        select_average_movement: Selects the average mangnitude of movement values for the specified number of days (data_range).
        select_average_time_moving: Selects the average time moving values for the specified number of days (data_range).
        select_average_time_moving_hypothesis_test: Selects the average time moving values from the Hour table for the specified number of days*24 (data_range).
        select_daily_movement: Selects the coordinates of all the rabbits movement for the most recent full day.
        time_moving_hourly: Selects the average time moving values for each hour for both rabbits in a different format from hypothesis test.
        magnitude_moving_hour: Selects the average magnitude of movement values for each hour for both rabbits.
    """

    def __init__(self, data_range=7):
        password = "rabbit42!"
        self.__Password = password
        self.__data_range = data_range
        self.__time_factor = 10 ** 6
        self.__rounding_factor = 10 # 10 significant figures
        self.__connect()

    def __connect(self):
        """
        Connects to the MySQL server.
        """
        try:
            self.Connector = mysql.connector.connect(user="root", password=self.__Password, host="localhost", database="RabbitHealth")
        except Exception as Error:
            print(Error)

    def select_most_recent_image(self):
        """
        Selects the file location of the most recent image which was added to the database.

        Returns:
            str: The file location of the most recent image.
        """
        statement = "SELECT File_Location FROM Image_Storage INNER JOIN Movement ON Image_Storage.Image_Name=Movement.Image_Name WHERE Movement.Date=(SELECT MAX(Date) FROM Movement) ORDER BY File_Location DESC "
        Cursor = self.Connector.cursor()
        Cursor.execute(statement)
        File_location = Cursor.fetchall()
        Cursor.close()
        return File_location[0][0]

    def select_random_day_image(self):
        """
        Selects a random image from the most recent day of fully captured images.

        Returns:
            str: The file location of the randomly selected image.
        """
        statement = "SELECT File_Location FROM Image_Storage INNER JOIN Movement ON Image_Storage.Image_Name=Movement.Image_Name WHERE Movement.Date=(SELECT MAX(Date) FROM Movement) ORDER BY File_Location DESC "
        Cursor = self.Connector.cursor()
        Cursor.execute(statement)
        File_location = Cursor.fetchall()
        Cursor.close()
        shuffle(File_location)
        return File_location[0][0]

    def select_average_movement(self):
        """
        Selects the average movement values for the specified number of days given by __data_range.

        Returns:
            list: A list of lists containing the average movement values for each day by both rabbits.
        """
        statement = "SELECT Avg_Pet1_Magnitude_Movement_Pixel, Avg_Pet2_Magnitude_Movement_Pixel FROM Daily_Movement ORDER BY Date DESC LIMIT " + str(self.__data_range)
        Cursor = self.Connector.cursor()
        Cursor.execute(statement)
        Average = Cursor.fetchall()
        Cursor.close()
        Avg = []
        for x in range(len(Average)):
            Avg.append([str(Average[x][0]), str(Average[x][1])])
        return Avg

    def select_average_time_moving(self):
        """
        Selects the average time moving values for the specified number of days given by __data_range.

        Returns:
            list: A 2d list containing the average time moving values for each rabbit over each day.
        """
        statement = "SELECT Avg_Pet1_Time_Moving, Avg_Pet2_Time_Moving FROM Daily_Movement ORDER BY Date DESC LIMIT " + str(self.__data_range)
        Cursor = self.Connector.cursor()
        Cursor.execute(statement)
        Average = Cursor.fetchall()
        Cursor.close()
        Avg = []
        for x in range(len(Average)):
            Avg.append([str(Average[x][0]), str(Average[x][1])])
        return Avg

    def select_average_time_moving_hypothesis_test(self):
        """
        Selects the average time moving values in hours for the specified number of days given by __data_range.

        Returns:
            tuple: A tuple containing cinny and cleo average time moving lists for each hour.
        """
        statement = "SELECT Avg_Pet1_Time_Moving, Avg_Pet2_Time_Moving FROM Hourly_Movement ORDER BY Date DESC LIMIT " + str(self.__data_range * 24)
        Cursor = self.Connector.cursor()
        Cursor.execute(statement)
        Average = Cursor.fetchall()
        Cursor.close()
        cinny, cleo = [], []
        for x in range(len(Average)):
            cinny.append(Average[x][0])
            cleo.append(Average[x][1])
        return cinny, cleo

    def select_daily_movement(self):
        """
        Selects all the measured coordinates of the rabbits' movement for the most recent full day day.

        Returns:
            tuple: A tuple containing two lists, Cinny and Cleos coordinates over the day.
        """
        statement = "SELECT Pet1_X_Coord, Pet1_Y_Coord, Pet2_X_Coord, Pet2_Y_Coord FROM Movement INNER JOIN Daily_Movement ON Daily_Movement.Date=Movement.Date WHERE Daily_Movement.Date=(SELECT MAX(Date) FROM Daily_Movement) "
        Cursor = self.Connector.cursor()
        Cursor.execute(statement)
        Movement = Cursor.fetchall()
        Cinny_coords, Cleo_coords = [], []
        for line in Movement:
            Cinny_coords.append([line[0], line[1]])
            Cleo_coords.append([line[2], line[3]])
        Cursor.close()
        return Cinny_coords, Cleo_coords

    def time_moving_hourly(self):
        """
        Selects the average time moving values for each hour for both rabbits over a number of days from __data_range.

        Returns:
            list: A 2d list containing the average time moving values for each hour for each rabbit.
        """
        statement = "SELECT Avg_Pet1_Time_Moving, Avg_Pet2_Time_Moving FROM Hourly_Movement ORDER BY Date DESC LIMIT " + str(self.__data_range * 24)
        Cursor = self.Connector.cursor()
        Cursor.execute(statement)
        Average = Cursor.fetchall()
        Cursor.close()
        Avg = []
        for x in range(len(Average)):
            Avg.append([int(Average[x][0]), int(Average[x][1])])
        return Avg

    def magnitude_moving_hour(self):
        """
        Selects the average magnitude of movement values for each hour for both rabbits in hourly time over a given number of days from __data_range.

        Returns:
            list: A 2d list containing the average magnitude of movement values for each hour for each rabbit.
        """
        statement = "SELECT Avg_Pet1_Magnitude_Movement_Pixel, Avg_Pet2_Magnitude_Movement_Pixel FROM Hourly_Movement ORDER BY Date DESC LIMIT " + str(self.__data_range * 24)
        Cursor = self.Connector.cursor()
        Cursor.execute(statement)
        Average = Cursor.fetchall()
        Cursor.close()
        Avg = []
        for x in range(len(Average)):
            number1 = round(int(Average[x][0]) / self.__time_factor, self.__rounding_factor)
            number2 = round(int(Average[x][1]) / self.__time_factor, self.__rounding_factor)
            Avg.append([number1, number2])
        return Avg