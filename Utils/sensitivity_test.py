import matplotlib.pyplot as plt

# Duration and corresponding EALs
depths = [3.15, 3.3, 3.45]
durations = [1, 2, 3, 4]
eals = [
    [152.64, 215.90, 264.72, 305.29],   # For depth 3.15
    [57.24,  81.05,  99.29,  114.74],   # For depth 3.3
    [18.9,   26.79,  32.79,  37.89]     # For depth 3.45
]

for i in range(len(depths)):
    plt.plot(durations, eals[i], marker='o', label=f'Depth = {depths[i]} m')

plt.title("EAL vs Duration for Different Flood Depths")
plt.xlabel("Duration (days)")
plt.ylabel("Expected Annual Loss (RM)")
plt.legend()
plt.grid(True)
plt.show()


import matplotlib.pyplot as plt

# Depths and corresponding EALs (for Duration = 2)
depths = [3.15, 3.3, 3.45]
eals = [215.90, 81.05, 26.79]

plt.figure(figsize=(8, 5))
plt.plot(depths, eals, marker='o', color='green')
plt.title("Sensitivity of EAL to Flood Depth (Duration = 2 days)")
plt.xlabel("Flood Depth (meters)")
plt.ylabel("Expected Annual Loss (RM)")
plt.grid(True)
plt.show()


# Asset value to EALs
import numpy as np
import matplotlib.pyplot as plt

# Fixed values from a scenario (e.g., depth=3.15, duration=2)
damage_ratio = 0.0314
probability = 0.015647

building_values = np.arange(300000, 550000, 50000)
content_values = np.arange(30000, 80000, 10000)

eal_matrix = np.zeros((len(building_values), len(content_values)))

for i, b in enumerate(building_values):
    for j, c in enumerate(content_values):
        total_asset = b + c
        el = damage_ratio * total_asset
        eal = el * probability
        eal_matrix[i, j] = eal

import seaborn as sns
import pandas as pd

df = pd.DataFrame(eal_matrix, index=building_values, columns=content_values)
plt.figure(figsize=(8, 6))
sns.heatmap(df, annot=True, fmt=".2f", cmap="YlGnBu")
plt.title("Sensitivity of EAL to Building and Content Values\n(Depth 3.15m, Duration 2 days)")
plt.xlabel("Content Value (RM)")
plt.ylabel("Building Value (RM)")
plt.tight_layout()
plt.show()

# Probability Sensitivity
print("Probability Sensitivity:")
damage_ratio = 0.0314
total_asset = 391000 + 48429

probs = [0.001, 0.005, 0.01, 0.02, 0.03]
eals = [damage_ratio * total_asset * p for p in probs]

for p, eal in zip(probs, eals):
    print(f"Probability: {p:.3f}, EAL: RM{eal:.2f}")


# Time Horizon Sensitivity
print("Time Horizon Sensitivity: ")
EAL = 215.90
years = [5, 10, 20]
total_losses = [EAL * y for y in years]

for y, loss in zip(years, total_losses):
    print(f"{y}-year loss projection: RM{loss:.2f}")


# Inflation Sensitivity
print("Inflation Sensitivity:")
building = 391000
content = 48429
inflation_rate = 0.02
years = 1

inflated_building = building * (1 + inflation_rate) ** years
inflated_content = content * (1 + inflation_rate) ** years
total_asset = inflated_building + inflated_content

damage_ratio = 0.035
probability = 0.01
el = damage_ratio * total_asset
eal = el * probability

print(f"Inflated EAL after {years} years: RM{eal:.2f}")

years = 5

inflated_building = building * (1 + inflation_rate) ** years
inflated_content = content * (1 + inflation_rate) ** years
total_asset = inflated_building + inflated_content

damage_ratio = 0.035
probability = 0.01
el = damage_ratio * total_asset
eal = el * probability

print(f"Inflated EAL after {years} years: RM{eal:.2f}")

years = 10

inflated_building = building * (1 + inflation_rate) ** years
inflated_content = content * (1 + inflation_rate) ** years
total_asset = inflated_building + inflated_content

damage_ratio = 0.035
probability = 0.01
el = damage_ratio * total_asset
eal = el * probability

print(f"Inflated EAL after {years} years: RM{eal:.2f}")

# Climate Change Sensitivity
print("Climate Change Sensitivity:")
base_prob = 0.01
years = [0, 10, 20, 30]
damage_ratio = 0.035
asset = 439429

for y in years:
    future_prob = base_prob * (1 + 0.10) ** (y / 10)
    el = damage_ratio * asset
    eal = el * future_prob
    print(f"Year {y}: Probability={future_prob:.4f}, EAL=RM{eal:.2f}")
