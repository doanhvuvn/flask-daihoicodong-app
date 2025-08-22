from flask import Flask, render_template, request, jsonify
import pandas as pd
from datetime import datetime
import os
import re

app = Flask(__name__)

# --- HÀM HELPER VÀ BIẾN TOÀN CỤC ---


def format_shares(value):
    """Hàm này lấy một chuỗi, trích xuất số, định dạng lại rồi thêm chữ 'cổ phần'."""
    try:
        numeric_part = re.sub(r'\D', '', str(value))
        if numeric_part:
            number = int(numeric_part)
            return f"{number:,} cổ phần"
    except (ValueError, TypeError):
        pass
    return value


def load_shareholder_data(filename='danhsach.xlsx'):
    database = {}
    try:
        df = pd.read_excel(filename, dtype=str)
        df.fillna('', inplace=True)

        column_mapping = {
            'macd': 'ma_co_dong',
            'hoten': 'ho_ten',
            'sodksh': 'cmnd',
                    'ngaycap': 'ngay_cap',
                    'socophan': 'so_luong_cp'
        }
        # Dùng hàm rename để đổi tên các cột trong DataFrame
        df.rename(columns=column_mapping, inplace=True)

        if 'so_luong_cp' in df.columns:
            df['so_luong_cp'] = df['so_luong_cp'].apply(format_shares)

        records = df.to_dict(orient='records')
        for record in records:
            key = str(record['ma_co_dong'])
            database[key] = record

    except Exception as e:
        print(f"Lỗi khi đọc {filename}: {e}")
    return database


def load_registered_ids(filename='dangky.xlsx'):
    if not os.path.exists(filename):
        return set()
    try:
        df = pd.read_excel(filename, dtype={'ma_co_dong': str})
        return set(df['ma_co_dong'].tolist())
    except Exception as e:
        print(f"Lỗi khi đọc {filename}: {e}")
        return set()


DATABASE = load_shareholder_data()
REGISTERED_IDS = load_registered_ids()

# --- CÁC ROUTE CỦA ỨNG DỤNG ---


@app.route('/')
def main_menu():
    return render_template('main_menu.html')


@app.route('/dang-ky')
def registration_page():
    return render_template('index.html')


@app.route('/bao-cao')
def report_page():
    return "<h1>Chức năng Báo cáo đang được phát triển</h1>"


@app.route('/tinh-trang')
def status_page():
    return "<h1>Chức năng Tình trạng đăng ký đang được phát triển</h1>"


@app.route('/api/shareholder/<ma_cd>')
def get_shareholder_info(ma_cd):
    thong_tin_co_dong = DATABASE.get(ma_cd)
    if thong_tin_co_dong:
        thong_tin_co_dong['da_dang_ky'] = ma_cd in REGISTERED_IDS
        return jsonify(thong_tin_co_dong)
    else:
        return jsonify({"error": "Shareholder not found"}), 404


@app.route('/register', methods=['POST'])
def register():
    # ... (giữ nguyên không đổi)
    data = request.get_json()
    ma_cd = data.get('ma_co_dong')
    if not ma_cd:
        return jsonify({'success': False, 'message': 'Không có mã cổ đông'}), 400
    filename = 'dangky.xlsx'
    try:
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
        REGISTERED_IDS.add(ma_cd)
        return jsonify({'success': True, 'message': 'Đăng ký thành công'}), 200
    except Exception as e:
        print(f"Lỗi khi ghi file dangky.xlsx: {e}")
        return jsonify({'success': False, 'message': 'Lỗi server khi ghi file'}), 500

# --- ROUTES CHO VIỆC IN RIÊNG LẺ ---


@app.route('/phieu-dang-ky/<ma_cd>')
def show_registration_slip(ma_cd):
    thong_tin_co_dong = DATABASE.get(ma_cd)
    if thong_tin_co_dong:
        return render_template('template.html', **thong_tin_co_dong)
    else:
        return "<h1>Không tìm thấy thông tin cổ đông</h1>", 404


@app.route('/the-bieu-quyet/<ma_cd>')
def show_voting_card(ma_cd):
    thong_tin_co_dong = DATABASE.get(ma_cd)
    if thong_tin_co_dong:
        return render_template('voting_card.html', **thong_tin_co_dong)
    else:
        return "<h1>Không tìm thấy thông tin cổ đông</h1>", 404

# --- ROUTE MỚI CHO PHIẾU BIỂU QUYẾT ---


@app.route('/phieu-bieu-quyet/<ma_cd>')
def show_ballot_form(ma_cd):
    thong_tin_co_dong = DATABASE.get(ma_cd)
    if thong_tin_co_dong:
        return render_template('ballot_form.html', **thong_tin_co_dong)
    else:
        return "<h1>Không tìm thấy thông tin cổ đông</h1>", 404


if __name__ == '__main__':
    app.run(debug=True)
