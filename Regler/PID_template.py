import matplotlib.pyplot as plt
import numpy as np

class PIDController:
    def __init__(self, Kp, Ki, Kd, setpoint):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self.previous_error = 0
        self.integral = 0

    def compute(self, process_variable, dt):
        # Calculate error
        error = self.setpoint - process_variable
        
        # Proportional term
        P_out = self.Kp * error
        
        # Integral term
        self.integral += error * dt
        I_out = self.Ki * self.integral
        
        # Derivative term
        derivative = (error - self.previous_error) / dt
        D_out = self.Kd * derivative
        
        # Compute total output
        output = P_out + I_out + D_out
        
        # Update previous error
        self.previous_error = error
        
        return output
    
# Initialize PID controller
setpoint = 100  # Desired temperature
pid = PIDController(Kp=1.0, Ki=0.1, Kd=0.05, setpoint=setpoint)
# Simulation parameters
time = np.linspace(0, 10, 100)  # 10 seconds, 100 steps
dt = time[1] - time[0]
process_variable = 20  # Initial temperature
process_values = []
# Simulate the process
for t in time:
    # PID control output
    control_output = pid.compute(process_variable, dt)
    
    # Simulate process dynamics (heating rate proportional to control output)
    process_variable += control_output * dt - 0.1 * (process_variable - 20) * dt  # Heat loss
    
    # Store the process variable
    process_values.append(process_variable)
# Plot results
plt.figure(figsize=(10, 6))
plt.plot(time, process_values, label='Process Variable (Temperature)')
plt.axhline(y=setpoint, color='r', linestyle='--', label='Setpoint')
plt.xlabel('Time (s)')
plt.ylabel('Temperature')
plt.title('PID Controller Simulation')
plt.legend()
plt.grid()
plt.show()    