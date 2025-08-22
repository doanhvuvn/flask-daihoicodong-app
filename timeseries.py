import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.express as px
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt
import seaborn as sbn
from vnstock import *

df = stock_historical_data(symbol='IJC',
                           start_date="2025-01-01",
                           end_date="2025-08-21")

print(df.head())
# Tính toán tỷ suất sinh lợi hàng ngày
# daily_returns = adj_close_df.pct_change().dropna()

# # Tính toán ma trận tương quan
# correlation_matrix = daily_returns.corr()

# # Trực quan hóa bằng heatmap
# plt.figure(figsize=(10, 8))
# sbn.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
# plt.title('Ma trận Tương quan Tỷ suất sinh lợi Hàng ngày')
# plt.show()

# =======================================================
# 1. TẠO DỮ LIỆU MẪU (Bỏ qua bước này nếu bạn có file thật)
# =======================================================
# Tạo một chuỗi ngày từ 2022-01-01 đến 2024-12-31
# dates = pd.date_range(start='2022-01-01', end='2024-12-31', freq='D')

# # Tạo dữ liệu doanh số với:
# # - Xu hướng tăng dần (trend)
# # - Yếu tố mùa vụ theo tuần (tăng vào cuối tuần)
# # - Nhiễu ngẫu nhiên (noise)
# # np.random.seed(42)
# # trend = np.linspace(1000, 2500, len(dates))  # Xu hướng tăng tuyến tính
# # weekly_seasonality = 150 * \
# #     np.sin(2 * np.pi * dates.dayofweek / 7) + 200 * (dates.dayofweek >= 5)
# # noise = np.random.normal(0, 80, len(dates))
# # sales = trend + weekly_seasonality + noise

# df = pd.read_excel('IJC.xlsx')

# # Tạo DataFrame

# print(df.head())

# df['NGÀY'] = pd.to_datetime(df['NGÀY'])
# df.set_index('NGÀY', inplace=True)

if not df.empty:
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['MA200'] = df['Close'].rolling(window=200).mean()
    plt.figure(figsize=(14, 7))
    plt.plot(df['Close'])
    plt.plot(df['MA50'], label='MA50', color='orange')
    plt.plot(df['MA200'], label='MA200', color='red')
    plt.title('Lịch sử Giá đóng cửa của Cổ phiếu IJC')
    plt.xlabel('Ngày')
    plt.ylabel('Giá')
    plt.legend()
    plt.show()

#     df['Tỷ suất sinh lợi'] = df['GIÁ ĐÓNG CỬA'].pct_change()
#     plt.figure(figsize=(14, 7))
#     df['Tỷ suất sinh lợi'].plot(legend=True, linestyle='--', marker='o')
#     plt.title('Tỷ suất sinh lợi hàng ngày')
#     plt.ylabel('Phần trăm (%)')
#     plt.show()

#     plt.figure(figsize=(10, 6))
#     sbn.histplot(df['Tỷ suất sinh lợi'].dropna(),
#                  bins=100, kde=True, color='purple')
#     plt.title('Phân phối của Tỷ suất sinh lợi hàng ngày')
#     plt.xlabel('Tỷ suất sinh lợi')
#     plt.ylabel('Tần suất')
#     plt.show()


# df['SMA20'] = df['GIÁ ĐÓNG CỬA'].rolling(window=20).mean()
# df['StdDev'] = df['GIÁ ĐÓNG CỬA'].rolling(window=20).std()
# df['Upper Band'] = df['SMA20'] + (df['StdDev'] * 2)
# df['Lower Band'] = df['SMA20'] - (df['StdDev'] * 2)

# # Vẽ biểu đồ
# plt.figure(figsize=(14, 7))
# plt.plot(df['GIÁ ĐÓNG CỬA'], label='Giá đóng cửa')
# plt.plot(df['Upper Band'], label='Dải trên', color='red', linestyle='--')
# plt.plot(df['Lower Band'], label='Dải dưới', color='green', linestyle='--')
# plt.plot(df['SMA20'], label='SMA 20 ngày', color='orange')
# plt.fill_between(df.index, df['Lower Band'],
#                  df['Upper Band'], color='gray', alpha=0.1)
# plt.title('Dải Bollinger cho Cổ phiếu Apple (AAPL)')
# plt.legend()
# plt.show()


# # Lấy dữ liệu gần đây để biểu đồ rõ ràng hơn (ví dụ: 1 năm qua)
# df_candle = df.loc['01/01/2025':]

# # Tạo biểu đồ nến
# fig = go.Figure(data=[go.Candlestick(x=df_candle.index,
#                 open=df_candle['GIÁ MỞ CỬA'],
#                 high=df_candle['GIÁ CAO NHẤT'],
#                 low=df_candle['GIÁ THẤP NHẤT'],
#                 close=df_candle['GIÁ ĐÓNG CỬA'],
#                 name='Giá')])

# # Thêm các đường trung bình động
# fig.add_trace(go.Scatter(x=df_candle.index,
#               y=df_candle['MA50'], mode='lines', name='MA50', line=dict(color='orange')))
# fig.add_trace(go.Scatter(x=df_candle.index,
#               y=df_candle['MA200'], mode='lines', name='MA200', line=dict(color='red')))

# # Cập nhật layout
# fig.update_layout(
#     title='Biểu đồ Nến Tương tác của Cổ phiếu Apple (AAPL)',
#     yaxis_title='Giá ($)',
#     xaxis_title='Ngày',
#     xaxis_rangeslider_visible=False  # Tắt thanh trượt mặc định để gọn hơn
# )

# fig.show()
