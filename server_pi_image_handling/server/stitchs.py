from server_code_splicing import stitch
from Server_code_MYSQL import sql_server_handling
import time
import os

class stitch():
    def __init__(self,password):
        self.stitcher=stitch()
        self.SQL=sql_server_handling(password)
        self.SQL.connect()
        self.local_queue=[]
        self.fails=0
        self.fail_flag=False
    def loop_stitches(self,queue):
        while True:
            self.stitchs(queue)
    def stitchs(self,queue):
        self.local_queue.append(queue.get())
        if len(self.local_queue)!=0:
            name=self.local_queue.pop(0)
            name=name[:-4]
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
                    self.SQL.save_images(name,file_name)
            else:
                os.remove(nameL)
                os.remove(nameR)
                self.SQL.save_images(name,file_name)