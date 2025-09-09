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
        vehicle_width = float(input("vehicle_width:"))

        self.DEFINED_ANGLES = numpy.arange(steering_angle_start, steering_angle_stop, steering_angle_step).tolist()
        print(f"Pre-defined steering angles: {self.DEFINED_ANGLES}")

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

    def deg_to_rad(self, degrees):
        return math.rad(degrees)

    def rad_to_deg(self,radians):
        return math.deg(radians)
    
    def steering_radius (self, wheelbase, steering_angle):
        steering_angle_rad = self.deg_to_rad(steering_angle)
        return wheelbase / math.sin(steering_angle_rad)

    def axle_to_center_distance(self, steering_radius, steering_angle):
        steering_angle_rad = self.deg_to_rad(steering_angle)
        return steering_radius * math.cos(steering_angle_rad)
    
    def wall_to_center_distance(self, axle_to_center_distance, frame_to_wall):
        return axle_to_center_distance - frame_to_wall
    
    def steering_angle_frame(self, wheelbase, axle_to_center, vehicle_width):
        half_vehicle_width = vehicle_width / 2
        ratio = wheelbase / (axle_to_center + half_vehicle_width)
        steering_angle_rad = math.atan(ratio)
        steering_angle_deg = self.rad_to_deg(steering_angle_rad)
        return steering_angle_deg
    
    def radius_frame(self, wheelbase, steering_angle_frame):
        steering_angle_frame_rad = self.deg_to_rad(steering_angle_frame)
        return (wheelbase+0.5) / math.sin(steering_angle_frame_rad)

    def alpha(self, wall_to_center, radius_frame):
        ratio = wall_to_center / radius_frame
        alpha_rad = math.asin(ratio)
        alpha_deg = self.rad_to_deg(alpha_rad)
        return alpha_deg

    def beta(self, steering_angle_frame, alpha):
        return 90 - steering_angle_frame - alpha

    def arc_length(self, radius_frame, beta):
        return 2*math.pi*radius_frame*(beta/360)
    
    def time(arc_length, speed):
        return arc_length / speed
    
    """ calculation steps: 
    - Empty lists for results
    - Loop through steering cases
    - perform calculations in defs
    - append results to lists
    - return dataframe from lists
    - safe df as csv
    - plot frame to wall distance (x) over time (y) for angle / speed combinations"""

    def perform_calc(self):
        # results lists
        wheelbase = []
        axle_to_wall_distance = []
        frame_to_wall_distance = []
        speed = []
        steering_radius = []
        axle_to_center = []
        wall_to_center = []
        steering_angle_frame = []
        radius_frame = []
        alpha = []
        beta = []
        arc_length = []
        time = []
    
        for axle_to_wall_distance in self.parameters.axle_to_wall:
            for i, case in enumerate(self.parameters.steering_cases):
                current_steering_angle = case["steering_angle"]
                current_speed = case["Speed"]

                steering_radius_calc = self.steering_radius(wheelbase=self.parameters.wheelbase, steering_angle=current_steering_angle)
                

if __name__ == "__main__":
    vehicle_params = parameters()
    vehicle_calcs = calculation(vehicle_params)
