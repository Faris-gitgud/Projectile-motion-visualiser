import numpy as np
import matplotlib.pyplot as plt
import os

os.makedirs("figures", exist_ok=True)
os.makedirs("results", exist_ok=True)

# =========================================================
# Projectile Simulation
# =========================================================

def simulate_projectile(v0, angle, g, dt):
    """
    Simulate projectile motion using a simple time-stepping method.

    Returns:
        landing_x: Estimated horizontal landing position
        points: Number of simulation points
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

            # Linear interpolation estimates the
            # position where the projectile reaches y = 0.
            f = (0 - previous_y) / (y - previous_y)

            landing_x = (
                previous_x
                + f * (x - previous_x)
            )

            return landing_x, points


# =========================================================
# Analytical Solution
# =========================================================

def analytical_range(v0, angle, g):
    """
    Calculate the theoretical horizontal range
    for ideal projectile motion.
    """

    theta = np.radians(angle)

    return (
        v0**2 * np.sin(2 * theta) / g
    )


# =========================================================
# Parameters
# =========================================================

v0 = 20
angle = 45
g = 9.81

dt_values = [
    0.1,
    0.05,
    0.02,
    0.01,
    0.005,
    0.001,
    0.0005,
    0.0001
]


# =========================================================
# Experiment 1: Convergence Analysis
# =========================================================

theoretical_range = analytical_range(v0, angle, g)

errors = []
landing_positions = []
num_points = []

for dt in dt_values:

    landing_x, points = simulate_projectile(
        v0,
        angle,
        g,
        dt
    )

    error = abs(
        landing_x - theoretical_range
    )

    landing_positions.append(landing_x)
    errors.append(error)
    num_points.append(points)


print("=" * 65)
print("PROJECTILE MOTION NUMERICAL ANALYSIS")
print("=" * 65)

print(f"\nAnalytical range: {theoretical_range:.10f} m")

print("\nConvergence Results:")
print(
    f"{'dt':<10}"
    f"{'Landing':<18}"
    f"{'Error':<18}"
    f"{'Points':<10}"
)

for dt, landing, error, points in zip(
    dt_values,
    landing_positions,
    errors,
    num_points
):

    print(
        f"{dt:<10}"
        f"{landing:<18.10f}"
        f"{error:<18.10f}"
        f"{points:<10}"
    )
import csv

with open(
    "results/results.csv",
    "w",
    newline=""
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "dt",
        "landing_position",
        "error",
        "num_points"
    ])

    for row in zip(
        dt_values,
        landing_positions,
        errors,
        num_points
    ):
        writer.writerow(row)

# =========================================================
# Estimate Convergence Order
# =========================================================

log_dt = np.log(dt_values)
log_error = np.log(errors)

p, intercept = np.polyfit(
    log_dt,
    log_error,
    1
)

print(
    f"\nEstimated convergence order: "
    f"p = {p:.6f}"
)


# Best-fit power law

fitted_errors = (
    np.exp(intercept)
    * np.array(dt_values) ** p
)


# =========================================================
# Plot 1: Convergence
# =========================================================

plt.figure()

plt.loglog(
    dt_values,
    errors,
    "o-",
    label="Measured error"
)

plt.loglog(
    dt_values,
    fitted_errors,
    "--",
    label=f"Best fit: p = {p:.3f}"
)

plt.xlabel("Timestep (dt)")
plt.ylabel("Absolute Error (m)")
plt.title(
    "Convergence of Numerical Projectile Simulation"
)

plt.grid(
    True,
    which="both"
)

plt.legend()

plt.tight_layout()
plt.savefig( "figures/convergence.png",dpi=300)
plt.show()



# =========================================================
# Experiment 2: Computational Cost
# =========================================================

plt.figure()

plt.loglog(
    dt_values,
    num_points,
    "o-",
    label="Simulation points"
)

# Fit computational scaling
log_points = np.log(num_points)

cost_exponent, cost_intercept = np.polyfit(
    log_dt,
    log_points,
    1
)

fitted_points = (
    np.exp(cost_intercept)
    * np.array(dt_values) ** cost_exponent
)

plt.loglog(
    dt_values,
    fitted_points,
    "--",
    label=(
        f"Best fit: exponent = "
        f"{cost_exponent:.3f}"
    )
)

plt.xlabel("Timestep (dt)")
plt.ylabel("Number of Integration Points")
plt.title(
    "Computational Cost vs Timestep"
)

plt.grid(
    True,
    which="both"
)

plt.legend()

plt.tight_layout()
plt.savefig("figures/computational_cost.png", dpi=300)
plt.show()


print(
    f"\nComputational cost scaling exponent: "
    f"{cost_exponent:.6f}"
)


# =========================================================
# Experiment 3: Validation Across Launch Angles
# =========================================================

angles = [
    15,
    30,
    45,
    60,
    75
]

validation_dt = 0.001

validation_results = []

for angle_test in angles:

    theoretical = analytical_range(
        v0,
        angle_test,
        g
    )

    numerical, points = simulate_projectile(
        v0,
        angle_test,
        g,
        validation_dt
    )

    error = abs(
        numerical - theoretical
    )

    percentage_error = (
        error / theoretical
    ) * 100

    validation_results.append(
        (
            angle_test,
            theoretical,
            numerical,
            error,
            percentage_error
        )
    )


# Print validation results

print("\nValidation Across Launch Angles:")

print(
    f"{'Angle':<10}"
    f"{'Analytical':<15}"
    f"{'Numerical':<15}"
    f"{'Error':<15}"
    f"{'Error (%)':<15}"
)

for result in validation_results:

    (
        angle_test,
        theoretical,
        numerical,
        error,
        percentage_error
    ) = result

    print(
        f"{angle_test:<10}°"
        f"{theoretical:<15.6f}"
        f"{numerical:<15.6f}"
        f"{error:<15.6f}"
        f"{percentage_error:<15.6f}"
    )


# =========================================================
# Plot 3: Analytical vs Numerical Range
# =========================================================

angle_array = np.array(angles)

analytical_ranges = np.array(
    [result[1] for result in validation_results]
)

numerical_ranges = np.array(
    [result[2] for result in validation_results]
)


plt.figure()

plt.plot(
    angle_array,
    analytical_ranges,
    "o-",
    label="Analytical range"
)

plt.plot(
    angle_array,
    numerical_ranges,
    "s--",
    label="Numerical range"
)

plt.xlabel("Launch Angle (degrees)")
plt.ylabel("Horizontal Range (m)")
plt.title(
    "Validation Across Different Launch Angles"
)

plt.grid(True)

plt.legend()

plt.tight_layout()
plt.savefig("figures/validation.png", dpi=300)
plt.show()