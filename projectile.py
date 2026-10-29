"""
Projectile motion: numerical simulation vs the analytical solution.

Experiments
-----------
1. Convergence: how the range error depends on the timestep dt.
2. Cost: step count and measured runtime for each dt, and error vs runtime.
3. Validation: numerical vs analytical range across launch angles,
   including the error predicted from the derivation in the README.

Outputs are written to the figures/ and results/ folders next to this file.
"""

import csv
import os
import time

import numpy as np
import matplotlib.pyplot as plt

# Use the folder containing this Python file as the project directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIGURES_DIR = os.path.join(BASE_DIR, "figures")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)


# =========================================================
# Projectile simulation
# =========================================================
def simulate_projectile(v0, angle, g, dt):
    """
    Simulate projectile motion with a simple time-stepping method.

    Each step updates the vertical velocity first, then moves the projectile
    using the NEW velocity (this ordering is what makes the error equal
    vx * dt; see the README for the derivation).

    Returns:
        landing_x: estimated horizontal landing position
        points: number of simulation points
    """
    theta = np.radians(angle)
    vx = v0 * np.cos(theta)
    vy = v0 * np.sin(theta)

    x = 0.0
    y = 0.0
    points = 1

    while y >= 0:
        previous_x = x
        previous_y = y

        # Update velocity
        vy -= g * dt

        # Update position
        x += vx * dt
        y += vy * dt
        points += 1

        # Projectile crossed the ground
        if y < 0:
            # Linear interpolation estimates where it reaches y = 0
            f = (0 - previous_y) / (y - previous_y)
            landing_x = previous_x + f * (x - previous_x)
            return landing_x, points


# =========================================================
# Analytical solution
# =========================================================
def analytical_range(v0, angle, g):
    """Theoretical horizontal range for ideal projectile motion."""
    theta = np.radians(angle)
    return v0**2 * np.sin(2 * theta) / g


# =========================================================
# Parameters
# =========================================================
v0 = 20
angle = 45
g = 9.81
dt_values = [0.1, 0.05, 0.02, 0.01, 0.005, 0.001, 0.0005, 0.0001]
RUNTIME_REPEATS = 3  # average the runtime over a few runs to reduce noise

# =========================================================
# Experiment 1: Convergence analysis (with runtime)
# =========================================================
theoretical_range = analytical_range(v0, angle, g)
vx = v0 * np.cos(np.radians(angle))

errors = []
landing_positions = []
num_points = []
runtimes = []

for dt in dt_values:
    start = time.perf_counter()
    for _ in range(RUNTIME_REPEATS):
        landing_x, points = simulate_projectile(v0, angle, g, dt)
    runtime = (time.perf_counter() - start) / RUNTIME_REPEATS

    landing_positions.append(landing_x)
    errors.append(abs(landing_x - theoretical_range))
    num_points.append(points)
    runtimes.append(runtime)

print("=" * 78)
print("PROJECTILE MOTION NUMERICAL ANALYSIS")
print("=" * 78)
print(f"\nAnalytical range: {theoretical_range:.10f} m")
print(f"Horizontal speed vx = v0*cos(theta) = {vx:.6f} m/s")

print("\nConvergence Results:")
print(
    f"{'dt':<10}{'Landing':<16}{'Error':<16}"
    f"{'Error/dt':<12}{'Points':<10}{'Runtime (ms)':<12}"
)
for dt, landing, error, points, runtime in zip(
    dt_values, landing_positions, errors, num_points, runtimes
):
    print(
        f"{dt:<10}{landing:<16.10f}{error:<16.10f}"
        f"{error / dt:<12.4f}{points:<10}{runtime * 1000:<12.2f}"
    )

with open(os.path.join(RESULTS_DIR, "results.csv"), "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(
        ["dt", "landing_position", "error", "error_over_dt",
         "num_points", "runtime_s"]
    )
    for dt, landing, error, points, runtime in zip(
        dt_values, landing_positions, errors, num_points, runtimes
    ):
        writer.writerow([dt, landing, error, error / dt, points, runtime])

# =========================================================
# Estimate convergence order
# =========================================================
log_dt = np.log(dt_values)
log_error = np.log(errors)

p, intercept = np.polyfit(log_dt, log_error, 1)
print(f"\nEstimated convergence order: p = {p:.6f}")

fitted_errors = np.exp(intercept) * np.array(dt_values) ** p

# =========================================================
# Plot 1: Convergence
# =========================================================
plt.figure()
plt.loglog(dt_values, errors, "o-", label="Measured error")
plt.loglog(dt_values, fitted_errors, "--", label=f"Best fit: p = {p:.3f}")
plt.xlabel("Timestep (dt)")
plt.ylabel("Absolute Error (m)")
plt.title("Convergence of Numerical Projectile Simulation")
plt.grid(True, which="both")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, "convergence.png"), dpi=300)
plt.show()

# =========================================================
# Experiment 2: Computational cost
# =========================================================
# Step count: N = flight time / dt, so this slope is expected by construction.
log_points = np.log(num_points)
cost_exponent, cost_intercept = np.polyfit(log_dt, log_points, 1)
fitted_points = np.exp(cost_intercept) * np.array(dt_values) ** cost_exponent

plt.figure()
plt.loglog(dt_values, num_points, "o-", label="Simulation points")
plt.loglog(
    dt_values, fitted_points, "--",
    label=f"Best fit: exponent = {cost_exponent:.3f}",
)
plt.xlabel("Timestep (dt)")
plt.ylabel("Number of Integration Points")
plt.title("Step Count vs Timestep (N = T/dt by construction)")
plt.grid(True, which="both")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, "computational_cost.png"), dpi=300)
plt.show()

print(f"\nStep-count scaling exponent: {cost_exponent:.6f}")

# Measured runtime: the real accuracy-versus-cost trade-off.
plt.figure()
plt.loglog(runtimes, errors, "o-")
for dt, runtime, error in zip(dt_values, runtimes, errors):
    plt.annotate(f"dt={dt}", (runtime, error), textcoords="offset points",
                 xytext=(5, 5), fontsize=7)
plt.xlabel("Measured runtime per simulation (s)")
plt.ylabel("Absolute Error (m)")
plt.title("Accuracy vs Measured Runtime")
plt.grid(True, which="both")
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, "error_vs_runtime.png"), dpi=300)
plt.show()

# =========================================================
# Experiment 3: Validation across launch angles
# =========================================================
angles = [15, 30, 45, 60, 75]
validation_dt = 0.001
validation_results = []

for angle_test in angles:
    theoretical = analytical_range(v0, angle_test, g)
    numerical, points = simulate_projectile(v0, angle_test, g, validation_dt)
    error = abs(numerical - theoretical)
    percentage_error = error / theoretical * 100
    # Prediction from the derivation: error = vx * dt
    predicted_error = v0 * np.cos(np.radians(angle_test)) * validation_dt
    validation_results.append(
        (angle_test, theoretical, numerical, error,
         percentage_error, predicted_error)
    )

print("\nValidation Across Launch Angles (dt = 0.001):")
print(
    f"{'Angle':<8}{'Analytical':<13}{'Numerical':<13}"
    f"{'Error':<12}{'Error (%)':<12}{'Predicted vx*dt':<16}"
)
for (angle_test, theoretical, numerical, error,
     percentage_error, predicted_error) in validation_results:
    print(
        f"{angle_test:<8}{theoretical:<13.6f}{numerical:<13.6f}"
        f"{error:<12.6f}{percentage_error:<12.6f}{predicted_error:<16.6f}"
    )

# =========================================================
# Plot 3: Analytical vs numerical range
# =========================================================
angle_array = np.array(angles)
analytical_ranges = np.array([r[1] for r in validation_results])
numerical_ranges = np.array([r[2] for r in validation_results])

plt.figure()
plt.plot(angle_array, analytical_ranges, "o-", label="Analytical range")
plt.plot(angle_array, numerical_ranges, "s--", label="Numerical range")
plt.xlabel("Launch Angle (degrees)")
plt.ylabel("Horizontal Range (m)")
plt.title("Validation Across Different Launch Angles")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, "validation.png"), dpi=300)
plt.show()
