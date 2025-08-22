import pandas as pd
import seaborn as sbn
import matplotlib.pyplot as plt

df = sbn.load_dataset('tips')

df['tip_percentage'] = df['tip']/df['total_bill']*100
df['bill_per_person'] = df['total_bill']/df['size']

plt.figure(figsize=(10, 6))
sbn.regplot(x='total_bill', y='tip', data=df)
plt.title('Mối quan hệ giữa Tổng hóa đơn và Tiền boa')
plt.xlabel('Tổng hóa đơn ($)')
plt.ylabel('Tiền boa ($)')
plt.grid(True)
plt.show()

plt.figure(figsize=(12, 7))
sbn.boxplot(x='day', y='total_bill', hue='time',
            data=df, order=['Thur', 'Fri', 'Sat', 'Sun'])
plt.title('Phân phối Tổng hóa đơn theo Ngày và Buổi ăn')
plt.xlabel('Ngày trong Tuần')
plt.ylabel('Tổng hóa đơn ($)')
plt.legend(title='Buổi ăn')
plt.show()

plt.figure(figsize=(10, 6))
sbn.violinplot(x='smoker', y='tip_percentage', data=df)
plt.title('Phân phối Tỷ lệ tiền boa giữa Người hút thuốc và Không hút thuốc')
plt.xlabel('Khách hàng có hút thuốc?')
plt.ylabel('Tỷ lệ tiền boa (%)')
plt.show()

sbn.pairplot(df, hue='sex', diag_kind='kde')
plt.suptitle('Biểu đồ tổng quan các mối quan hệ', y=1.02)  # Thêm tiêu đề chung
plt.show()

print(df.head())
