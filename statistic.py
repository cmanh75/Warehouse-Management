import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV data
df = pd.read_csv("static/assets/revenue.csv")

# Convert TIME column to datetime and set as index
df['TIME'] = pd.to_datetime(df['TIME'])

# Resample data by minute and sum revenues
df_by_minute = df.set_index('TIME').resample('1min')['REVENUE'].sum().reset_index()

plt.figure(figsize=(16,10))
plt.plot(df_by_minute['TIME'], df_by_minute['REVENUE'])
plt.xlabel('Time', fontsize=14)
plt.ylabel('Revenue', fontsize=14)
plt.title('Revenue by Minute', fontsize=16)
plt.grid(True)

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Format y-axis labels as currency
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

# Save the plot
plt.savefig('static/assets/revenue_plot.png', bbox_inches='tight')
plt.close()
