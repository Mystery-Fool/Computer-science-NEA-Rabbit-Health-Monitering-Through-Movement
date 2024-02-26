from mainpage.backend_management.web_Sql_handling import Website_SQL
import numpy as np
import scipy.stats as stats

class time_moving():
    """
    Class for calculating average time for moving and running hypothesis tests.

    Args:
        sql (Website_SQL): An instance of the Website_SQL class.
        data_range (int): The range of days to consider (default: 7).

    Attributes:
        __sql (Website_SQL): An instance of the Website_SQL class.
        __data_range (int): The range of days to consider.
        __time_factor (int): The conversion factor from microseconds to seconds as data is store in microseconds.

    Methods:
        Private:
        __hypothesis_test: Performs the hypothesis test for average time spent moving for each rabbit.
        __warning_level: Determines the warning level based on the p-value.

        Public:
        time: Calculates the average time for moving.
        run_hypothesis: Runs the hypothesis test for average time.
    """
        
    def __init__(self, sql, data_range = 7):
        np.random.seed(42)  # meaning of life
        self.__sql = sql
        self.__data_range = data_range
        self.__time_factor = 10 ** 6  # converts from microseconds to seconds

    def time(self):
        """
        Calculates the mean time for moving over the span of 7 days.

        Returns:
            tuple: A tuple containing the average time for Cinny and Cleo.
        """
        times = self.__sql.select_average_time_moving()
        cinny, cleo = 0, 0
        for x in range(len(times)):
            cinny += int(times[x][0])
            cleo += int(times[x][1])
        cinny = (cinny / self.__data_range) / (self.__time_factor)
        cleo = (cleo / self.__data_range) / (self.__time_factor)
        cinny = round(cinny, 3)  # 3dp precision
        cleo = round(cleo, 3)
        return cinny, cleo

    def run_hypothesis(self):
        """
        Public method adding on to private __hypothesis_test method providing context to values.

        Returns:
            tuple: A tuple containing the warning level for Cinny and Cleo, and the probability-values for Cinny and Cleo.
        """
        cinny_p, cleo_p = self.__hypothesis_test()
        cinny = self.__warning_level(cinny_p)
        cleo = self.__warning_level(cleo_p)
        return (cinny, cleo), (cinny_p, cleo_p)

    def __hypothesis_test(self):
        """
        Performs the hypothesis test for average time spent moving for each rabbit.

        Returns:
            tuple: A tuple containing the p-value for Cinny and Cleo.
        """
        cinny, cleo = self.__sql.select_average_time_moving_hypothesis_test()
        sum_sq_cinny, sum_sq_cleo = 0, 0
        cinny_mean, cleo_mean = 0, 0
        for iterator in range(len(cinny)):
            cinny_mean += int(cinny[iterator])
            sum_sq_cinny += int(cinny[iterator]) ** 2
            cleo_mean += int(cleo[iterator])
            sum_sq_cleo += int(cleo[iterator]) ** 2
        sq_sum_cinny = cinny_mean ** 2
        sq_sum_cleo = cleo_mean ** 2
        cinny_mean, cleo_mean = 0, 0
        for iterator in range(0, 24):
            cinny_mean += int(cinny[iterator])
            cleo_mean += int(cleo[iterator])
        cinny_mean = cinny_mean / 24
        cleo_mean = cleo_mean / 24
        cinny_standard_deviation = (((sum_sq_cinny) - (sq_sum_cinny / len(cinny))) / len(cinny)) ** 0.5
        cleo_standard_deviation = (((sum_sq_cleo) - (sq_sum_cleo / len(cleo))) / len(cleo)) ** 0.5
        normal_cinny = stats.norm.rvs(loc=cinny_mean, scale=cinny_standard_deviation, size = 1000)
        normal_cleo = stats.norm.rvs(loc=cleo_mean, scale=cleo_standard_deviation, size = 1000)
        cinny_p_value = stats.ttest_1samp(normal_cinny, cinny_mean)[1]
        cleo_p_value = stats.ttest_1samp(normal_cleo, cleo_mean)[1]
        return cinny_p_value, cleo_p_value

    def __warning_level(self, p_value):
        """
        Determines the warning level based on the p-value determined by the hypothesis test.

        Parameters:
            p_value (float): The p-value.

        Returns:
            str: The warning level.
        """
        if p_value < 0.25 or p_value > 0.75:
            return "Out of the ordinary"
        if p_value < 0.1 or p_value > 0.9:
            return "Cause for concern"
        if p_value < 0.05 or p_value > 0.95:
            return "Significant"
        else:
            return "Normal"
