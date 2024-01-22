import mysql.connector
from getpass import getpass
import os
import datetime
from Image_and_server_handling.vector_handling import vectors
from getpass import getpass
import time
from Image_and_server_handling.image_handling import create_gif
from Image_and_server_handling.Ai_handling import Ai
import numpy as np
import multiprocessing

class sql_server_handling():
    def __init__(self):
        self.__Password = getpass()
        self.Ai=Ai()
        try:
            self.__connect()
        except:
            print("mySQL down or wrong password")
    def __connect(self):
        self.Connector = mysql.connector.connect(user="root", password=self.__Password, host="localhost", database="RabbitHealth")

    def automate_SQL_db_updates(self):
        days_running=0
        Past_Time=time.strftime("%H",time.localtime())
        date=datetime.date.today()
        while True:
            Current_Time=time.strftime("%H",time.localtime())
            if Current_Time!=Past_Time: #have else deal with time.sleep
                time.sleep(60)#delay to make sure information is finished processing
                hour=datetime.time(int(Past_Time),0,0)
                self.__update_hourly_movement(date,hour)
                Past_Time=Current_Time
                if Past_Time==0:
                    days_running+=1
                    self.__update_daily_movement(date)
                    self.__make_gif(date)
                    date=datetime.date.today()
                    if days_running>2:
                        temp_date=date-datetime.timedelta(days=3)
                        self.remove_images_day(temp_date)
            else:
                delay=62-int(time.strftime("%M",time.localtime()))#delay to make sure information is finished processing
                time.sleep(delay*60)

    def __find_distance_and_avg_time(Pet1_X_Coords,Pet1_Y_Coords,Pet2_X_Coords,Pet2_Y_Coords):
        time_between_image=10000000
        counter=0
        time_moving=0
        Past_Pet_X_Coord=-1
        Past_Pet_Y_Coord=-1
        for iterator in range(len(Pet1_X_Coords)):
            Pet1_X_Coord, Pet1_Y_Coord=Pet1_X_Coords[iterator],Pet1_Y_Coords[iterator]
            if Pet1_X_Coord==Pet1_Y_Coord==0:
                pass
            elif Past_Pet_X_Coord==-1:
                Past_Pet_X_Coord=Pet1_X_Coord
                Past_Pet_Y_Coord=Pet1_Y_Coord
            else:
                counter+=1
                if  Pet1_X_Coord*0.99<Past_Pet_X_Coord<Pet1_X_Coord*1.01 and Pet1_Y_Coord*0.99<Past_Pet_Y_Coord<Pet1_Y_Coord*1.01:#rabbit moves a negligible amount-might be ai picking a slightly different midpoint therefore ignore
                    Past_Pet_X_Coord=Pet1_X_Coord
                    Past_Pet_Y_Coord=Pet1_Y_Coord
                else:
                    vectorx=abs(Pet1_X_Coord-Past_Pet_X_Coord)
                    vectory=abs(Pet1_Y_Coord-Past_Pet_Y_Coord)
                    distance+=vectors.distance([vectorx,vectory])
                    Past_Pet_X_Coord=Pet1_X_Coord
                    Past_Pet_Y_Coord=Pet1_Y_Coord
                    time_moving+=time_between_image
        pet1_avg_distance=distance//counter
        pet1_avg_time_moving=time_moving//counter
        counter=0
        Past_Pet_X_Coord=-1
        Past_Pet_Y_Coord=-1
        for iterator in range(len(Pet2_X_Coords)):
            Pet2_X_Coord, Pet2_Y_Coord=Pet2_X_Coords[iterator],Pet2_Y_Coords[iterator]
            if Pet2_X_Coord==Pet2_Y_Coord==0:
                pass
            elif Past_Pet_X_Coord==-1:
                Past_Pet_X_Coord=Pet2_X_Coord
                Past_Pet_Y_Coord=Pet2_Y_Coord
            else:
                counter+=1
                if  Pet2_X_Coord*0.99<Past_Pet_X_Coord<Pet2_X_Coord*1.01 and Pet2_Y_Coord*0.99<Past_Pet_Y_Coord<Pet2_Y_Coord*1.01:#rabbit moves a negligible amount-might be ai picking a slightly different midpoint therefore ignore
                    Past_Pet_X_Coord=Pet2_X_Coord
                    Past_Pet_Y_Coord=Pet2_Y_Coord
                else:
                    vectorx=abs(Pet2_X_Coord-Past_Pet_X_Coord)
                    vectory=abs(Pet2_Y_Coord-Past_Pet_Y_Coord)
                    distance+=vectors.distance([vectorx,vectory])
                    Past_Pet_X_Coord=Pet2_X_Coord
                    Past_Pet_Y_Coord=Pet2_Y_Coord 
                    time_moving+=time_between_image
        pet2_avg_distance=distance//counter
        pet2_avg_time_moving=time_moving//counter
        return pet1_avg_distance,pet1_avg_time_moving,pet2_avg_distance,pet2_avg_time_moving
    
    def __update_hourly_movement(self,date,hour):#rabbits might not be captured in which case 0,0 will be recored and an average result will be taken if all values are 0,0
        #date must be in an array year,month,day hour should be in int
        statement="SELECT Pet1_X_Coord, Pet1_Y_Coord, Pet2_X_Coord, Pet2_Y_Coord FROM Movement WHERE Date=%s and Hour=%s"
        date=date.strftime("%Y-%m-%d")
        hour=hour.strftime("%H:%M:%S")
        values=(date,hour,)
        Cursor=self.Connector.cursor()
        Cursor.execute(statement,values)
        pet1_d,pet1_t,pet2_d,pet2_t=self.__find_distance_and_avg_time(Cursor.fetchall())
        statement="INSERT INTO Hourly_Movement (Date, Hour, Avg_Pet1_Time_Moving, Avg_Pet1_Magnitude_Movement_Pixel, Avg_Pet2_Time_Moving, Avg_Pet2_Magnitude_Movement_Pixel) VALUES (%s, %s, %s, %s, %s, %s)"
        values=(date,hour,pet1_t,pet1_d,pet2_t,pet2_d,)
        Cursor.execute(statement,values)
        self.Connector.commit()
        Cursor.close()

    def __update_daily_movement(self,date):
        statement="SELECT Avg_Pet1_Time_Moving, Avg_Pet1_Magnitude_Movement_Pixel, Avg_Pet2_Time_Moving, Avg_Pet2_Magnitude_Movement_Pixel FROM Hourly_Movement WHERE Date=%s"
        date=date.strftime("%Y-%m-%d")
        value=(date,)
        Cursor=self.Connector.cursor()
        Cursor.execute(statement,value)
        Avg_Pet1_Time_Moving_Day,Avg_Pet1_Magnitude_Movement_Pixel_Day=0
        for (Avg_Pet1_Time_Moving, Avg_Pet1_Magnitude_Movement_Pixel) in Cursor:
            Avg_Pet1_Time_Moving_Day+=Avg_Pet1_Time_Moving
            Avg_Pet1_Magnitude_Movement_Pixel_Day+=Avg_Pet1_Magnitude_Movement_Pixel
        Avg_Pet2_Time_Moving_Day,Avg_Pet2_Magnitude_Movement_Pixel_Day=0
        for (Avg_Pet2_Time_Moving, Avg_Pet2_Magnitude_Movement_Pixel) in Cursor:
            Avg_Pet2_Time_Moving_Day+=Avg_Pet2_Time_Moving
            Avg_Pet2_Magnitude_Movement_Pixel_Day+=Avg_Pet2_Magnitude_Movement_Pixel
        statement="INSERT INTO Daily_Movement (Date, Avg_Pet1_Time_Moving, Avg_Pet1_Magnitude_Movement_Pixel, Avg_Pet2_Time_Moving, Avg_Pet2_Magnitude_Movement_Pixel) VALUES (%s, %s, %s, %s, %s)"
        values=(date,Avg_Pet1_Time_Moving_Day,Avg_Pet1_Magnitude_Movement_Pixel_Day,Avg_Pet2_Time_Moving_Day,Avg_Pet2_Magnitude_Movement_Pixel_Day,)
        Cursor.execute(statement,values)
        self.Connector.commit()
        Cursor.close()

    def __update_movement(self,image_location,image_name,date,hour,minutes_seconds):
        #date must be in an array year,month,day hour should be in int
        Cinny_xyxy,Cleo_xyxy,human=self.Ai.find_rabbits(image_location)
        Cinny_xyxy=np.split(Cinny_xyxy,2)
        Cinny_x=(Cinny_xyxy[0][0]+Cinny_xyxy[1][0])//2
        Cinny_y=(Cinny_xyxy[0][1]+Cinny_xyxy[1][1])//2
        Cleo_xyxy=np.split(Cleo_xyxy,2)
        Cleo_x=(Cleo_xyxy[0][0]+Cleo_xyxy[1][0])//2
        Cleo_y=(Cleo_xyxy[0][1]+Cleo_xyxy[1][1])//2
        date=date.strftime("%Y-%m-%d")
        hour=hour.strftime("%H:%M:%S")
        minutes_seconds=minutes_seconds.strftime("%H:%M:%S")
        if human==True:
            person=1
        else:
            person=0
        statement="INSERT INTO Movement (Date, Hour, Minutes_Seconds, Pet1_X_Coord, Pet1_Y_Coord, Pet2_X_Coord, Pet2_Y_Coord, Image_Name, Person) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values=(date,hour,minutes_seconds,Cinny_x.item(),Cinny_y.item(),Cleo_x.item(),Cleo_y.item(),image_name,person,)
        Cursor=self.Connector.cursor()
        Cursor.execute(statement,values)
        self.Connector.commit()
        Cursor.close()

    def remove_images_day(self,date): #takes a datetime.date
        statement="SELECT File_Location FROM Image_Storage INNER JOIN Movement ON Image_Storage.Image_Name=Movement.Image_Name WHERE Image_Storage.Date=%s"
        date=date.strftime("%Y-%m-%d")
        value=(date,)
        Cursor=self.Connector.cursor()
        Cursor.execute(statement,value)
        for File_Location in Cursor:
            os.remove(File_Location)
        value=(0,date,)
        statement="UPDATE Image_Storage SET File_Exists=%s INNER JOIN Movement ON Image_Storage.Image_Name=Movement.Image_Name WHERE Image_Storage.Date=%s"
        Cursor.execute(statement,value)
        self.Connector.commit()
        Cursor.close()

    def save_images(self,name,file_location):#17-01-00_2024-01-15.jpg
        Cursor=self.Connector.cursor()
        statement="INSERT INTO image_storage (Image_Name, File_Location, File_Exists) VALUES (%s, %s, %s)"
        values=(name,file_location,1,)
        Cursor.execute(statement,values)
        self.Connector.commit()
        Cursor.close()
        temp_name=name
        temp_name=temp_name.split("_")
        time=temp_name[0].split("-")
        date=temp_name[1]
        date=date.split("-")
        date=datetime.date(int(date[0]),int(date[1]),int(date[2]))
        hour=datetime.time(int(time[0]),0,0)
        minutes_seconds=datetime.time(0,int(time[1]),int(time[2]))
        self.__update_movement(file_location,name,date,hour,minutes_seconds)

    def __make_gif(self,date):
        statement="SELECT File_Location,Person FROM Image_Storage INNER JOIN Movement ON Image_Storage.Image_Name=Movement.Image_Name WHERE Movement.Date=%s"
        date=date.strftime("%Y-%m-%d")
        value=(date,)
        Cursor=self.Connector.cursor()
        Cursor.execute(statement,value)
        File_locations=Cursor.File_Location()
        Person=Cursor.Person()
        Cursor.close()
        create_gif.select_images_and_create(File_locations,date,Person)
    
    def select_image(self,date,hour,minutes_seconds):
        statement="SELECT File_Location FROM Image_Storage INNER JOIN Movement ON Image_Storage.Image_Name=Movement.Image_Name WHERE Movement.Date=%s and Movement.Hour=%s and Movement.Minutes_Seconds=%s"
        date=date.strftime("%Y-%m-%d")
        hour=hour.strftime("%H:%M:%S")
        minutes_seconds=minutes_seconds.strftime("%H:%M:%S")
        values=(date,hour,minutes_seconds,)
        Cursor=self.Connector.cursor()
        Cursor.execute(statement,values)
        File_locations=Cursor.fetchall()
        Cursor.close()
        return File_locations