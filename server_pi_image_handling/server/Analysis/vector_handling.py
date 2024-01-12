class vectors():
    def distance(vector):
        distance=(vector[0]**2+vector[1]**2)**0.5
        return distance
    
class time_distance_calculator(vectors):
    def distance_calculator(self,movement):
        for vector in movement:
            total=total+self.distance(vector)
        return total

    