import matplotlib.pyplot as plt
from numpy import array, polyfit
from mainpage.backend_management.web_Sql_handling import Website_SQL

class create_graphs():
    """
    Class for creating graphs for display on webpage.

    Args:
        save_location (str): The location to save the graphs.
        sql (object): An instance of the Website_SQL class.
        data_range (int): The range of days for data to be consider (default is 7).

    Attributes:
        save_location (str): The location to save the graphs.
        data_range (int): The range of days for data to be consider.
        __sql (Website_SQL): The custom object for handling SQL operations.

    Methods:
        Public:
        movement: Generates movement graphs for both rabbits.
        cinny_report: Generates time and magnitude graphs exclusively for cinny.
        cleo_report: Generates time and magnitude graphs exclusively for cleo.
    
        Private:
        __line: Generates a line graph.
        __line_repeat_data: Generates a line graph with repeated data.
        __time_graph: Generates a movement graph over repeated 24 hours for a specific rabbit.
        __magnitude_graph: Generates a magnitude of movement graph over repeated 24 hour for a specific rabbit.
    """

    def __init__(self, save_location, data_range=7):
        self.save_location = save_location
        self.data_range = data_range
        self.__sql = Website_SQL(data_range=data_range)
        # Cinnys colour is rgb(255, 56, 25) and Cleos colour is rgb(43, 255, 156)

    def __line(self, y_title, y_values, colour, name, x_title="Days ago"):
        """
        Generates a line graph.

        Args:
            y_title (str): The title of the y-axis.
            y_values (list): The values for the y-axis.
            colour (list): The RGB values for the line color.
            name (str): The name of the graph.
            x_title (str): The title of the x-axis (default is "Days ago").
        """
        x_values = []
        increment = 0
        for z in y_values:
            increment = increment + 1
            x_values.append(increment)
        x_values.reverse()
        x_values = array(x_values)
        scatter = plt.scatter(x_values, y_values, marker='x', s=20, color=colour)
        scatter.axes.invert_xaxis()
        gradient, intercept = polyfit(x_values, y_values, 1)
        plt.plot(x_values, gradient * x_values + intercept, color=colour)
        plt.xlabel(x_title)
        plt.ylabel(y_title)
        location = self.save_location
        plt.savefig(location + name + "graph.png")
        plt.close()

    def __line_repeat_data(self, y_title, y_values, colour, limit, name, x_title="Time"):
        """
        Generates a line graph with repeated data in a given range.

        Args:
            y_title (str): The title of the y-axis.
            y_values (list): The values for the y-axis.
            colour (list): The RGB values for the line color.
            limit (int): The limit of the range of data.
            name (str): The filename of the graph.
            x_title (str): The title of the x-axis (default is "Time").
        """
        x_values = []
        increment = 0
        for iterator in range(limit):
            increment = increment + 1
            x_values.append(increment)
        x_list = []
        for iterator in range(0, len(y_values) // limit):
            x_list.extend(x_values)
        x_values = array(x_list)
        scatter = plt.scatter(x_values, y_values, marker='x', s=20, color=colour)
        plt.xlabel(x_title)
        plt.ylabel(y_title)
        location = self.save_location
        plt.savefig(location + name + "graph.png")
        plt.close()

    def movement(self):
        """
        Generates movement graphs for both rabbits.
        """
        averages = self.__sql.select_average_movement()
        cinny, cleo = [], []
        for x in range(len(averages)):
            cinny.append(int(averages[x][0]))
            cleo.append(int(averages[x][1]))
        cinny.reverse()
        cleo.reverse()
        self.__line("Movement (pixels)", cinny, [1, 56 / 255, 25 / 255], "cinny_")
        self.__line("Movement (pixels)", cleo, [43 / 255, 1, 156 / 255], "cleo_")

    def __time_graph(self, rabbit_number, colour, name):
        """
        Generates an average time graph for a specific rabbit.

        Args:
            rabbit_number (int): The number of the rabbit (0 for cinny, 1 for cleo).
            colour (list): The RGB values for the line color.
            name (str): The name of the graph.
        """
        times = self.__sql.time_moving_hourly()
        time = []
        for x in range(len(times)):
            time.append(int(times[x][rabbit_number]))
        time.reverse()
        self.__line_repeat_data("Time moving (microseconds)", time, colour, 24, name)

    def __magnitude_graph(self, rabbit_number, colour, name):
        """
        Generates an average magnitude graph for a specific rabbit.

        Args:
            rabbit_number (int): The number of the rabbit (0 for cinny, 1 for cleo).
            colour (list): The RGB values for the line color.
            name (str): The name of the graph.
        """
        magnitudes = self.__sql.magnitude_moving_hour()
        magnitude = []
        for x in range(len(magnitudes)):
            magnitude.append(float(magnitudes[x][rabbit_number]))
        magnitude.reverse()
        self.__line_repeat_data("Movement (pixels)", magnitude, colour, 24, name)

    def cinny_report(self):
        """
        Generates average time and magnitude graphs for cinny.
        """
        self.__time_graph(0, [1, 56 / 255, 25 / 255], "report_cinny_time_")
        self.__magnitude_graph(0, [1, 56 / 255, 25 / 255], "report_cinny_magnitude_")

    def cleo_report(self):
        """
        Generates average time and magnitude graphs for cleo.
        """
        self.__time_graph(1, [43 / 255, 1, 156 / 255], "report_cleo_time_")
        self.__magnitude_graph(1, [43 / 255, 1, 156 / 255], "report_cleo_magnitude_")