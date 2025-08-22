column_mapping = {
    'macd': 'ma_co_dong',
    'hoten': 'ho_ten',
    'sodksh': 'cmnd',
              'ngaycap': 'ngay_cap',
              'socophan': 'so_luong_cp'
}
# Dùng hàm rename để đổi tên các cột trong DataFrame
df.rename(columns=column_mapping, inplace=True)
