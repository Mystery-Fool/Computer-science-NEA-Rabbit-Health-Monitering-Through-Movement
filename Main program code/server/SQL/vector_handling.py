class vectors():
    def distance(vector):
        """
        Calculates the magnitude of a vector.

        Args:
            vector (tuple): The vector coordinates (x, y).

        Returns:
            float: The magnitude of the vector.
        """
        distance = ((vector[0] ** 2 ) + (vector[1] ** 2)) ** 0.5
        return distance
    
    
class time_distance_calculator(vectors):
    def distance_calculator(self,movement):
        """
        Calculates the total distance traveled based on a series of vectors.

        Args:
            movement (list): A list of vectors representing the movement.

        Returns:
            int: The total distance traveled.
        """
        total = 0
        for vector in movement:
            total = total + self.distance(vector)
        return total

    