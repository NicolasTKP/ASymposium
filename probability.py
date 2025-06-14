import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('Data/predicted_normal_klangWLRF.csv')
data = df['wl_PEKANMERU'].values  

mean = np.mean(data)
std = np.std(data)

# Probability of exceeding 4.2
p_exceed = norm.sf(4.2, loc=mean, scale=std)  # sf = 1 - cdf
print(f"Estimated P(X > 4.2): {p_exceed:.20f}")

days = 365 
prob_at_least_once = 1 - (1 - p_exceed) ** days
print(f"Chance of exceeding at least once in a year: {prob_at_least_once:.20f}")