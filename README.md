# Projectile Motion: Numerical Simulation and Analysis

A Python investigation of projectile motion. It combines an interactive visualiser with a numerical study of how the timestep affects accuracy, why the error behaves the way it does, and how well the simulation matches the exact answer.

## The question

> **How does the timestep size affect the accuracy and cost of a numerical projectile simulation, and can I explain the error from the maths?**

The project started as an interactive 2D visualiser. Once it worked, I wanted to know how accurately the computer represents the physics, so I compared it with the exact analytical answer.

## Physics model (ideal projectile)

Assumptions: no air resistance, constant gravity, flat ground.

With launch speed $v_0$ and angle $\theta$:

$$v_x = v_0\cos\theta, \qquad v_{0y} = v_0\sin\theta$$

$$x = v_x t, \qquad y = v_{0y}t - \tfrac12 g t^2$$

The projectile lands when $y = 0$, which gives a flight time $T = 2v_{0y}/g$ and a range

$$R = \frac{v_0^2 \sin 2\theta}{g}$$

For $v_0 = 20$ m/s, $\theta = 45^\circ$, $g = 9.81$ m/s²: $R = 40.7747$ m.

## Numerical method

The simulation moves forward in small steps of size $\Delta t$. Each step:

1. Update the vertical velocity: $v_y \leftarrow v_y - g\,\Delta t$
2. Move using the **new** velocity: $x \leftarrow x + v_x\Delta t$, $y \leftarrow y + v_y\Delta t$
3. Stop when $y < 0$, then use linear interpolation between the last two points to estimate where the projectile reached $y = 0$.

(Updating velocity first and then position is known as semi-implicit Euler, or Euler–Cromer.)

## Why the error is proportional to Δt

The convergence slope came out close to 1. I wanted to understand why, not just measure it.

After $k$ steps the velocity is $v_{0y} - g k\,\Delta t$. Adding up the vertical moves over $n$ steps:

$$y_n = \sum_{k=1}^{n}\left(v_{0y} - g k\,\Delta t\right)\Delta t = n\,v_{0y}\Delta t - g\,\Delta t^2\,\frac{n(n+1)}{2}$$

Writing $t = n\,\Delta t$, this becomes

$$y(t) = v_{0y}t - \tfrac12 g t^2 - \underbrace{\tfrac12 g\,t\,\Delta t}_{\text{extra term from the method}}$$

The last term always pulls the projectile down. Setting $y = 0$ gives a simulated flight time of

$$T_{\text{sim}} = \frac{2v_{0y}}{g} - \Delta t$$

so the simulation **lands exactly one timestep early**, and the range error is

$$\text{error} \approx v_x\,\Delta t = v_0\cos\theta\,\Delta t$$

This predicts two things before looking at any data: the error is proportional to $\Delta t$ (slope 1 on a log-log plot), and the ratio error/$\Delta t$ should equal $v_x$. For $v_0 = 20$ m/s at $45^\circ$, $v_x = 14.142$ m/s.

## Checking the prediction

| Timestep Δt (s) | Numerical range (m) | Absolute error (m) | Error / Δt |
|---:|---:|---:|---:|
| 0.1 | 39.3532329284 | 1.4214867454 | 14.2149 |
| 0.05 | 40.0648132385 | 0.7099064353 | 14.1981 |
| 0.02 | 40.4916121406 | 0.2831075332 | 14.1554 |
| 0.01 | 40.6331912041 | 0.1415284697 | 14.1528 |
| 0.005 | 40.7039807358 | 0.0707389380 | 14.1478 |
| 0.001 | 40.7605767298 | 0.0141429440 | 14.1429 |
| 0.0005 | 40.7676483080 | 0.0070713658 | 14.1427 |
| 0.0001 | 40.7733054566 | 0.0014142172 | 14.1422 |

The ratio approaches $v_x = 14.142$ as $\Delta t$ shrinks. At large $\Delta t$ it is slightly higher (about 0.5% at $\Delta t = 0.1$), because my derivation ignores the interpolation at landing, which adds a small leftover that shrinks with $\Delta t$.

A log-log fit of error against $\Delta t$ gives a slope of about **1.001**.

![Convergence plot](figures/convergence.png)

## Cost

**Step count.** The number of steps is the flight time divided by $\Delta t$, so $N \propto 1/\Delta t$ by construction. The fitted slope of about −0.999 confirms the bookkeeping but is not an experimental finding.

![Step count plot](figures/computational_cost.png)

**Measured runtime.** The real trade-off is accuracy against actual compute time, so the script times each run (averaged over a few repeats) and plots error against runtime. Results depend on the machine, and the numbers are saved in `results/results.csv`.

![Error vs runtime](figures/error_vs_runtime.png)

## Validation across launch angles

The error formula predicts that the error depends on the angle through $\cos\theta$. At $\Delta t = 0.001$:

| Angle | Analytical range (m) | Numerical range (m) | Error (m) | Predicted $v_x\Delta t$ (m) |
|---:|---:|---:|---:|---:|
| 15° | 20.387360 | 20.368037 | 0.019323 | 0.019319 |
| 30° | 35.311943 | 35.294621 | 0.017322 | 0.017321 |
| 45° | 40.774720 | 40.760577 | 0.014143 | 0.014142 |
| 60° | 35.311943 | 35.301943 | 0.010000 | 0.010000 |
| 75° | 20.387360 | 20.382183 | 0.005177 | 0.005176 |

The simulation also reproduces the expected behaviour of the model: 15° and 75° give equal ranges, 30° and 60° give equal ranges, and the maximum is at 45°.

![Validation plot](figures/validation.png)

## Key findings

1. The error is proportional to $\Delta t$ (fitted slope ≈ 1.001).
2. The derivation explains why: the update rule makes the projectile land one timestep early, so the error is $v_x\Delta t$, and the measured error/$\Delta t$ matches $v_x$.
3. The same formula predicts the error at other launch angles.

## Limitations

- **Ideal model only.** No air resistance, flat ground, constant gravity.
- **Exact answer available.** Comparing against a closed-form result checks the code against a formula. It says little about cases where no exact answer exists.
- **First order is a property of this update rule, not of simulation in general.** For constant acceleration, moving the projectile with the *average* velocity over each step reproduces the exact parabola. I have not yet tested that.
- **The error formula ignores interpolation**, so it is slightly off at large timesteps.

## What I would do next

- Add **air resistance**, where there is no exact answer, and compare my method against a higher-order method, using a very fine timestep as the reference.
- Carry the same idea into time-stepping for circuits (see my [circuit solver](https://github.com/Faris-gitgud/Circuit-visualizer)).

## How to run

```bash
pip install numpy matplotlib
python projectile.py            # interactive visualiser
python projectile_analysis.py   # experiments, figures and results
```

The analysis script writes plots to `figures/` and a results table to `results/results.csv`.

## Project structure

```
Projectile-motion-visualiser/
├── projectile.py             # interactive visualiser
├── projectile_analysis.py    # numerical experiments and analysis
├── figures/                  # convergence, step count, runtime, validation plots
├── results/
│   └── results.csv           # results table
└── README.md
```

## Acknowledgements and AI assistance

I wrote the original simulation and analysis code. I used an AI assistant (Claude) to review the project, to suggest the error derivation and the runtime measurement, and to help draft this README. I ran the code and checked the results myself.
