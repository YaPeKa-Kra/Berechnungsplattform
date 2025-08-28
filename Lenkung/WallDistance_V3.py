import math
import numpy

# base parameters

# vehicle wall distances
axle_to_wall_range = numpy.arange(0.9, 3.3, 0.1)
DEFINED_AXLE_TO_WALL_LIST = numpy.round(axle_to_wall_range, 2)
print(f"Pre-defined axle-to-wall distances: {list(DEFINED_AXLE_TO_WALL_LIST)}")

frame_to_wall_range = numpy.arange(0, 2.4, 0.1)
DEFINED_FRAME_TO_WALL_DISTANCES = numpy.round(frame_to_wall_range, 2)
print(f"Pre-defined frame-to-wall distances: {list(DEFINED_FRAME_TO_WALL_DISTANCES)}")

class parameters():
    def __init__(self):
        self.wheelbase = float(input("wheelbase:"))
        self.axle_to_wall = DEFINED_AXLE_TO_WALL_LIST
        self.frame_to_wall = DEFINED_FRAME_TO_WALL_DISTANCES

        steering_angle_start = float(input("steering_angle_start:"))
        steering_angle_stop = float(input("steering_angle_stop:"))
        steering_angle_step = float(input("steering_angle_step:"))

        self.DEFINED_ANGLES = numpy.arange(steering_angle_start, steering_angle_stop, steering_angle_step).tolist()
        #print(f"Pre-defined steering angles: {self.DEFINED_ANGLES}")

        vehicle_speed = float(input("vehicle_speed:"))

        #cases dictionary
        self.steering_cases = []
        for angle in self.DEFINED_ANGLES:
            self.steering_cases.append({
                "steering_angle": angle,
                "Speed": vehicle_speed
            })

class calculation():
    def __init__(self, vehicle_parameters):
        self.parameters = vehicle_parameters

    def steering_radius (half_wheelbase, steering_angle_rad):
        return half_wheelbase / math.sin(steering_angle_rad)

    def axle_to_center_distance(steering_radius, steering_angle_rad):
        return steering_radius * math.cos(steering_angle_rad)
    
    def wall_to_center_distance(axle_to_center_distance, frame_to_wall):
        return axle_to_center_distance - frame_to_wall
    
    def alpha(wall_to_center, steering_radius):
        return math.asin(wall_to_center/steering_radius)
    
    def beta(steering_angle, alpha):
        return 90 - steering_angle - alpha
    
    def arc_length(steering_radius, beta):
        return 2*math.pi*steering_radius*(beta/360)
    
    def time(arc_length, speed):
        return arc_length / speed
    
    #def perform_calc(self):
    def perform_calculations(self):

        


if __name__ == "__main__":
    vehicle = parameters()