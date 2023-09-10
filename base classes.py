class Mainframe():
    def make_gif(): #Allows for the creation of the gif covering the day of activity
        return
    def heatmap(): #Creates acurate heatmap of activity during the day
        return
    def temp_store(self,pixel_x,pixel_y): #Adds to the array of where the animal currently is
        return
    def temp_store_create(self): #mby add mby remove - detects camera resolution to produce the array
        return
    def make_ASCII_FRAME(pixel_x,pixel_y): #Creates the ascii frame of the collected data
        return
    def perm_store(array,date): #Stores the ASCII_FRAME in a text file
        return
    
class Food():
    def __init__(self): #Add food detection automata with states
        self._food=True
        return
    def is_food(self):
        return
    
class Rabbit(Mainframe):
    num = ()
    def __init__(self,filelocation):
        self.__healthy=100 #1 to 100 scale of health comparision
        self.__temparray=[],[]
    
    def locate(self):  #Runs object detection locating the specific subject - also checks if humans in frame - in which case deletes image
        return pixel_x,pixel_y
        return "human"
    def health_check(self): #Compares averages and updates the __healthy
        return self.__healthy
