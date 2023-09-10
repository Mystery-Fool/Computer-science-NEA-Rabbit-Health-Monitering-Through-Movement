import time
import multiprocessing
queue=multiprocessing.Queue()
Local_Queue=[]
#queue.put(5)
while True:
    time.sleep(0.1)
    try:
        Local_Queue.append(queue.get())
    except:
        time.sleep(1)
    if len(Local_Queue)!=0:
        name=Local_Queue[0]
        print(Local_Queue.pop())