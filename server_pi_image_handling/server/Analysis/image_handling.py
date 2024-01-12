from PIL import Image, ImageDraw
from imageio.v3 import imread
from imageio.v2 import mimwrite
from pygifsicle import optimize
import matplotlib.pyplot as plt
from numpy import polyfit, array

class create_image():
    def __init__(self,base_image=Image.open("location of base image")):
        self.base=base_image
    def daily_movement(self,day_movement,colour):#colour1: 255,56,25 colour2: 43,255,156
        x=0
        colour=(colour)
        new_image=self.base
        drawing=ImageDraw.Draw(new_image)
        for coords in day_movement:
            if x//2==0: #Faster if statement
                x=1
                prev_coord=coords
            else:
                for x in range(2):
                    prev_coord.append(coords[x-1])
                drawing.line(prev_coord,fill=colour,width=2)#check width
                prev_coord=coords
            x=x+1
        return new_image
class create_gif():
    def create(image_locations,gif_save_location,gif_name):
        try:
            images=[]
            for image_location in image_locations:
                images.append(imread(image_location))
            gif_save_location=gif_save_location+gif_name+".gif"
            mimwrite(gif_save_location,images)
            optimize(gif_save_location)
        except Exception as Error:
            print(Error)
            return False
        
class create_graphs():
    def line(self,g_title,y_title,y_values,save_location,colour="blue"):#colour RGB values in array
        x_values=[]
        increment=0
        for z in y_values:
            increment=increment+1
            x_values.append(increment)
        x_values.reverse()
        x_values=array(x_values)
        scatter=plt.scatter(x_values,y_values,marker='x',c=colour,s=20)
        scatter.axes.invert_xaxis()
        gradient, intercept = polyfit(x_values,y_values,1)
        plt.plot(x_values, gradient*x_values + intercept)
        save_location=save_location+"graph.png"
        plt.savefig(save_location)
#x=create_graphs()
#x.line("hi","hi",[1,2,10,4,5],"")