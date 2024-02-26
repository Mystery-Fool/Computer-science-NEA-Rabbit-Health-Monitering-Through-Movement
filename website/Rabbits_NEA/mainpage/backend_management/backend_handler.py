from mainpage.backend_management.rabbit_time import time_moving
from mainpage.backend_management.web_Sql_handling import Website_SQL
from mainpage.backend_management.graphs import create_graphs
from mainpage.backend_management.image_handling import website_images
import os

class handler():
    """
    Class for directing all the backend operations.

    Args:
        file_location_static (str, optional): The file location for static files servered to the website. Defaults to "../static/".
        path_to_images (str, optional): The path to the images directory to allow for interfacing with main code. Defaults to "../../../../".

    Attributes:
        __sql (Website_SQL): The object for handling SQL operations for gathering data.
        __time_moving (time_moving): The object for handling time data.
        __graph (create_graphs): The object for creating graphs.
        __images (website_images): The object for handling image grabbing.
    
    Methods:
        Public:
        handle_website: Handles the mainpage by running the necessary modules.
        handle_report: Handles the printing report by running the necessary modules.
    """
    
    def __init__(self, file_location_static="../static/", path_to_images="../../../../"):
        file_location_static = os.path.join(os.path.dirname(__file__), file_location_static) # append the file location to the current directory
        path_to_images = os.path.join(os.path.dirname(__file__), path_to_images)
        self.__sql = Website_SQL()
        self.__time_moving = time_moving(self.__sql)
        self.__graph = create_graphs(file_location_static)
        self.__images = website_images(file_location_static, path_to_images)

    def handle_website(self):
        """
        Handles the mainpage by running the necessary modules to gather data required for display.

        Returns:
            tuple: A tuple containing the hypothesis and times to be displayed on webpage.
        """
        self.__images.serve_latest_gif()
        hypothesis = self.__time_moving.run_hypothesis()
        print(hypothesis)
        times = self.__time_moving.time()
        print(times)
        self.__graph.movement()
        self.__images.serve_latest_image()
        self.__images.daily_movement()
        return hypothesis[0], times

    def handle_report(self):
        """
        Handles the printing report by running the necessary modules to gather data required for display.

        Returns:
            tuple: A tuple containing the hypothesis and times in number form to display more information.
        """
        hypothesis = self.__time_moving.run_hypothesis()
        print(hypothesis)
        times = self.__time_moving.time()
        print(times)
        self.__graph.cinny_report()
        self.__graph.cleo_report()
        return hypothesis[1], times
