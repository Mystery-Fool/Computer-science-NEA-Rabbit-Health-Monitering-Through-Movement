from Image_and_server_handling.splicing import stitch
from Image_and_server_handling.Server_code_MYSQL import sql_server_handling
import time
import os

class my_stitch():
    def __init__(self):
        self.stitcher=stitch()
        self.local_queue=[]
        self.fails=0
        self.fail_flag=False
    def loop_stitches(self,queue,SQL):
        while True:
            self.local_queue.append(queue.get())
            if len(self.local_queue)!=0:
                name=self.local_queue.pop(0)
                name=name[:-4]
                start_time=time.time()
                print("started stitching: ",name)
                nameL="Recived_images\\"+ name +"L.jpg"
                nameR="Recived_images\\"+ name +"R.jpg"
                file_name="Stitched_images\\" + name + ".jpg"
                time.sleep(0.5)
                try:
                    self.stitcher.stitch_and_save(nameL,nameR,file_name)
                except:
                    time.sleep(10)
                    try:
                        self.stitcher.stitch_and_save(nameL,nameR,file_name)
                    except:
                        self.fails=self.fails+1
                        print("failed stitch ", self.fails," times")
                        self.local_queue.append(name)
                        self.fail_flag=True
                    else:
                        os.remove(nameL)
                        os.remove(nameR)
                        SQL.save_images(name,file_name)
                        print("stitching success")
                else:
                    os.remove(nameL)
                    os.remove(nameR)
                    SQL.save_images(name,file_name)
                    print("stitching success")
                end_time=time.time()
                print(end_time-start_time)