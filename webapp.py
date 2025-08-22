import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.title("BẢNG PHÂN TÍCH DOANH THU BÁN HÀNG")
st.write("Đây là trang web tự động hiển thị kết quả phân tích từ file 'sales_data.csv'")

try:

    df = pd.read_csv('sales_data.csv')

    df['Date'] = pd.to_datetime(df['Date'])
    df['Revenue'] = df['Price']*df['Quantity']

    df['Month'] = df['Date'].dt.month

    st.header("1.Dữ liệu bán hàng gốc")
    st.dataframe(df)

    st.header("2.Phân tích doanh thu theo tháng")
    revenue_by_month = df.groupby('Month')['Revenue'].sum().reset_index()
    st.write("Bảng tổng hợp doanh thu")
    st.dataframe(revenue_by_month)

    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.plot(revenue_by_month['Month'],
             revenue_by_month['Revenue'],  marker='o')
    ax1.set_title('Tổng Doanh thu theo Tháng')
    ax1.set_xlabel('Tháng')
    ax1.set_ylabel('Doanh thu ($)')
    ax1.grid(True)
    ax1.set_xticks(revenue_by_month['Month'])

    st.pyplot(fig1)

    st.header("3.Phân tích sản phẩm bán chạy")
    product_sales = df.groupby('Product')['Quantity'].sum(
    ).sort_values(ascending=False).reset_index()
    st.write("Bảng tổng hợp dố lượng bán")
    st.dataframe(product_sales)

    fig2, ax2 = plt.subplots(figsize=(10, 6))
    ax2.bar(product_sales['Product'], product_sales['Quantity'], color=[
            'skyblue', 'lightgreen', 'salmon', 'gold'])
    ax2.set_title('Top Sản phẩm Bán chạy')
    ax2.set_xlabel('Sản phẩm')
    ax2.set_ylabel('Tổng số lượng đã bán')

    st.pyplot(fig2)

except FileNotFoundError:
    st.error("Không tìm thấy file")
# except Exception as e:
    # st.error(f"Đã xảy ra lỗi {e}")
