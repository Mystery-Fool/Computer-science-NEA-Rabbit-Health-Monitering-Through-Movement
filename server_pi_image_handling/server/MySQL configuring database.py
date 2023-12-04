import mysql.connector
from getpass import getpass
Password = getpass()
Connector = mysql.connector.connect(user="root", password=Password, host="localhost")
Cursor = Connector.cursor()
Cursor.execute("CREATE DATABASE RabbitHealth")
Connector.close()
Connector = mysql.connector.connect(user="root", password=Password, host="localhost", database="RabbitHealth")
Cursor = Connector.cursor()

#Cursor.execute("CREATE TABLE Broken_Image_Temporary_Storage (Image_Name CHAR(50), File_Location_L CHAR(50), File_Location_R CHAR(50), PRIMARY KEY(Image_Name))")
Cursor.execute("CREATE TABLE Image_Storage (Image_Name CHAR(50), File_Location CHAR(50), PRIMARY KEY(Image_Name))")
Cursor.execute("CREATE TABLE Daily_Movement (Date DATE NOT NULL, Pet1_Time_Moving TIME NOT NULL, Pet1_Magnitude_Movement_Pixel INT(32) NOT NULL, Pet2_Time_Moving TIME NOT NULL, Pet2_Magnitude_Movement_Pixel INT(32) NOT NULL, PRIMARY KEY(Date))")
Cursor.execute("CREATE TABLE Hourly_Movement (Date DATE NOT NULL, Hour TIME NOT NULL, Pet1_Time_Moving TIME NOT NULL, Pet1_Magnitude_Movement_Pixel INT(32) NOT NULL, Pet2_Time_Moving TIME NOT NULL, Pet2_Magnitude_Movement_Pixel INT(32) NOT NULL, PRIMARY KEY(Hour), FOREIGN KEY(Date) REFERENCES Daily_Movement(Date))")
Cursor.execute("CREATE TABLE Movement (Date DATE NOT NULL, Hour TIME NOT NULL,Minutes_Seconds TIME NOT NULL, Pet1_X_Coord INT(16) NOT NULL, Pet1_Y_Coord INT(16) NOT NULL, Pet2_X_Coord INT(16) NOT NULL, Pet2_Y_Coord INT(16) NOT NULL, Image_Name CHAR(50), Person BOOLEAN NOT NULL, PRIMARY KEY(Minutes_Seconds), FOREIGN KEY(Date) REFERENCES Daily_Movement(Date), FOREIGN KEY(Hour) REFERENCES Hourly_Movement(Hour), FOREIGN KEY(Image_Name) REFERENCES Image_Storage(Image_Name))")


#Cursor.execute("DROP DATABASE RabbitHealth")
Connector.close()
print("complete")