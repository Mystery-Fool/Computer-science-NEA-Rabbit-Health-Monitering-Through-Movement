import mysql.connector
from getpass import getpass
Password = getpass()
Connector = mysql.connector.connect(user="root", password=Password, host="localhost", database="RabbitHealth")
Cursor = Connector.cursor()
name="19-12-00_2023-12-02"
file_location="19-12-00_2023-12-02.jpg"
statement=f"INSERT INTO image_storage (Image_Name, File_Location) VALUES (%s, %s)"
values=(name,file_location)
Cursor.execute(statement,values)
Connector.commit()