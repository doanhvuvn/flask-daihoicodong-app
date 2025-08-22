# 1. Import thư viện vnstock
from vnstock import *
import matplotlib.pyplot as plt

from vnstock import Vnstock
stock = Vnstock().stock(symbol='IJC', source='VCI')
df = stock.quote.history(start='2024-01-01', end='2025-08-20', interval='1D')

if not df.empty:
    df['MA50'] = df['close'].rolling(window=50).mean()
    df['MA200'] = df['close'].rolling(window=200).mean()
    plt.figure(figsize=(14, 7))
    plt.plot(df['close'])
    plt.plot(df['MA50'], label='MA50', color='orange')
    plt.plot(df['MA200'], label='MA200', color='red')
    plt.title('Lịch sử Giá đóng cửa của Cổ phiếu IJC')
    plt.xlabel('Ngày')
    plt.ylabel('Giá')
    plt.legend()
    plt.show()
