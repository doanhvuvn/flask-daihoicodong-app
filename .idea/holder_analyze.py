import pandas as pd
import pyodbc
import seaborn as sbn
import matplotlib.pyplot as plt

connection_string = (
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    r'SERVER=192.168.1.8;'
    r'DATABASE=daihoicodong;'
    r'UID=sa;'
    r'PWD=d@5th@3o;'
)

sql_query = 'select * from tbl_codong'

df = None

connection = pyodbc.connect(connection_string)
df = pd.read_sql(sql_query, connection)
connection.close()

if df is not None:

    df['namdangky'] = df['ngaycap'].dt.year
    print(df.head())

    quoctich_cophan = df.groupby('quoctich')['socophan'].sum()
    print(quoctich_cophan)

    # plt.figure(figsize=(10, 6))
    # quoctich_cophan.plot(kind='bar')
    # plt.title('Biểu đồ các quốc gia nắm giữ cổ phiếu IJC')
    # plt.xlabel('Quốc gia')
    # plt.ylabel('Số cổ phiếu')
    # plt.grid(True)
    # plt.show()

    plt.figure(figsize=(10, 6))
    sbn.regplot(x='namdangky', y='socophan', data=df)
    plt.title('Biểu đồ các quốc gia nắm giữ cổ phiếu IJC')
    plt.xlabel('Quốc gia')
    plt.ylabel('Số cổ phiếu')
    plt.grid(True)
    plt.show()
