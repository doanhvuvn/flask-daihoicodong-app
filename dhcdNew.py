from flask import Flask, render_template, request, jsonify
import pandas as pd
from datetime import datetime
import os
import re

app = Flask(__name__)

# --- HÀM MỚI ĐỂ ĐỊNH DẠNG SỐ CỔ PHẦN ---


def format_shares(value):
    """Hàm này lấy một chuỗi, trích xuất số, định dạng lại rồi thêm chữ 'cổ phần'."""
    try:
        # Dùng re.sub để xóa tất cả các ký tự không phải là số
        numeric_part = re.sub(r'\D', '', str(value))
        if numeric_part:
            # Chuyển chuỗi số thành số nguyên
            number = int(numeric_part)
            # Định dạng số với dấu phẩy phân tách hàng nghìn và thêm lại đơn vị
            return f"{number:,} cổ phần"
    except (ValueError, TypeError):
        # Nếu có lỗi, trả về giá trị gốc
        pass
    return value

# --- HÀM ĐỌC DỮ LIỆU CỔ ĐÔNG (DANHSACH.XLSX) ---


# --- CẬP NHẬT HÀM ĐỌC DỮ LIỆU CỔ ĐÔNG ---
def load_shareholder_data(filename='danhsach.xlsx'):
    database = {}
    try:
        df = pd.read_excel(filename, dtype=str)
        df.fillna('', inplace=True)

        # Giả sử bạn cần đổi tên cột (giữ lại nếu cần)
        # column_mapping = {'Số lượng Cổ phần': 'so_luong_cp', ...}
        # df.rename(columns=column_mapping, inplace=True)

        column_mapping = {
            'macd': 'ma_co_dong',
            'hoten': 'ho_ten',
            'sodksh': 'cmnd',
            'ngaycap': 'ngay_cap',
            'socophan': 'so_luong_cp'
        }
        # Dùng hàm rename để đổi tên các cột trong DataFrame
        df.rename(columns=column_mapping, inplace=True)

        # --- DÒNG MỚI: ÁP DỤNG HÀM ĐỊNH DẠNG CHO CỘT SỐ LƯỢNG CỔ PHẦN ---
        # Kiểm tra xem cột 'so_luong_cp' có tồn tại không trước khi định dạng
        if 'so_luong_cp' in df.columns:
            df['so_luong_cp'] = df['so_luong_cp'].apply(format_shares)

        records = df.to_dict(orient='records')
        for record in records:
            key = str(record['ma_co_dong'])
            database[key] = record

    except Exception as e:
        print(f"Lỗi khi đọc {filename}: {e}")
    return database

# --- HÀM MỚI: ĐỌC DANH SÁCH MÃ CỔ ĐÔNG ĐÃ ĐĂNG KÝ (DANGKY.XLSX) ---


def load_registered_ids(filename='dangky.xlsx'):
    if not os.path.exists(filename):
        return set()  # Trả về một tập hợp rỗng nếu file không tồn tại
    try:
        df = pd.read_excel(filename, dtype={'ma_co_dong': str})
        # Trả về một tập hợp (set) các mã đã đăng ký để kiểm tra nhanh hơn
        return set(df['ma_co_dong'].tolist())
    except Exception as e:
        print(f"Lỗi khi đọc {filename}: {e}")
        return set()


# --- NẠP DỮ LIỆU KHI ỨNG DỤNG KHỞI ĐỘNG ---
DATABASE = load_shareholder_data()
REGISTERED_IDS = load_registered_ids()  # Nạp danh sách đã đăng ký

# --- CÁC ROUTE CỦA ỨNG DỤNG ---


@app.route('/')
def trang_chu():
    return render_template('index.html')

# --- CẬP NHẬT API TRA CỨU ---


@app.route('/api/shareholder/<ma_cd>')
def get_shareholder_info(ma_cd):
    thong_tin_co_dong = DATABASE.get(ma_cd)
    if thong_tin_co_dong:
        # KIỂM TRA XEM MÃ NÀY CÓ TRONG DANH SÁCH ĐÃ ĐĂNG KÝ KHÔNG
        thong_tin_co_dong['da_dang_ky'] = ma_cd in REGISTERED_IDS
        return jsonify(thong_tin_co_dong)
    else:
        return jsonify({"error": "Shareholder not found"}), 404

# --- ROUTE /register GIỮ NGUYÊN ---


@app.route('/register', methods=['POST'])
def register():
    # ... (giữ nguyên hàm này, không thay đổi)
    data = request.get_json()
    ma_cd = data.get('ma_co_dong')
    if not ma_cd:
        return jsonify({'success': False, 'message': 'Không có mã cổ đông'}), 400
    filename = 'dangky.xlsx'
    try:
        # Tải lại danh sách đã đăng ký để kiểm tra lại lần nữa
        current_registered_ids = load_registered_ids(filename)
        if ma_cd in current_registered_ids:
            return jsonify({'success': False, 'message': 'Mã cổ đông này đã được đăng ký trước đó.'}), 409

        now = datetime.now()
        thoi_gian_dang_ky = now.strftime("%d/%m/%Y %H:%M:%S")
        new_record = {'ma_co_dong': [ma_cd],
                      'thoi_gian_dang_ky': [thoi_gian_dang_ky]}
        df_new = pd.DataFrame(new_record)

        df_existing = pd.DataFrame(columns=['ma_co_dong', 'thoi_gian_dang_ky'])
        if os.path.exists(filename):
            df_existing = pd.read_excel(filename, dtype={'ma_co_dong': str})

        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined['ma_co_dong'] = df_combined['ma_co_dong'].astype(str)
        df_combined.to_excel(filename, index=False)

        # CẬP NHẬT LẠI BIẾN TOÀN CỤC SAU KHI GHI THÀNH CÔNG
        REGISTERED_IDS.add(ma_cd)

        return jsonify({'success': True, 'message': 'Đăng ký thành công'}), 200
    except Exception as e:
        print(f"Lỗi khi ghi file dangky.xlsx: {e}")
        return jsonify({'success': False, 'message': 'Lỗi server khi ghi file'}), 500

# --- ROUTE /phieu-dang-ky GIỮ NGUYÊN ---


@app.route('/phieu-dang-ky/<ma_cd>')
def show_registration_slip(ma_cd):
    # ... (giữ nguyên không đổi)
    thong_tin_co_dong = DATABASE.get(ma_cd)
    if thong_tin_co_dong:
        return render_template('template.html', **thong_tin_co_dong)
    else:
        return "<h1>Không tìm thấy thông tin cổ đông</h1>", 404


if __name__ == '__main__':
    app.run(debug=True)
