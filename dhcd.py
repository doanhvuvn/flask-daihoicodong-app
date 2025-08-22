import streamlit as st
import streamlit.components.v1 as components
import pyodbc
import pymssql
import pandas as pd
import subprocess
import os

st.title("Đăng ký cổ đông tham dự ĐHCĐ Becamex IJC năm 2025")

connection_string = (
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    r'SERVER=180.148.4.140,16923;'
    r'DATABASE=daihoicodong;'
    r'UID=sa;'
    r'PWD=d@5th@3o;'
)

# SERVER = "180.148.4.140"
# PORT = 16923
# USER = "sa"
# PASSWORD = "d@5th@3o"
# DATABASE = "daihoicodong"


# sql_query = 'select * from tbl_codong'

# df = None

# connection = pyodbc.connect(connection_string)
# df = pd.read_sql(sql_query, connection)
# connection.close()

macodong = st.text_input("Nhập mã cổ đông để bắt đầu")
js_code = """
    <script>
        setTimeout(function() {
            const input = window.parent.document.querySelector('input[aria-label="Nhập mã cổ đông để bắt đầu"]');
            if (input) {    
                input.focus();
            }
        }   , 0);
    </script>"""
components.html(js_code, height=1, width=1)

if len(macodong) == 5:
    sql_query = "select macd as [Mã CĐ],hoten as [Tên CĐ],diachi as [Địa chỉ],socophan as [Số CP] from tbl_codong where macd='" + macodong + "'"

    df = None

    # connection = pymssql.connect(
    #     server=SERVER, user=USER, password=PASSWORD, database=DATABASE)
    # connection = pyodbc.connect(connection_string)
    # df = pd.read_sql(sql_query, connection)
    # connection.close()

    # with pymssql.connect(server=SERVER, port=PORT, user=USER, password=PASSWORD, database=DATABASE) as conn:
    #     with conn.cursor(as_dict=True) as cursor:
    #         cursor.execute(sql_query)
    #         data_rows = cursor.fetchall()
    # df = pd.DataFrame(data_rows)

    df = None

    connection = pyodbc.connect(connection_string)
    df = pd.read_sql(sql_query, connection)
    connection.close()

    if len(df) > 0:
        st.write(df.loc[0])

        df1 = None
        sql_query = "select * from vw_dangky where macd='" + macodong + "'"
        connection = pyodbc.connect(connection_string)
        df1 = pd.read_sql(sql_query, connection)
        connection.close()
        if len(df1) == 0:
            if st.button("Đăng ký"):
                st.write("Đăng ký xong")
        else:
            if st.button("In lại"):
                df2 = None
                sql_query = "select id from tbl_codong where macd='" + macodong + "'"
                connection = pyodbc.connect(connection_string)
                df2 = pd.read_sql(sql_query, connection)
                connection.close()
                idcodong = df2.loc[0, 'id']

                runner_exe_path = "E:\App\Hello Python\dhcdlite\DaihoiCD.exe"
                os.startfile(
                    "E:\App\Hello Python\dhcdlite\DaihoiCD.exe", "", " " + str(idcodong))
                # process = subprocess.run(
                #     [runner_exe_path, idcodong], capture_output=True, text=True)

    else:
        st.write("Mã cổ đông không tồn tại")
# try:


# except Exception as e:

    # st.write("Mã cổ đông không tồn tại")

#     # Hiển thị kết quả
#     st.header(f"Chỉ số BMI của bạn là: {bmi:.2f}")

#     # Đưa ra nhận xét dựa trên chỉ số BMI
#     if bmi < 18.5:
#         st.warning("Bạn đang ở trong nhóm Gầy (Underweight).")
#     elif 18.5 <= bmi < 24.9:
#         st.success("Bạn đang ở trong nhóm Bình thường (Normal weight). ")
#     elif 25 <= bmi < 29.9:
#         st.warning("Bạn đang ở trong nhóm Thừa cân (Overweight).")
#     else:
#         st.error("Bạn đang ở trong nhóm Béo phì (Obesity).")
