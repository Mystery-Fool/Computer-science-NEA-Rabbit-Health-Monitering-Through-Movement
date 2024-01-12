import mysql.connector
from getpass import getpass
import os
import datetime
from Analysis.vector_handling import vectors
from getpass import getpass
import time

class sql_server_handling():
    def __init__(self):
        self.__Password = getpass()
        try:
            self.connect()
        except:
            print("mySQL down or wrong password")
    def connect(self):
        self.Connector = mysql.connector.connect(user="root", password=self.__Password, host="localhost", database="RabbitHealth")
    def automate_SQL_db_updates(self):
        days_running=0
        Past_Time=time.strftime("%H",time.localtime())
        date=datetime.date.today()
        while True:
            Current_Time=time.strftime("%H",time.localtime())
            if Current_Time!=Past_Time: #have else deal with time.sleep
                time.sleep(60)#delay to make sure information is finished processing
                self.update_hourly_movement(date,int(Past_Time))
                Past_Time=Current_Time
                if Past_Time==0:
                    days_running+=1
                    self.update_daily_movement(date)
                    date=datetime.date.today()
                    if days_running>1:
                        temp_date=date-datetime.timedelta(days=3)
                        self.remove_images_day(temp_date)
            else:
                delay=61-(time.strftime("%M",time.localtime()))
                time.sleep(delay*60)
    def __find_distance_and_avg_time(Cursor):
        time_between_image=2000000
        counter=0
        time_moving=0
        Past_Pet_X_Coord=-1
        Past_Pet_Y_Coord=-1
        for (Pet1_X_Coord, Pet1_Y_Coord) in Cursor:
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
        for (Pet2_X_Coord, Pet2_Y_Coord) in Cursor:
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
    def update_hourly_movement(self,date,hour):#rabbits might not be captured in which case 0,0 will be recored and an average result will be taken if all values are 0,0
        #date must be in an array year,month,day hour should be in int
        statement="SELECT Pet1_X_Coord, Pet1_Y_Coord, Pet2_X_Coord, Pet2_Y_Coord FROM Movement WHERE Date=%s and Hour=%s"
        hour=datetime.hour(hour)
        values=(date,hour)
        Cursor=self.Connector.cursor()
        Cursor.execute(statement,values)
        pet1_d,pet1_t,pet2_d,pet2_t=self.__find_distance_and_avg_time(Cursor)
        statement="INSERT INTO Hourly_Movement (Date, Hour, Avg_Pet1_Time_Moving, Avg_Pet1_Magnitude_Movement_Pixel, Avg_Pet2_Time_Moving, Avg_Pet2_Magnitude_Movement_Pixel) VALUES (%s, %s, %s, %s, %s, %s)"
        values=(date,hour,pet1_t,pet1_d,pet2_t,pet2_d)
        Cursor.execute(statement,values)
        self.Connector.commit()
        Cursor.close()
    def update_daily_movement(self,date):
        statement="SELECT Avg_Pet1_Time_Moving, Avg_Pet1_Magnitude_Movement_Pixel, Avg_Pet2_Time_Moving, Avg_Pet2_Magnitude_Movement_Pixel FROM Hourly_Movement WHERE Date=%s"
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
        values=(date,Avg_Pet1_Time_Moving_Day,Avg_Pet1_Magnitude_Movement_Pixel_Day,Avg_Pet2_Time_Moving_Day,Avg_Pet2_Magnitude_Movement_Pixel_Day)
        Cursor.execute(statement,values)
        self.Connector.commit()
        Cursor.close()
    def remove_images_day(self,date): #takes a datetime.date
        statement="SELECT File_Location FROM Image_Storage INNER JOIN Movement ON Image_Storage.Image_Name=Movement.Image_Name WHERE Image_Storage.Date=%s"
        value=(date,)
        Cursor=self.Connector.cursor()
        Cursor.execute(statement,value)
        for File_Location in Cursor:
            os.remove(File_Location)
        statement="UPDATE File_Location SET Image_Storage=NULL INNER JOIN Movement ON Image_Storage.Image_Name=Movement.Image_Name WHERE Image_Storage.Date=%s"
        Cursor.execute(statement,value)
        self.Connector.commit()
        Cursor.close()
    def save_images(self,name,file_location):
        Cursor=self.Connector.cursor()
        statement="INSERT INTO image_storage (Image_Name, File_Location) VALUES (%s, %s)"
        values=(name,file_location)
        Cursor.execute(statement,values)
        self.Connector.commit()
        Cursor.close()
#sqlclass -grabbing gifs file locations
#inputing AI results