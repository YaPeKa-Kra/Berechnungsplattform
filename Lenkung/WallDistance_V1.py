import pandas as pd
import math
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# --- Create axle-to-wall list ranges --- 
axle_to_wall_range = np.arange(0.9, 3.3, 0.1)
DEFINED_AXLE_TO_WALL_DISTANCES = np.round(axle_to_wall_range, 2)
print(f"Pre-defined axle-to-wall distances: {list(DEFINED_AXLE_TO_WALL_DISTANCES)}")

frame_to_wall_range = np.arange(0, 2.4, 0.1)
DEFINED_FRAME_TO_WALL_DISTANCES = np.round(frame_to_wall_range, 2)
print(f"Pre-defined frame-to-wall distances: {list(DEFINED_FRAME_TO_WALL_DISTANCES)}")

# fixed angle range from 0-25° with 0.5° steps
#angle_ranges = np.arange(0, 26, 0.5)
#DEFINED_ANGLE_RANGES = angle_ranges
#print(f"Pre-defined angle range: {list(DEFINED_ANGLE_RANGES)}")

PLOT_FRAME_TO_WALL_DISTANCE = DEFINED_FRAME_TO_WALL_DISTANCES[0] 

# --- Input Code: Base Parameters added by user --- 

class BaseParameters:
    def __init__(self):
        self.half_wheelbase = float(input("Enter half wheelbase in m (e.g., 5.0 for 10m wheelbase): "))
        self.axle_to_wall_distances = DEFINED_AXLE_TO_WALL_DISTANCES
        self.frame_to_wall_distances = DEFINED_FRAME_TO_WALL_DISTANCES

        angle_start = float(input("Enter start angle in degrees: "))
        angle_end = float(input("Enter end angle in degrees: "))
        angle_step = float(input("Enter angle step in degrees: "))       
        speed = float(input("Enter velocity:"))

        angles = np.arange(angle_start, angle_end + angle_step, angle_step).tolist()
        self.DEFINED_ANGLE_RANGE = angles
        print(f"Defined Angle range: {list(self.DEFINED_ANGLE_RANGE)}")

        self.steering_speed_cases = []
        for angle in self.DEFINED_ANGLE_RANGE:
            self.steering_speed_cases.append({
                "Steering angle": angle,
                "Speed": speed
            })

# --- Calculation Code including formulas taken from excel sheet ---

class CalcEngine:
    def __init__(self, vehicle_parameters):
        self.parameters = vehicle_parameters
        self.df = pd.DataFrame()

    def degrees_to_radians(self, degrees):
        """Converts degrees to radians. Internal helper."""
        return math.radians(degrees)

    def radians_to_degrees(self, radians):
        """Converts radians to degrees. Internal helper."""
        return math.degrees(radians)

    def calculate_steering_radius_new(self, half_wheelbase, steering_angle_deg):
        """
        Calculates the steering radius using the formula: half_wheelbase / sin(steering angle deg).
        Assumes steering_angle_deg is in degrees and converts to radians for sin().
        Returns infinity if steering angle is 0.
        """
        if steering_angle_deg == 0:
            return float('inf')
        
        steering_angle_rad = self.degrees_to_radians(steering_angle_deg)
        
        if math.sin(steering_angle_rad) == 0:
            return float('inf')
            
        return half_wheelbase / math.sin(steering_angle_rad)

    def calculate_axle_to_center_new(self, steering_radius, steering_angle_deg):
        """
        Calculates axle to center using the formula: Steering radius * cos(steering angle deg).
        Assumes steering_angle_deg is in degrees and converts to radians for cos().
        """
        if steering_radius == float('inf'):
            return float('inf')

        steering_angle_rad = self.degrees_to_radians(steering_angle_deg)
        return steering_radius * math.cos(steering_angle_rad)

    def calculate_wall_to_center_new(self, axle_to_center, axle_to_wall_distance):
        """
        Calculates wall to center using the formula: Axle to center - axle to wall.
        """
        return axle_to_center - axle_to_wall_distance

    def calculate_alpha_new(self, wall_to_center, steering_radius):
        """
        Calculates alpha using the formula: arcsin(wall to center / steering radius).
        Result is converted to degrees. Handles potential domain errors for asin.
        """
        if steering_radius == 0 or steering_radius == float('inf'): # Avoid division by zero or infinite
            return 0.0 

        ratio = wall_to_center / steering_radius
        if ratio > 1:
            ratio = 1.0 # Clamp to 1 to avoid domain error for asin
        elif ratio < -1:
            ratio = -1.0 # Clamp to -1
            
        alpha_rad = math.asin(ratio) # Result is initially in radians
        return self.radians_to_degrees(alpha_rad) # Convert to degrees


    def calculate_beta_new(self, steering_angle_deg, alpha_deg):
        """
        Calculates beta using the formula: 90 - steering angle deg - alpha.
        Assumes all input angles are in degrees. Returns beta in degrees.
        """
        return 90 - steering_angle_deg - alpha_deg


    def calculate_arc_length_new(self, steering_radius, beta_deg):
        """
        Calculates arc length using the formula: 2 * pi * steering radius * (beta / 360).
        Assumes beta_deg is in degrees.
        """
        if steering_radius == float('inf'):
            return float('inf')
        return 2 * math.pi * steering_radius * (beta_deg / 360)


    def calculate_time_to_collision(self, axle_to_wall_distance, speed, alpha_deg):
        """
        Calculates the Time to Collision (TTC) based on axle_to_wall_distance,
        speed, and the alpha angle. Alpha is in degrees, converted to radians for cos().
        """
        if speed <= 0:
            return float('inf') 
        
        alpha_rad_for_cos = self.degrees_to_radians(alpha_deg) # Convert alpha to radians for cos()
        cos_alpha = math.cos(alpha_rad_for_cos)

        if cos_alpha == 0:
            return float('inf')

        return axle_to_wall_distance / (speed * abs(cos_alpha))

    def perform_calculations(self):
        """
        Performs calculations for each combination of axle_to_wall, frame_to_wall, steering angle, and speed.
        All angles are handled in degrees where possible, with internal radian conversions for math functions.
        """
        # List to store results
        half_wheelbase_out = []
        axle_to_wall_distances_out = []
        frame_to_wall_distances_out = []
        steering_angles_deg_list = []
        speeds_list = []
        steering_radii_new_list = []
        axle_to_centers_new_list = []
        wall_to_centers_new_list = []
        alphas_new_deg_list = [] 
        betas_new_deg_list = []
        arc_lengths_new_list = []
        times_list = [] 

        half_wheelbase_val = self.parameters.half_wheelbase

        # Calculation Loop - important! 
        for current_axle_to_wall_dist in self.parameters.axle_to_wall_distances:
            for current_frame_to_wall_dist in self.parameters.frame_to_wall_distances:
                for i, case_params in enumerate(self.parameters.steering_speed_cases):
                    current_steering_angle_deg = case_params["Steering angle"]
                    current_speed = case_params["Speed"]
                    
                    s_radius_new = self.calculate_steering_radius_new(half_wheelbase_val, current_steering_angle_deg)
                    axle_center_new = self.calculate_axle_to_center_new(s_radius_new, current_steering_angle_deg)
                    wall_center_new = self.calculate_wall_to_center_new(axle_center_new, current_axle_to_wall_dist)
                    alpha_new_deg = self.calculate_alpha_new(wall_center_new, s_radius_new)
                    beta_new_deg = self.calculate_beta_new(current_steering_angle_deg, alpha_new_deg)
                    arc_len_new = self.calculate_arc_length_new(s_radius_new, beta_new_deg)
                    time_to_collision_val = self.calculate_time_to_collision(
                        current_axle_to_wall_dist, current_speed, alpha_new_deg
                    )

                    # Store results in prepared lists
                    half_wheelbase_out.append(half_wheelbase_val)
                    axle_to_wall_distances_out.append(current_axle_to_wall_dist)
                    frame_to_wall_distances_out.append(current_frame_to_wall_dist)
                    steering_angles_deg_list.append(current_steering_angle_deg)
                    speeds_list.append(current_speed)
                    
                    steering_radii_new_list.append(s_radius_new)
                    axle_to_centers_new_list.append(axle_center_new)
                    wall_to_centers_new_list.append(wall_center_new)
                    alphas_new_deg_list.append(alpha_new_deg)
                    betas_new_deg_list.append(beta_new_deg)
                    arc_lengths_new_list.append(arc_len_new)
                    times_list.append(time_to_collision_val)

        # Create dataframe
        self.df = pd.DataFrame({
            "0.5*wheelbase (m)": half_wheelbase_out,
            "Axle to Wall Distance (m)": axle_to_wall_distances_out,
            "Frame to Wall Distance (m)": frame_to_wall_distances_out,
            "Steering Angle (°)": steering_angles_deg_list,
            # "Steering Angle (rad)" Column not needed
            "Speed (m/s)": speeds_list,
            "Steering Radius (m)": steering_radii_new_list,
            "Axle to Center Distance (m)": axle_to_centers_new_list,
            "Wall to Center Distance (m)": wall_to_centers_new_list,
            "Alpha (°)": alphas_new_deg_list,
            "Beta (°)": betas_new_deg_list,
            "Arc Length (m)": arc_lengths_new_list,
            "Time (s)": times_list
        })
        return self.df

# --- Class init and visualisation ---

if __name__ == "__main__":
    vehicle_params = BaseParameters()
    vehicle_calcs = CalcEngine(vehicle_params)
    df_results = vehicle_calcs.perform_calculations()

    print("\n--- Calculation Results ---")
    print(df_results)

    # --- Export DataFrame ---
    df_filename = input("\nEnter filename for the DataFrame (e.g., 'steering_data_full_results'): ") + ".txt"
    df_results.to_csv(df_filename, index=False, sep='\t')
    print(f"DataFrame saved to {df_filename}")

    # --- Plotting Results ---
    fig = go.Figure()

    # iterate over cases according to user input
    # filter by wheelbase
    half_wheelbase_val_for_legend = df_results["0.5*wheelbase (m)"].iloc[0]

    for i, case_params in enumerate(vehicle_params.steering_speed_cases):
        steering_angle = case_params["Steering angle"]
        speed = case_params["Speed"]

        # Filter df by steering angle, speed, and frame to wall distance
        subset_df = df_results[
            (df_results["Steering Angle (°)"] == steering_angle) &
            (df_results["Speed (m/s)"] == speed) &
            (df_results["Frame to Wall Distance (m)"] == PLOT_FRAME_TO_WALL_DISTANCE)
        ].sort_values(by="Axle to Wall Distance (m)")

        # Add traces
        fig.add_trace(go.Scatter(
            x=subset_df["Axle to Wall Distance (m)"],
            y=subset_df["Time (s)"],
            mode='lines+markers',
            # Legend showing angle and speed according to user input
            name=f'LW: {steering_angle}° | Speed: {speed} m/s',
            visible="legendonly" if i > 0 else True 
        ))

    # Plot Layout
    fig.update_layout(
        title=f"Time to Collision (s) vs. Axle to Wall Distance (m) (Frame-Wall: {PLOT_FRAME_TO_WALL_DISTANCE}m, Half-WB: {half_wheelbase_val_for_legend}m)", 
        xaxis_title="Axle to Wall Distance (m)",
        yaxis_title="Time (s)",
        legend_title="Steering/Speed Cases", 
        legend=dict(
            orientation="v",
            yanchor="auto",
            y=1,
            xanchor="left",
            x=1.02,
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="rgba(0, 0, 0, 0.5)",
            borderwidth=1,
            itemclick="toggle",
            itemdoubleclick="toggleothers"
        ),
        hovermode="x unified"
    )

    # Save Plot to html
    plot_filename = input("Enter filename for the HTML plot (without .html): ") + ".html"
    fig.write_html(plot_filename)
    print(f"Plot saved to {plot_filename}")

    # Open plot
    fig.show()