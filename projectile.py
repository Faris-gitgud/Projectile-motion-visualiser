import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider


"""
Interactive projectile-motion simulator based on ideal projectile-motion
equations. The simulator allows the initial velocity and launch angle
to be varied interactively.
"""

def ideal_trajectory(v0, angle_degrees, g=9.81, num_points=300):
    """
    Calculate the projectile trajectory for ideal projectile motion
    without air resistance.
    """

    if v0 < 0:
        raise ValueError("Initial velocity must be non-negative.")

    if not 0 <= angle_degrees <= 90:
        raise ValueError("Launch angle must be between 0 and 90 degrees.")

    if g <= 0:
        raise ValueError("Gravitational acceleration must be positive.")

    theta = np.radians(angle_degrees)

    # projectile motion equations
    time_flight = (2 * v0 * np.sin(theta)) / g
    max_range = (v0**2 * np.sin(2 * theta)) / g
    max_height = (v0**2 * (np.sin(theta))**2) / (2 * g)

    # time array
    t = np.linspace(0, time_flight, num_points)

    # position coordinates at time 't'
    x = v0 * np.cos(theta) * t
    y = v0 * np.sin(theta) * t - 0.5 * g * t**2  # using kinematic equation for vertical motion

    return x, y, time_flight, max_range, max_height 



"""
Set up the interactive visualisation.
"""

# Main figure and axes for the plot  
fig, ax = plt.subplots(figsize=(10, 6))
plt.subplots_adjust(left=0.1, bottom=0.30)

# initial parameters
v0_initial = 20  # initial velocity (m/s)
angle_initial = 45  # launch angle (degrees)

# initial trajectory calculation
x, y, time_flight, max_range, max_height = ideal_trajectory(v0_initial, angle_initial)

# tracing the trajectory of the projectile
trajectory_line, = ax.plot(x, y, label='Projectile Trajectory', color='#2563eb', linewidth=2.5)

# Mark peak of the trajectory.
peak_point, = ax.plot([max_range / 2], [max_height], marker = 'o', color='#dc2626', label='Peak Point')

# Title of plot and labels of x and y axes
ax.set_title('Projectile Motion Simulator', fontsize=16, fontweight='bold')
ax.set_xlabel('Horizontal Displacement(m)', fontsize=12)
ax.set_ylabel('Vertical Displacement (m)', fontsize=12)

# set initial limits for the axes,add grid and legend
ax.set_xlim(0, 100)
ax.set_ylim(0, 50)
ax.grid(True, linestyle='--', alpha=0.6)
ax.legend(loc='upper right')

# making a result box which displays the results of each launch
result_box = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=10, verticalalignment='top', 
                     bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9))

def update_results(r, t, h):
    """
    Update the result box with the latest results
    """
    result_text = f"Time of Flight: {r:.2f} s\nMax Range: {t:.2f} m\nMax Height: {h:.2f} m"
    result_box.set_text(result_text)

# display initial results
update_results(time_flight, max_range, max_height)

"""
Create interactive sliders for the initial conditions.
"""

# positioning the sliders on the plot
ax_v0 = plt.axes([0.1, 0.2, 0.8, 0.03])
ax_angle = plt.axes([0.1, 0.15, 0.8, 0.03])

# creating the sliders
slider_v0 = Slider(ax_v0, 'Initial Velocity (m/s)', 5, 50, valinit=v0_initial)
slider_angle = Slider(ax_angle, 'Launch Angle (degrees)', 0, 90, valinit=angle_initial, valstep=1)

def update(values):
    """
    Update the trajectory plot and result box based on slider values
    """
    v0 = slider_v0.val
    angle = slider_angle.val

    # Recalculate trajectory with new values given by user on the sliders
    x, y, time_flight, max_range, max_height = ideal_trajectory(v0, angle)

    # Update the trajectory and peak-point marker.
    trajectory_line.set_data(x, y)
    peak_point.set_data([max_range / 2], [max_height])

    # Rescale the axes based on the new trajectory.
    ax.set_xlim(0, max_range + 5)
    ax.set_ylim(0, max_height + 5)

    #. Update the result box with new results
    update_results(time_flight, max_range, max_height)
    fig.canvas.draw_idle()

# Connect the sliders to the update function.    
slider_v0.on_changed(update)
slider_angle.on_changed(update)

# show the plot with the interactive sliders
plt.show()

