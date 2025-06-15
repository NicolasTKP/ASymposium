import pandas as pd

df = pd.read_csv('Data/probability_klangWLRF.csv')
df2 = pd.read_csv('Data/probability_normal_klangWLRF.csv')
df = pd.concat([df,df2], ignore_index=False)
print(df)

ls = ['Normal', "Danger", 'Danger', 'Danger', 'Normal']

df['Risk Level'] = ls
print(df)
df.to_csv('Data/probability_klangWL.csv', index=False)
