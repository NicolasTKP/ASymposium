import pandas as pd
stations = ['27234', '3014080_', 'PANDAMARAN', 'SELATMUARA', 'PEKANMERU']
params = {
    'Station': '3014080_',
    'building_value': 391000,
    'content_value': 48429,
}



prob_df = pd.read_csv('Data/Py_output/probability_klangWL.csv')
def adjusted_damage_ratio(d_actual, h_actual,d_avg=2, h_avg=1.1, base_ratio=0.032, k=0.5, m=0.4):
    return base_ratio * (d_actual / d_avg) ** k * (h_actual / h_avg) ** m

if params['Station'] in stations:
    try:
        df = pd.read_csv('Data/R_output/cleaned_klangWLRF.csv')
        danger_lvl = df.loc[df['station_id'] == params['Station'], 'danger'].values[0]
    except:
        df = pd.read_csv('Data/R_output/normal_klangWLRF.csv')
        danger_lvl = df.loc[df['station_id'] == params['Station'], 'danger'].values[0]

    table = pd.DataFrame(columns=['Depth', 'Flood_Duration', 'Probability', 'Building_Value', 'Content_Value', 'Damage_Ratio', 'Estimated_Loss', 'EAL'])
    for i in [1.05,1.1,1.15]:
        depth = round(danger_lvl * i, 2)
        for duration in [1,2,3,4]:
            dmg_ratio = round(adjusted_damage_ratio(d_actual=duration,h_actual=i),4)
            estimated_loss = round((params['building_value'] + params['content_value']) * dmg_ratio,2)
            if i == 1.05:
                prob = prob_df.loc[prob_df['Station_ID'] == params['Station'], 'P(X > Danger * 1.05)'].values[0]
            elif i == 1.1:
                prob = prob_df.loc[prob_df['Station_ID'] == params['Station'], 'P(X > Danger * 1.1)'].values[0]
            else:
                prob = prob_df.loc[prob_df['Station_ID'] == params['Station'], 'P(X > Danger * 1.15)'].values[0]

            eal = round(estimated_loss * prob,2)

            new_row = pd.DataFrame([{
                'Depth': depth,
                'Flood_Duration': duration,
                'Probability': prob,
                'Building_Value': params['building_value'],
                'Content_Value': params['content_value'],
                'Damage_Ratio': dmg_ratio,
                'Estimated_Loss': estimated_loss,
                'EAL':eal
            }])
            table = pd.concat([table, new_row], ignore_index=False)

print("Pricing Table:")
print(table)
eal_at_duration_4 = table[table['Flood_Duration'] == 4]
total_eal = eal_at_duration_4.groupby('Depth')['EAL'].sum()
print(total_eal.sum())
table.to_csv('Data/Py_output/pricing.csv', index=False)