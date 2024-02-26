import multiprocessing
from Image_and_server_handling.Server_communication import Server_Communication
from Image_and_server_handling.stitchs import my_stitch
       
if __name__=="__main__": #Main section to run the server code.
    queue=multiprocessing.Queue()
    server=multiprocessing.Process(target=Server_Communication, args=(queue,)).start()
    my_stitch(queue)