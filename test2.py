base_ratio = 0.032
d_actual = 4
d_avg = 2
h_actual = 1.0
h_avg = 0.5


def adjusted_damage_ratio(base_ratio, d_actual, d_avg, h_actual, h_avg, k=1, m=2):
    return base_ratio * (d_actual / d_avg) ** k * (h_actual / h_avg) ** m

ratio = adjusted_damage_ratio(0.032, d_actual=6, d_avg=3, h_actual=1.0, h_avg=0.5)
print(f"Adjusted Damage Ratio = {ratio:.4f}")