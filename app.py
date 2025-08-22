import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('sales_data.csv')

df['Date'] = pd.to_datetime(df['Date'])
df['Revenue'] = df['Price']*df['Quantity']

df['Month'] = df['Date'].dt.month

revenue_by_month = df.groupby('Month')['Revenue'].sum()


print(df)


plt.figure(figsize=(10, 6))
revenue_by_month.plot(kind='line', marker='o')

plt.title("Biểu đồ doanh thu theo tháng")
plt.xlabel("Tháng")
plt.ylabel("Doanh thu VNĐ")
plt.grid(True)
plt.xticks(revenue_by_month.index)
plt.show()
