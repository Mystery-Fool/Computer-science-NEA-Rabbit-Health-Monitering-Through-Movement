import mysql.connector
from getpass import getpass
Password = getpass()
Connector = mysql.connector.connect(user="root", password=Password, host="localhost")
print(Connector)
Cursor = Connector.cursor()
Cursor.execute("CREATE DATABASE RabbitHealth")
Connector.close()
Connector = mysql.connector.connect(user="root", password=Password, host="localhost", database="RabbitHealth")

Cursor.execute("CREATE TABLE ")