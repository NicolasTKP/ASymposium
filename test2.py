base_ratio = 0.032
d_actual = 4
d_avg = 2
h_actual = 1.15
h_avg = 1.1


def adjusted_damage_ratio(base_ratio, d_actual, d_avg, h_actual, h_avg, k=0.5, m=0.4):
    return base_ratio * (d_actual / d_avg) ** k * (h_actual / h_avg) ** m

ratio = adjusted_damage_ratio(base_ratio, d_actual=d_actual, d_avg=d_avg, h_actual=h_actual, h_avg=h_avg)
print(f"Adjusted Damage Ratio = {ratio:.4f}")