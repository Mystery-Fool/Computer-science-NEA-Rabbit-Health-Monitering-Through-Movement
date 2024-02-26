from Image_and_server_handling.splicing import stitch
from Image_and_server_handling.Server_code_Saving_Images_MYSQL import sql_server_image_handling
import time
import os

class my_stitch():
    """
    Class for stitching and saving images using the global queue.

    Args:
        queue (multiprocessing.Queue): The queue to retrieve image names from.

    Attributes:
        stitcher (stitch): An instance of the stitch class for image stitching.
        local_queue (list): A list to store the image names retrieved from the queue.
        fails (int): The number of failed stitching attempts.
        SQL (sql_server_image_handling): An instance of the sql_server_image_handling class for saving images to a SQL server.
        error_names (list): A list to store the names of images that failed to stitch multiple times.

    Methods:
        Private:
        __recovery: Recovers images from the "Recived_images" directory and adds them to the local queue.
        __Loop_stitches: Continuously retrieves image names from the queue, stitches and saves the images, and handles any errors.
    """

    def __init__(self, queue):
        self.stitcher = stitch()
        self.local_queue = []
        self.fails = 0
        self.SQL = sql_server_image_handling()
        self.error_names = []
        self.__recovery()
        self.__Loop_stitches(queue)

    def __recovery(self):
        """
        Recovers images from the "Recived_images" directory and adds them to the local queue to give a second shot at adding them to database.
        """
        files = os.listdir("Recived_images")
        for file in files:
            if file.endswith("L.jpg"): # So repeated entries not entered
                file=file[:-5]
                file=file+".jpg"
                self.local_queue.append(file)

    def __Loop_stitches(self, queue):
        """
        Continuously retrieves image names from the global queue moving into local queue, and then stitching and saving joined images while handling any errors e.g. file not found.

        Args:
            queue (multiprocessing.Queue): The queue to retrieve image names from.
        """
        local_fails = 0
        while True:
            self.local_queue.append(queue.get())
            if len(self.local_queue) != 0:
                name = self.local_queue.pop(0)
                name = name[:-4]
                if len(name) < 18:
                    print(len(name))
                    continue
                start_time = time.time()
                print("started stitching: ", name)
                nameL = "Recived_images\\" + name + "L.jpg"
                nameR = "Recived_images\\" + name + "R.jpg"
                file_name = "Stitched_images\\" + name + ".jpg"
                try:
                    self.stitcher.stitch_and_save(nameL, nameR, file_name)
                except:
                    time.sleep(0.5)
                    try:
                        self.stitcher.stitch_and_save(nameL, nameR, file_name)
                    except:
                        self.fails += 1
                        local_fails += 1
                        print("failed stitch ", self.fails, " times")
                        if local_fails > 1:
                            if name in self.error_names:
                                local_fails = 0
                                continue
                            self.error_names.append(name)
                        self.local_queue.append(name)
                    else:
                        os.remove(nameL)
                        os.remove(nameR)
                        self.SQL.save_images(name, file_name)
                        print("stitching success")
                else:
                    os.remove(nameL)
                    os.remove(nameR)
                    self.SQL.save_images(name, file_name)
                    print("stitching success")
                end_time = time.time()
                print(end_time - start_time)
