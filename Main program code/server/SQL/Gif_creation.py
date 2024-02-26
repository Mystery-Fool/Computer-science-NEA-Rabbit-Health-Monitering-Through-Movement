from imageio.v3 import imread
from imageio.v2 import mimwrite
from random import randint



class create_gif():
    """
    Class for creating gifs.

    Args:
        None

    Attributes:
        None

    Methods:
        Private:
        __create: Creates a GIF using the given image locations and saves it to the specified location.

        Public:
        select_images_and_create: Selects random images to form a GIF.
    """

    def __init__(self):
        pass
    
    def select_images_and_create(self, image_locations, gif_save_location, person):
        """
        Selects a random images every 150-300 images avoiding those with people then creates a GIF.

        Args:
            image_locations (list): List of image file locations.
            gif_save_location (str): File path to save the GIF.
            person (list): List representing if person is within image - same length as image_locations (list).
        """

        total = 0
        number_of_images = len(image_locations)
        images = []
        while True:
            total += randint(150, 300) # between 150 and 300 images to avoid memory overflow (only 20GB of RAM which can be dedicated)
            if total > number_of_images:
                break
            while True:
                if total > number_of_images:
                    break
                elif person[total] == 0:
                    images.append(imread("..\\" + image_locations[total]))
                    break
                else:
                    total += 1

        self.__create(images, gif_save_location)  # Could add error handling
    
    def __create(self, images, gif_save_location):
        """
        Creates a GIF using the given images and saves it to the specified location.

        Args:
            image_locations (list): List of images.
            gif_save_location (str): File path to save the GIF.

        Returns:
            bool: True if the GIF creation is successful, False otherwise.
        """
        try: # tried to use gifsicle to optimize gif size but I was unable to get it working on windows
            gif_save_location = gif_save_location.strftime("%Y-%m-%d")
            gif_save_location = "Gifs//" + gif_save_location + ".gif"
            mimwrite(gif_save_location, images, fps=10, loop=0) # loop 0 means infinite loops
            print(gif_save_location, "gif finished")
            return True
        except Exception as Error:
            print(Error)
            return False
        