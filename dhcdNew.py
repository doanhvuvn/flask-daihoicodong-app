from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import os
import re

app = Flask(__name__)
DATABASE_FILE = 'daihoi.db'

# --- HÀM HELPER ĐỂ KẾT NỐI CSDL ---


def get_db_connection():
    """Tạo kết nối tới CSDL SQLite. Trả về các dòng dưới dạng dictionary."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # Giúp truy cập các cột bằng tên
    return conn

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


@app.route('/xac-nhan/<ma_cd>')
def confirmation_page(ma_cd):
    conn = get_db_connection()
    shareholder = conn.execute(
        'SELECT * FROM shareholders WHERE ma_co_dong = ?', (ma_cd,)).fetchone()
    confirmed = conn.execute(
        'SELECT 1 FROM confirmations WHERE ma_co_dong = ?', (ma_cd,)).fetchone()
    conn.close()

    if shareholder:
        thong_tin_co_dong = dict(shareholder)
        # Định dạng lại số cổ phần để hiển thị
        thong_tin_co_dong['so_luong_cp'] = f"{thong_tin_co_dong['so_luong_cp']:,} cổ phần"
        da_xac_nhan = confirmed is not None
        return render_template('confirmation_form.html', da_xac_nhan=da_xac_nhan, **thong_tin_co_dong)
    else:
        return "<h1>Mã cổ đông không hợp lệ.</h1>", 404

# --- ROUTE BIỂU QUYẾT ĐÃ ĐƯỢC CẬP NHẬT LOGIC ---


@app.route('/bieu-quyet/<ma_cd>')
def online_ballot_page(ma_cd):
    conn = get_db_connection()

    # KIỂM TRA 1: CỔ ĐÔNG CÓ TỒN TẠI KHÔNG?
    shareholder = conn.execute(
        'SELECT * FROM shareholders WHERE ma_co_dong = ?', (ma_cd,)).fetchone()
    if not shareholder:
        conn.close()
        return "<h1>Mã cổ đông không hợp lệ.</h1>", 404

    # KIỂM TRA 2: CỔ ĐÔNG ĐÃ ĐĂNG KÝ THAM DỰ CHƯA?
    registered = conn.execute(
        'SELECT 1 FROM registrations WHERE ma_co_dong = ?', (ma_cd,)).fetchone()
    if not registered:
        conn.close()
        return "<h1>Cổ đông chưa đăng ký tham dự đại hội, không thể biểu quyết.</h1>", 403

    # Lấy các thông tin còn lại
    ballot_items = conn.execute(
        'SELECT * FROM ballot_items ORDER BY id').fetchall()
    voted = conn.execute(
        'SELECT 1 FROM votes WHERE ma_co_dong = ?', (ma_cd,)).fetchone()
    conn.close()

    thong_tin_co_dong = dict(shareholder)
    thong_tin_co_dong['so_luong_cp'] = f"{thong_tin_co_dong['so_luong_cp']:,} cổ phần"
    has_voted = voted is not None

    return render_template('ballot_online.html',
                           shareholder_info=thong_tin_co_dong,
                           ballot_content=[dict(row) for row in ballot_items],
                           has_voted=has_voted)

# --- ROUTE KẾT QUẢ BIỂU QUYẾT ĐÃ ĐƯỢC CẬP NHẬT LOGIC ---


@app.route('/ket-qua-bieu-quyet')
def ballot_results_page():
    conn = get_db_connection()

    # 1. TÍNH TỔNG SỐ CỔ PHẦN CỦA CÁC CỔ ĐÔNG ĐÃ ĐĂNG KÝ
    query_total_registered_shares = """
        SELECT SUM(s.so_luong_cp) 
        FROM shareholders s 
        JOIN registrations r ON s.ma_co_dong = r.ma_co_dong
    """
    total_shares_result = conn.execute(
        query_total_registered_shares).fetchone()
    total_registered_shares = total_shares_result[0] if total_shares_result[0] else 0

    results = []
    if total_registered_shares > 0:
        # Lấy nội dung các tờ trình
        ballot_items = conn.execute(
            'SELECT * FROM ballot_items ORDER BY id').fetchall()

        # Lấy kết quả biểu quyết đã tổng hợp
        query_vote_summary = """
            SELECT id_totrinh, bieuquyet, SUM(so_co_phan) as total_shares
            FROM votes
            GROUP BY id_totrinh, bieuquyet
        """
        vote_summary = conn.execute(query_vote_summary).fetchall()

        # Chuyển đổi kết quả sang dạng dễ xử lý
        summary_dict = {}
        for row in vote_summary:
            if row['id_totrinh'] not in summary_dict:
                summary_dict[row['id_totrinh']] = {1: 0, 2: 0, 3: 0}
            summary_dict[row['id_totrinh']
                         ][row['bieuquyet']] = row['total_shares']

        # Tính toán và gộp dữ liệu
        for item in ballot_items:
            item_id = item['id']
            item_votes = summary_dict.get(item_id, {1: 0, 2: 0, 3: 0})

            disagree_percent = (item_votes.get(
                2, 0) / total_registered_shares) * 100
            no_opinion_percent = (item_votes.get(
                3, 0) / total_registered_shares) * 100
            agree_percent = 100 - disagree_percent - no_opinion_percent

            results.append({
                'totrinh': item['totrinh'],
                'noidung': item['noidung'],
                'agree_percent': agree_percent,
                'disagree_percent': disagree_percent,
                'no_opinion_percent': no_opinion_percent
            })

    conn.close()
    return render_template('ballot_results.html', results=results)


# --- CÁC API ENDPOINT ---

@app.route('/api/shareholder/<ma_cd>')
def get_shareholder_info(ma_cd):
    conn = get_db_connection()
    shareholder = conn.execute(
        'SELECT * FROM shareholders WHERE ma_co_dong = ?', (ma_cd,)).fetchone()
    registered = conn.execute(
        'SELECT 1 FROM registrations WHERE ma_co_dong = ?', (ma_cd,)).fetchone()
    conn.close()

    if shareholder:
        thong_tin_co_dong = dict(shareholder)
        thong_tin_co_dong['da_dang_ky'] = registered is not None
        thong_tin_co_dong['so_luong_cp'] = f"{thong_tin_co_dong['so_luong_cp']:,} cổ phần"
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

    conn = get_db_connection()
    try:
        existing = conn.execute(
            'SELECT 1 FROM registrations WHERE ma_co_dong = ?', (ma_cd,)).fetchone()
        if existing:
            return jsonify({'success': False, 'message': 'Mã cổ đông này đã được đăng ký trước đó.'}), 409

        now = datetime.now()
        thoi_gian_dang_ky = now.strftime("%d/%m/%Y %H:%M:%S")
        conn.execute('INSERT INTO registrations (ma_co_dong, thoi_gian_dang_ky) VALUES (?, ?)',
                     (ma_cd, thoi_gian_dang_ky))
        conn.commit()
        return jsonify({'success': True, 'message': 'Đăng ký thành công'}), 200
    except Exception as e:
        print(f"Lỗi khi ghi vào CSDL (registrations): {e}")
        return jsonify({'success': False, 'message': 'Lỗi server khi ghi dữ liệu'}), 500
    finally:
        conn.close()


@app.route('/api/confirm', methods=['POST'])
def confirm_attendance():
    # ... (giữ nguyên không đổi)
    data = request.get_json()
    ma_cd = data.get('ma_co_dong')
    if not ma_cd:
        return jsonify({'success': False, 'message': 'Không có mã cổ đông'}), 400

    conn = get_db_connection()
    try:
        existing = conn.execute(
            'SELECT 1 FROM confirmations WHERE ma_co_dong = ?', (ma_cd,)).fetchone()
        if existing:
            return jsonify({'success': False, 'message': 'Cổ đông đã xác nhận trước đó.'}), 409

        now = datetime.now()
        thoi_gian_xac_nhan = now.strftime("%d/%m/%Y %H:%M:%S")
        conn.execute('INSERT INTO confirmations (ma_co_dong, thoi_gian_xac_nhan) VALUES (?, ?)',
                     (ma_cd, thoi_gian_xac_nhan))
        conn.commit()
        return jsonify({'success': True, 'message': 'Xác nhận thành công'}), 200
    except Exception as e:
        print(f"Lỗi khi ghi vào CSDL (confirmations): {e}")
        return jsonify({'success': False, 'message': 'Lỗi server khi ghi dữ liệu'}), 500
    finally:
        conn.close()

# --- API BIỂU QUYẾT ĐÃ ĐƯỢC CẬP NHẬT LOGIC ---


@app.route('/api/submit-ballot', methods=['POST'])
def submit_ballot():
    data = request.get_json()
    ma_cd = data.get('ma_co_dong')
    so_cp_raw = data.get('so_co_phan')
    votes = data.get('votes')

    if not all([ma_cd, so_cp_raw, votes]):
        return jsonify({'success': False, 'message': 'Dữ liệu gửi lên không hợp lệ'}), 400

    conn = get_db_connection()
    try:
        # KIỂM TRA LẠI XEM CỔ ĐÔNG ĐÃ ĐĂNG KÝ CHƯA TRƯỚC KHI GHI NHẬN BIỂU QUYẾT
        registered = conn.execute(
            'SELECT 1 FROM registrations WHERE ma_co_dong = ?', (ma_cd,)).fetchone()
        if not registered:
            return jsonify({'success': False, 'message': 'Cổ đông chưa đăng ký tham dự.'}), 403

        existing_vote = conn.execute(
            'SELECT 1 FROM votes WHERE ma_co_dong = ?', (ma_cd,)).fetchone()
        if existing_vote:
            return jsonify({'success': False, 'message': 'Cổ đông đã biểu quyết trước đó.'}), 409

        so_cp = int(re.sub(r'\D', '', so_cp_raw))

        records_to_insert = []
        for vote in votes:
            records_to_insert.append(
                (ma_cd, so_cp, vote['id'], vote['bieuquyet']))

        conn.executemany('INSERT INTO votes (ma_co_dong, so_co_phan, id_totrinh, bieuquyet) VALUES (?, ?, ?, ?)',
                         records_to_insert)
        conn.commit()
        return jsonify({'success': True, 'message': 'Biểu quyết thành công'}), 200
    except Exception as e:
        print(f"Lỗi khi ghi vào CSDL (votes): {e}")
        return jsonify({'success': False, 'message': 'Lỗi server khi ghi dữ liệu'}), 500
    finally:
        conn.close()

# --- ROUTES CHO VIỆC IN RIÊNG LẺ ---


@app.route('/phieu-dang-ky/<ma_cd>')
def show_registration_slip(ma_cd):
    conn = get_db_connection()
    shareholder = conn.execute(
        'SELECT * FROM shareholders WHERE ma_co_dong = ?', (ma_cd,)).fetchone()
    conn.close()
    if shareholder:
        thong_tin_co_dong = dict(shareholder)
        thong_tin_co_dong['so_luong_cp'] = f"{thong_tin_co_dong['so_luong_cp']:,} cổ phần"
        return render_template('template.html', **thong_tin_co_dong)
    else:
        return "<h1>Không tìm thấy thông tin cổ đông</h1>", 404


@app.route('/the-bieu-quyet/<ma_cd>')
def show_voting_card(ma_cd):
    conn = get_db_connection()
    shareholder = conn.execute(
        'SELECT * FROM shareholders WHERE ma_co_dong = ?', (ma_cd,)).fetchone()
    conn.close()
    if shareholder:
        thong_tin_co_dong = dict(shareholder)
        thong_tin_co_dong['so_luong_cp'] = f"{thong_tin_co_dong['so_luong_cp']:,} cổ phần"
        return render_template('voting_card.html', **thong_tin_co_dong)
    else:
        return "<h1>Không tìm thấy thông tin cổ đông</h1>", 404


@app.route('/phieu-bieu-quyet/<ma_cd>')
def show_ballot_form(ma_cd):
    conn = get_db_connection()
    shareholder = conn.execute(
        'SELECT * FROM shareholders WHERE ma_co_dong = ?', (ma_cd,)).fetchone()
    conn.close()
    if shareholder:
        thong_tin_co_dong = dict(shareholder)
        thong_tin_co_dong['so_luong_cp'] = f"{thong_tin_co_dong['so_luong_cp']:,} cổ phần"
        return render_template('ballot_form.html', **thong_tin_co_dong)
    else:
        return "<h1>Không tìm thấy thông tin cổ đông</h1>", 404


if __name__ == '__main__':
    app.run(debug=True)
