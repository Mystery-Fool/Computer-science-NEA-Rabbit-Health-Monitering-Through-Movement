#Task have some way to get the messages from both clients then compare names and work out how to splice images together
#**Then add entry to MYSQL database of that name** -phase two - *add to queue to run into tensorflow* - seperate class phase 3
#upgrade to automata down the line along with making into classes
import time
import multiprocessing
from Image_and_server_handling.Server_communication import Server_Communication
from Image_and_server_handling.stitchs import my_stitch
import threading
from Image_and_server_handling.Server_code_MYSQL import sql_server_handling

def start_collected(queue):
    server=threading.Thread(target=server_checker,args=(queue,))
    server.start()

def start_stitching(queue,sql):
    stitcher=my_stitch()
    stitcher.loop_stitches(queue,sql)
    

def server_checker(queue):
    File_Names=["",""]
    Server=Server_Communication(File_Names)
    time.sleep(1)
    Server.accept_connections()
    timer=0
    Past_Name=""
    while True:
        time.sleep(0.1)
        timer+=1
        if File_Names[0]==File_Names[1]!=Past_Name: #risk of error if raspberry pis get out of sync
            print(File_Names[0])
            timer=0
            Past_Name=File_Names[0]
            Server.MyEvent.set()
            time.sleep(0.01)
            Server.MyEvent.clear()
            queue.put(Past_Name)
        if timer>500:
            print(File_Names)
            timer=0
            #send an email
        
        
if __name__=="__main__":
    sql=sql_server_handling()
    my_sql=threading.Thread(target=sql.automate_SQL_db_updates)
    my_sql.start()
    queue=multiprocessing.Queue()
    collected=multiprocessing.Process(target=start_collected, args=(queue,))
    collected.start()
    start_stitching(queue,sql)
    


    
    