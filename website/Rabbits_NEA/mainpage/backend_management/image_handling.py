from PIL import Image, ImageDraw
from mainpage.backend_management.web_Sql_handling import Website_SQL
import shutil
import os
import time

class website_images():
    """
    Class for handling all the image creation operations.

    Args:
        save_location (str): The directory where the images will be saved (static folder).
        image_location (str): The directory where the images are grabbed from.

    Attributes:
        save_location (str): The directory where the images will be saved (static folder).
        image_location (str): The directory where the images are grabbed from.
        __sql (Website_SQL): The object for handling SQL operations.

    Methods:
        Public:
        serve_latest_image: Copies the most recent stitched image from maincode to website.
        serve_latest_gif: Copies the latest gif from SQL code to website.
        daily_movement: Draws movement lines on the random day image to represent where/how the bunny uses the room and saves the modified image.
        
        Private:
        __random_day_image: Selects a random day image.
        __draw_lines: Draws lines on the image based on the given coordinates and colour.
        __draw_image: formatting for image around __draw_lines.
    """
    
    def __init__(self, save_location, image_location):
        self.save_location = save_location
        self.image_location = image_location
        self.__sql = Website_SQL()

    def serve_latest_image(self):
        """
        Copies the most recent stitched image from maincode to website.
        """
        image = self.__sql.select_most_recent_image()
        image_path = self.image_location + image
        shutil.copy(image_path, self.save_location + "latest_image.jpg")

    def serve_latest_gif(self):
        """
        Copies the latest gif from SQL code to website.
        """
        files = os.listdir(self.image_location + "SQL/Gifs")
        list = []
        for file in files:
            if file.endswith(".gif"):
                list.append(file)
        list.reverse()
        gif_path = self.image_location + "SQL/Gifs/" + list[0]
        save_location = self.save_location[:-1]
        oldname = save_location + "/" + list[0]
        rename = save_location + "/" + "latest_gif.gif"
        os.remove(rename)
        shutil.copy(gif_path, save_location)
        time.sleep(0.5)
        os.rename(oldname, rename)

    def __random_day_image(self):
        """
        Selects a random day image from most recent full day.

        Returns:
            PIL.Image: The random day image.
        """
        image = self.__sql.select_random_day_image()
        image_path = self.image_location + image
        image = Image.open(image_path)
        return image

    def __draw_lines(self, coordinates, colour, drawing):
        """
        Draws lines on the image based on the given coordinates and colour.

        Args:
            coordinates (list): List of coordinates for drawing lines.
            colour (tuple): RGB colour value.
            drawing (PIL.ImageDraw): The drawing object.

        Returns:
            PIL.ImageDraw: The modified drawing object.
        """
        first = True
        for coords in coordinates:
            if coords[0] == 0:
                continue
            if first == True:
                prev_coord = coords
                first = False
                continue
            prev_coord.append(coords[0])
            prev_coord.append(coords[1])
            drawing.line((prev_coord), fill=colour, width=2)  # check width
            prev_coord = coords
        return drawing

    def daily_movement(self):
        """
        Draws daily movement lines on the random day image.
        Saves the modified image as "cinny_daily_movement.png" and "cleo_daily_movement.png".
        """
        colour = [(255, 56, 25), (43, 255, 156)]
        new_image = self.__random_day_image()
        image = new_image.copy()
        day_movement_cin, day_movement_cleo = self.__sql.select_daily_movement()
        self.__draw_image("cinny_", day_movement_cin, colour[0], new_image)
        self.__draw_image("cleo_", day_movement_cleo, colour[1], image)

    def __draw_image(self, name, coords, colour, image):
        """
        Formatting for image around __draw_lines then saves image in required location.

        Args:
            name (str): The name of the image.
            coords (list): List of coordinates for drawing lines.
            colour (tuple): RGB colour value.
            image (PIL.Image): The image to be modified.
        """
        drawing = ImageDraw.Draw(image)
        drawing = self.__draw_lines(coords, colour, drawing)
        location = self.save_location + name + "daily_movement.png"
        image.save(location)
        image.close()