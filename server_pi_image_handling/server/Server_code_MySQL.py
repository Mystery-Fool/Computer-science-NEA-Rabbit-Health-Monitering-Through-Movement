import mysql.connector
from getpass import getpass
import os
from server_code_splicing import stitch

class sql_server_handling():
    def __init__(self,password):
        self.Password = password
    def connect(self):
        self.Connector = mysql.connector.connect(user="root", password=self.Password, host="localhost", database="RabbitHealth")
        self.Cursor = self.Connector.cursor()
    def select(self,select,fro,where):
        pass
    def save_images(self,name,file_location):
        statement="INSERT INTO image_storage (Image_Name, File_Location) VALUES (%s, %s)"
        values=(name,file_location)
        self.Cursor.execute(statement,values)
        self.Connector.commit()
