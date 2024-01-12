#Task have some way to get the messages from both clients then compare names and work out how to splice images together
#**Then add entry to MYSQL database of that name** -phase two - *add to queue to run into tensorflow* - seperate class phase 3
#upgrade to automata down the line along with making into classes
import time
import multiprocessing
from Server_communication import Server_Communication
from stitchs import stitch


def start_stitching(queue):
    stitcher=stitch()
    stitching=multiprocessing.Process(target=stitcher.loop_stitches, args=(queue,))
    stitching.start()

def server_checker(queue):
    Server=Server_Communication()
    time.sleep(1)
    Server.accept_connections()
    File_Names=["",""]
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
        if timer==500:
            pass
            #send an email
        
        
if __name__=="__main__":
    queue=multiprocessing.Queue()
    server_checker(queue)
    start_stitching(queue)
    
    
    
    