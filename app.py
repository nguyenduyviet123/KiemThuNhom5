# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from db import get_connection
import pyodbc
import time
from flask import request, jsonify
from uuid import uuid4
from datetime import datetime, timedelta
from flask import Response
import threading
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__, static_folder='static', template_folder='templates')

app.secret_key = "replace_this_with_random_secret"

def rows_to_dicts(cursor):
    cols = [col[0] for col in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]

#------------------Trang chủ(DashBoard)-----------------
@app.route("/dashboard")
def index():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM SANPHAM")
        products_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM LOAISANPHAM_")
        types_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM TAI_KHOAN")
        accounts_count = cur.fetchone()[0]
    finally:
        cur.close()
        conn.close()
    return render_template("dashboard.html", products_count=products_count,
                           types_count=types_count, accounts_count=accounts_count)

# ---------------- LOAI SAN PHAM ----------------
@app.route("/loaisp")
def loaisp_list():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT MaLoai, TenLoai FROM LOAISANPHAM_ ORDER BY MaLoai")
    items = rows_to_dicts(cur)
    cur.close(); conn.close()
    return render_template("loaisp_list.html", items=items)

from flask import Flask, render_template, request, redirect, url_for, flash
from uuid import uuid4

#===============Thêm Loại Sản phẩm===============
@app.route("/loaisp/add", methods=["GET", "POST"])
def loaisp_add():
    if request.method == "POST":

        # 👉 Phân biệt request JSON (Postman) hay Form (HTML)
        is_json = request.is_json

        if is_json:
            data = request.get_json()
            ma = data.get("MaLoai") or str(uuid4())[:8]
            ten = data.get("TenLoai")
        else:
            ma = request.form.get("MaLoai") or str(uuid4())[:8]
            ten = request.form.get("TenLoai")

        if not ten:
            if is_json:
                return jsonify({
                    "status": "error",
                    "message": "Thiếu tên loại sản phẩm"
                }), 400
            else:
                flash("Thiếu tên loại sản phẩm", "danger")
                return redirect(url_for("loaisp_add"))

        conn = get_connection()
        cur = conn.cursor()

        # ✅ KIỂM TRA TRÙNG MÃ LOẠI
        cur.execute(
            "SELECT MaLoai FROM LOAISANPHAM_ WHERE MaLoai = ?",
            (ma,)
        )
        exists = cur.fetchone()

        if exists:
            cur.close()
            conn.close()

            if is_json:
                return jsonify({
                    "status": "error",
                    "message": f"Mã loại {ma} đã tồn tại"
                }), 400
            else:
                flash(f"Mã loại sản phẩm {ma} đã tồn tại! Vui lòng nhập mã khác.", "danger")
                return redirect(url_for("loaisp_add"))

        # ✅ INSERT
        cur.execute(
            "INSERT INTO LOAISANPHAM_ (MaLoai, TenLoai) VALUES (?, ?)",
            (ma, ten)
        )
        conn.commit()
        cur.close()
        conn.close()

        if is_json:
            return jsonify({
                "status": "success",
                "message": "Thêm loại sản phẩm thành công",
                "data": {
                    "MaLoai": ma,
                    "TenLoai": ten
                }
            }), 200
        else:
            flash("Thêm loại sản phẩm thành công", "success")
            return redirect(url_for("loaisp_list"))

    # GET request: hiển thị form
    return render_template("loaisp_form.html", item=None)

#=============Sửa Loại Sản Phẩm==============
@app.route("/loaisp/edit/<ma>", methods=["GET","POST"])
def loaisp_edit(ma):
    conn = get_connection()
    cur = conn.cursor()
    if request.method == "POST":
        ten = request.form.get("TenLoai")
        cur.execute("UPDATE LOAISANPHAM_ SET TenLoai = ? WHERE MaLoai = ?", ten, ma)
        conn.commit()
        cur.close(); conn.close()
        flash("Cập nhật thành công", "success")
        return redirect(url_for("loaisp_list"))
    cur.execute("SELECT MaLoai, TenLoai FROM LOAISANPHAM_ WHERE MaLoai = ?", ma)
    rows = rows_to_dicts(cur)
    cur.close(); conn.close()
    item = rows[0] if rows else None
    return render_template("loaisp_form.html", item=item)

#===============Xóa Loại Sản Phẩm============
@app.route("/loaisp/delete/<ma>", methods=["POST"])
def loaisp_delete(ma):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM LOAISANPHAM_ WHERE MaLoai = ?", ma)
    conn.commit()
    cur.close(); conn.close()
    flash("Đã xóa loại sản phẩm", "warning")
    return redirect(url_for("loaisp_list"))

#==================API======================
@app.route("/api/loaisp", methods=["GET"])
def api_check_loai():
    ma_loai = request.args.get("MaLoai")

    if not ma_loai:
        return {"message": "Vui lòng cung cấp MaLoai"}, 400

    try:
        ma_loai = int(ma_loai)
    except:
        return {"message": "MaLoai phải là số"}, 400

    conn = get_connection()
    cur = conn.cursor()

    # Lấy loại bánh trực tiếp từ DB (dynamic)
    cur.execute("""
        SELECT TenLoai
        FROM LOAISANPHAM_        
        WHERE MaLoai = ?
    """, (ma_loai,))

    row = cur.fetchone()

    cur.close()
    conn.close()

    if row:
        ten_loai = row[0]
        return {"message": f"Tìm thấy loại bánh: {ten_loai}"}

    return {"message": "Không tìm thấy loại bánh trong database"}


# ---------------- SAN PHAM ----------------

@app.route("/sanpham")
def sanpham_list():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            s.MaSP, s.TenSP_, s.DonGia, s.GiaCu, s.MoTa, s.Anh,
            s.MaLoai, l.TenLoai, s.ThoiGianCapNhat
        FROM SANPHAM s
        LEFT JOIN LOAISANPHAM_ l ON s.MaLoai = l.MaLoai
        WHERE s.TrangThai = 1       -- chỉ lấy sản phẩm chưa xóa
        ORDER BY s.MaSP
    """)

    products = rows_to_dicts(cur)
    cur.close()
    conn.close()
    return render_template("sanpham_list.html", products=products)


        #=============Thêm sản phẩm================

@app.route("/sanpham/add", methods=["GET", "POST"])
def sanpham_add():
    conn = get_connection()
    cur = conn.cursor()

    # Nếu GET → trả form
    if request.method == "GET":
        cur.execute("SELECT MaLoai, TenLoai FROM LOAISANPHAM_")
        loai = rows_to_dicts(cur)
        cur.close()
        conn.close()
        return render_template("sanpham_form.html", item=None, loai=loai)

    # Nếu POST → JSON (API) hoặc FORM (Web)
    if request.is_json:
        data = request.get_json()
        ma = data.get("MaSP")
        ten = data.get("TenSP")
        dongia = data.get("DonGia")
        giacu = data.get("GiaCu", 0)
        mota = data.get("MoTa", "")
        anh = data.get("Anh", "")
        maloai = data.get("MaLoai", "")
        from_api = True
    else:
        ma = request.form.get("MaSP") or str(uuid4())[:8]
        ten = request.form.get("TenSP_")
        dongia = request.form.get("DonGia") or 0
        giacu = request.form.get("GiaCu") or 0
        mota = request.form.get("MoTa")
        anh = request.form.get("Anh")
        maloai = request.form.get("MaLoai")
        from_api = False

    # ❗ KIỂM TRA TÊN SẢN PHẨM TRỐNG
    if not ten or ten.strip() == "":
        if from_api:
            return jsonify({"error": "Tên sản phẩm không được để trống!"}), 400
        else:
            flash("Tên sản phẩm không được để trống!", "danger")
            cur.close()
            conn.close()
            return redirect(url_for("sanpham_add"))

    # KIỂM TRA TRÙNG MÃ
    cur.execute("SELECT MaSP FROM SANPHAM WHERE MaSP = ?", ma)
    if cur.fetchone():
        cur.close()
        conn.close()
        if from_api:
            return jsonify({"error": f"Mã sản phẩm {ma} đã tồn tại!"}), 400
        else:
            flash(f"Mã sản phẩm {ma} đã tồn tại!", "danger")
            return redirect(url_for("sanpham_add"))

    # INSERT
    cur.execute("""
        INSERT INTO SANPHAM (MaSP, TenSP_, DonGia, GiaCu, MoTa, Anh, MaLoai, ThoiGianCapNhat)
        VALUES (?, ?, ?, ?, ?, ?, ?, GETDATE())
    """, ma, ten, dongia, giacu, mota, anh, maloai)
    conn.commit()

    cur.close()
    conn.close()

    # Trả về tùy request
    if from_api:
        return jsonify({"msg": "Thêm API thành công!"})
    else:
        flash("Thêm sản phẩm thành công", "success")
        return redirect(url_for("sanpham_list"))
    



#=============Sửa sản phẩm================
# --- HÀM SỬA SẢN PHẨM (ĐÃ NÂNG CẤP VALIDATION) ---
@app.route("/api/sanpham/edit/<ma>", methods=["POST"])
@app.route("/sanpham/edit/<ma>", methods=["GET", "POST"], endpoint='sanpham_edit')
def sanpham_edit_hybrid(ma):
    conn = None
    cur = None
    is_api = request.path.startswith('/api/')

    try:
        conn = get_connection()
        cur = conn.cursor()

        if request.method == "POST":
            # 1. Lấy dữ liệu
            if request.is_json:
                data = request.json
                ten = data.get("TenSP_")
                raw_dongia = data.get("DonGia")
                giacu = data.get("GiaCu", 0)
                mota = data.get("MoTa")
                anh = data.get("Anh")
                maloai = data.get("MaLoai")
            else:
                ten = request.form.get("TenSP_")
                raw_dongia = request.form.get("DonGia")
                giacu = request.form.get("GiaCu") or 0
                mota = request.form.get("MoTa")
                anh = request.form.get("Anh")
                maloai = request.form.get("MaLoai")

            # --- KIỂM TRA 1: TÊN KHÔNG ĐƯỢC ĐỂ TRỐNG (MỚI THÊM) ---
            if not ten or str(ten).strip() == "":
                msg = "Tên không được để trống"
                if is_api: return jsonify({"status": "error", "message": msg}), 400
                flash(msg, "danger")
                return redirect(url_for("sanpham_edit", ma=ma))

            # --- KIỂM TRA 2: GIÁ PHẢI LÀ SỐ (SỬA LOGIC) ---
            dongia = 0
            try:
                # Cố gắng ép kiểu sang số
                if raw_dongia:
                    dongia = float(str(raw_dongia).replace(',', '').strip())
                else:
                    dongia = 0 # Nếu bỏ trống giá thì cho là 0 (hoặc báo lỗi tùy bạn)
            except ValueError:
                # NẾU NHẬP CHỮ (abc) -> SẼ NHẢY VÀO ĐÂY -> BÁO LỖI NGAY
                msg = "Đơn giá phải là số hợp lệ (không được nhập chữ)"
                if is_api: return jsonify({"status": "error", "message": msg}), 400
                flash(msg, "danger")
                return redirect(url_for("sanpham_edit", ma=ma))
            
            # --- KIỂM TRA 3: GIÁ KHÔNG ĐƯỢC ÂM ---
            if dongia < 0:
                msg = "Giá không được nhỏ hơn 0"
                if is_api: return jsonify({"status": "error", "message": msg}), 400
                flash(msg, "danger")
                return redirect(url_for("sanpham_edit", ma=ma))
            # ... (Các đoạn kiểm tra Validation ở trên giữ nguyên) ...
            
            # --- VALIDATION 3: KIỂM TRA MÃ LOẠI TỒN TẠI (MỚI) ---
            # Lưu ý: Chỉ kiểm tra nếu người dùng có gửi maloai lên
            if maloai:
                # Kiểm tra trong bảng LOAISANPHAM_ xem có ID này không
                cur.execute("SELECT COUNT(*) FROM LOAISANPHAM_ WHERE MaLoai = ?", maloai)
                count = cur.fetchone()[0]
                if count == 0:
                    msg = f"Loại sản phẩm (Mã {maloai}) không tồn tại"
                    if is_api: return jsonify({"status": "error", "message": msg}), 400
                    flash(msg, "danger")
                    return redirect(url_for("sanpham_edit", ma=ma))
            # 4. Update Database (Nếu vượt qua 3 ải trên)
            cur.execute("""
                UPDATE SANPHAM 
                SET TenSP_=?, DonGia=?, GiaCu=?, MoTa=?, Anh=?, MaLoai=?, ThoiGianCapNhat=GETDATE()
                WHERE MaSP = ?
            """, ten, dongia, giacu, mota, anh, maloai, ma)
            
            # --- THÊM ĐOẠN KIỂM TRA NÀY VÀO ---
            if cur.rowcount == 0:
                # Nếu không tìm thấy dòng nào để sửa -> Báo lỗi 404 (Not Found)
                msg = f"Không tìm thấy sản phẩm có mã {ma}"
                if is_api: return jsonify({"status": "error", "message": msg}), 404
                flash(msg, "warning")
                return redirect(url_for("sanpham_list"))
            # ------------------------------------

            conn.commit()

            # 5. Trả về kết quả thành công (Giữ nguyên)
            if is_api:
                return jsonify({
                    "status": "success", 
                    "message": "Cập nhật thành công",
                    "data": {"MaSP": ma, "TenSP": ten, "DonGia": dongia}
                }), 200
            
            flash("Cập nhật thành công", "success")
            return redirect(url_for("sanpham_list"))

        # --- PHẦN GET (HIỂN THỊ FORM) ---
        cur.execute("SELECT * FROM SANPHAM WHERE MaSP = ?", ma)
        rows = rows_to_dicts(cur)
        cur.execute("SELECT MaLoai, TenLoai FROM LOAISANPHAM_")
        loai = rows_to_dicts(cur)

        item = rows[0] if rows else None
        return render_template("sanpham_form.html", item=item, loai=loai)

    except Exception as e:
        if is_api: return jsonify({"status": "error", "message": str(e)}), 500
        return f"Lỗi hệ thống: {str(e)}", 500
    finally:
        if cur: cur.close()
        if conn: conn.close()







#=============Xóa sản phẩm==================

@app.route("/sanpham/delete/<ma>", methods=["POST"])  #Chuyển vào thùng rác
def sanpham_delete(ma):
    conn = get_connection()
    cur = conn.cursor()

    # 🔍 1) Kiểm tra sản phẩm có tồn tại không
    cur.execute("SELECT MaSP, TrangThai FROM SANPHAM WHERE MaSP = ?", (ma,))
    row = cur.fetchone()

    if not row:
        # ❌ Không tìm thấy
        if request.is_json:
            return jsonify({
                "success": False,
                "message": f"Không tìm thấy sản phẩm có mã {ma}"
            }), 404

        flash(f"Không tìm thấy sản phẩm có mã {ma}", "danger")
        return redirect(url_for("sanpham_list"))

    MaSP, TrangThai = row

    # 🔴 2) Nếu sản phẩm ĐÃ nằm trong thùng rác → báo lỗi
    if TrangThai == 0:
        if request.is_json:
            return jsonify({
                "success": False,
                "message": f"Sản phẩm mã {ma} đã ở trong thùng rác"
            }), 400

        flash(f"Sản phẩm mã {ma} đã ở trong thùng rác!", "warning")
        return redirect(url_for("sanpham_list"))

    # 🟦 3) Xóa mềm (đưa vào thùng rác)
    cur.execute("""
        UPDATE SANPHAM
        SET TrangThai = 0, NgayXoa = ?
        WHERE MaSP = ?
    """, (datetime.now(), ma))

    conn.commit()
    cur.close()
    conn.close()

    # JSON response
    if request.is_json:
        return jsonify({
            "success": True,
            "message": f"Đã chuyển sản phẩm mã {ma} vào thùng rác"
        })

    flash(f"Đã chuyển sản phẩm mã {ma} vào thùng rác!", "success")
    return redirect(url_for("sanpham_list"))

@app.route("/sanpham/delete_permanent/<ma>", methods=["POST", "DELETE"]) # Xóa vĩnh viễn
def delete_permanent(ma):
    is_api = request.method == "DELETE" or request.is_json

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM SANPHAM WHERE MaSP = ?", (ma,))
    deleted = cur.rowcount
    conn.commit()
    cur.close(); conn.close()

    if deleted == 0:
        if is_api:
            return jsonify({"success": False, "message": f"Không tìm thấy sản phẩm {ma}"}), 404
        flash(f"Không tìm thấy sản phẩm {ma}", "danger")
        return redirect(url_for("sanpham_trash"))

    # API trả JSON
    if is_api:
        return jsonify({"success": True, "message": f"Đã xóa vĩnh viễn sản phẩm {ma}"}), 200

    # Web POST → flash + redirect
    flash(f"Đã xóa vĩnh viễn sản phẩm {ma}", "success")
    return redirect(url_for("sanpham_trash"))


#================Tu dong xoa================

def auto_delete_old_items():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM SANPHAM
        WHERE TrangThai = 0 AND NgayXoa <= DATEADD(day, -30, GETDATE())
    """)

    conn.commit()
    cur.close()
    conn.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(auto_delete_old_items, 'interval', hours = 24)
    scheduler.start()

start_scheduler()


# thùng rác
@app.route("/sanpham/trash")
def sanpham_trash():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT sp.MaSP, sp.TenSP_, sp.Anh, sp.NgayXoa, l.TenLoai
        FROM SANPHAM sp
        LEFT JOIN LOAISANPHAM_ l ON sp.MaLoai = l.MaLoai
        WHERE sp.TrangThai = 0 AND sp.NgayXoa IS NOT NULL
    """)

    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    items = [dict(zip(columns, row)) for row in rows]

    for p in items:
        ngay_xoa = p.get("NgayXoa")

        if ngay_xoa:
            expire_date = ngay_xoa + timedelta(days=30)
            days_left = (expire_date - datetime.now()).days

            if days_left >= 0:
                p["time_left"] = f"Còn {days_left} ngày"
            else:
                p["time_left"] = "Đang chờ hệ thống xóa"
        else:
            p["time_left"] = "Không xác định"

    cursor.close()
    conn.close()

    return render_template("sanpham_trash.html", items=items)


#=============Khôi phục dữ liệu==============
@app.route("/sanpham/restore/<ma>", methods=["POST"])
def sanpham_restore(ma):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE SANPHAM 
        SET TrangThai = 1, NgayXoa = NULL
        WHERE MaSP = ?
    """, ma)

    conn.commit()
    cur.close(); conn.close()
    flash("Khôi phục sản phẩm thành công!", "success")
    return redirect(url_for("sanpham_trash"))





# ✅ API trả về chi tiết sản phẩm (cho modal “Xem chi tiết”)
@app.route("/api/sanpham/<ma>")
def api_sanpham_detail(ma):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.MaSP, s.TenSP_, s.DonGia, s.GiaCu, s.MoTa, s.Anh, 
               s.MaLoai, l.TenLoai
        FROM SANPHAM s
        LEFT JOIN LOAISANPHAM_ l ON s.MaLoai = l.MaLoai
        WHERE s.MaSP = ?
    """, ma)
    row = cur.fetchone()
    if not row:
        cur.close(); conn.close()
        return {"error": "Không tìm thấy sản phẩm"}, 404

    cols = [col[0] for col in cur.description]
    product = dict(zip(cols, row))
    cur.close(); conn.close()
    return product

# ✅ Trang HTML hiển thị chi tiết sản phẩm
@app.route("/sanpham/view/<ma>")
def sanpham_view(ma):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.MaSP, s.TenSP_, s.DonGia, s.GiaCu, s.MoTa, s.Anh, 
               s.MaLoai, l.TenLoai
        FROM SANPHAM s
        LEFT JOIN LOAISANPHAM_ l ON s.MaLoai = l.MaLoai
        WHERE s.MaSP = ?
    """, ma)
    rows = rows_to_dicts(cur)
    cur.close(); conn.close()
    if not rows:
        flash("Không tìm thấy sản phẩm", "error")
        return redirect(url_for("sanpham_list"))
    return render_template("chi_tiet_sanpham.html", p=rows[0])



# ---------------- TAI KHOAN ----------------

@app.route("/taikhoan")
def taikhoan_list():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT MaTK, TenDangNhap, Email, VaiTro, MaKH FROM TAI_KHOAN")
    items = rows_to_dicts(cur)
    cur.close(); conn.close()
    return render_template("taikhoan_list.html", items=items)


@app.route("/taikhoan/add", methods=["GET", "POST"])
def taikhoan_add():
    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        matk = request.form.get("MaTK") or str(uuid4())[:8]
        ten = request.form.get("TenDangNhap")
        mk = request.form.get("MatKhau")
        email = request.form.get("Email")
        role = request.form.get("VaiTro")

        # ✅ Lấy thông tin khách hàng từ form
        hoten = request.form.get("HoTen")
        diachi = request.form.get("DiaChi") or "Chưa cập nhật"
        sodt = request.form.get("SoDT") or "0000000000"

        # ✅ Sinh mã khách hàng mới
        cur.execute("SELECT TOP 1 MaKH FROM KHACHHANG ORDER BY MaKH DESC")
        last = cur.fetchone()
        if last and last[0].startswith("KH"):
            num = int(last[0][2:]) + 1
            makh = f"KH{num:02d}"
        else:
            makh = "KH01"

        # ✅ Thêm khách hàng mới
        cur.execute("""
            INSERT INTO KHACHHANG (MaKH, HoTen, DiaChi, SoDT)
            VALUES (?, ?, ?, ?)
        """, makh, hoten, diachi, sodt)

        # ✅ Thêm tài khoản
        cur.execute("""
            INSERT INTO TAI_KHOAN (MaTK, TenDangNhap, MatKhau, Email, VaiTro, MaKH)
            VALUES (?, ?, ?, ?, ?, ?)
        """, matk, ten, mk, email, role, makh)

        conn.commit()
        cur.close(); conn.close()

        flash(f"Thêm tài khoản và khách hàng thành công (Mã khách hàng: {makh})", "success")
        return redirect(url_for("taikhoan_list"))

    cur.execute("SELECT MaKH, HoTen FROM KHACHHANG")
    kh = rows_to_dicts(cur)
    cur.close(); conn.close()
    return render_template("taikhoan_form.html", item=None, kh=kh)


@app.route("/taikhoan/delete/<ma>", methods=["POST"])
def taikhoan_delete(ma):
    conn = get_connection()
    cur = conn.cursor()
    
    # Lấy MaKH
    cur.execute("SELECT MaKH FROM TAI_KHOAN WHERE MaTK = ?", ma)
    row = cur.fetchone()
    makh = row[0] if row else None

    # Xóa tài khoản
    cur.execute("DELETE FROM TAI_KHOAN WHERE MaTK = ?", ma)

    # Xóa khách hàng nếu không còn tài khoản nào
    if makh:
        cur.execute("SELECT COUNT(*) FROM TAI_KHOAN WHERE MaKH = ?", makh)
        if cur.fetchone()[0] == 0:
            cur.execute("DELETE FROM KHACHHANG WHERE MaKH = ?", makh)

    conn.commit()
    cur.close(); conn.close()

    # Redirect kèm query param
    return redirect(url_for("taikhoan_list", deleted=1))


    # ------------------ API TÌM KIẾM SẢN PHẨM ------------------
@app.route("/api/search_sanpham", methods=["GET"])
def api_search_sanpham():
    q = request.args.get("q", "").strip().lower()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            RTRIM(s.MaSP) AS MaSP,
            s.TenSP_,
            s.Anh,
            s.DonGia,
            s.GiaCu,
            RTRIM(l.TenLoai) AS TenLoai
        FROM SANPHAM s
        LEFT JOIN LOAISANPHAM_ l 
            ON RTRIM(s.MaLoai) = RTRIM(l.MaLoai)
        WHERE LOWER(s.TenSP_) LIKE ?
           OR LOWER(l.TenLoai) LIKE ?
    """, (f"%{q}%", f"%{q}%"))

    rows = rows_to_dicts(cur)

    cur.close()
    conn.close()

    # ✅ KHÔNG TÌM THẤY → TRẢ MẢNG CÓ THÔNG BÁO
    if not rows:
        return jsonify([
            {
                "message": "Không có sản phẩm này"
            }
        ]), 200

    # ✅ CÓ SẢN PHẨM
    return jsonify(rows), 200


































# ---------------- FRONT-END ----------------

#-----Home------------
# -----Home------------
#@app.route("/home")
#def home():  # ✅ đổi tên tránh trùng
#    conn = get_connection()
#    cursor = conn.cursor()
#    cursor.execute("SELECT MaSP, TenSP_, DonGia, Anh FROM SANPHAM")
#    products = cursor.fetchall()
#    conn.close()
#    return render_template('home.html', products=products)


@app.route("/")
def home():
    conn = get_connection()
    cursor = conn.cursor()
    # Lấy danh sách loại sản phẩm (menu)
    cursor.execute("SELECT MaLoai, TenLoai FROM LOAISANPHAM_ ORDER BY TenLoai")
    categories = cursor.fetchall()
    # Lấy tất cả sản phẩm
    cursor.execute("""
    SELECT MaSP, TenSP_, DonGia, Anh, MaLoai
    FROM SANPHAM
    WHERE TrangThai = 1
""")

    products = cursor.fetchall()
    conn.close()
    return render_template('home.html', products=products, categories=categories, ma_loai_hien_tai=None)




@app.route("/home/loai/<ma_loai>")
def home_loai(ma_loai):
    conn = get_connection()
    cursor = conn.cursor()
    # Lấy danh sách loại sản phẩm
    cursor.execute("SELECT MaLoai, TenLoai FROM LOAISANPHAM_ ORDER BY TenLoai")
    categories = cursor.fetchall()
    # Lấy sản phẩm theo loại
    cursor.execute("""
    SELECT MaSP, TenSP_, DonGia, Anh, MaLoai
    FROM SANPHAM
    WHERE MaLoai = ? AND TrangThai = 1
""", (ma_loai,))

    products = cursor.fetchall()
    conn.close()
    return render_template("home.html", products=products, categories=categories, ma_loai_hien_tai=int(ma_loai))



@app.route('/chitiet/<ma_sp>')
def chitiet(ma_sp):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT MaSP, TenSP_, DonGia, MoTa, Anh 
    FROM SANPHAM 
    WHERE MaSP=? AND TrangThai=1
    """, (ma_sp,))

    sp = cursor.fetchone()
    conn.close()
    return render_template('CTSP.html', sp=sp)


# Trang đăng nhập (chưa xử lý logic)
@app.route("/dangnhap", methods=["GET", "POST"])
def dangnhap():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT TenDangNhap, MatKhau, VaiTro FROM TAI_KHOAN WHERE TenDangNhap = ? AND MatKhau = ?", (username, password))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            role = user[2].lower()
            if role == "admin":
                return redirect(url_for("index"))   # Dashboard
            else:
                return redirect(url_for("home"))    # Trang người dùng
        else:
            flash("Tên đăng nhập hoặc mật khẩu không đúng!", "danger")

    return render_template("DangNhap.html")

# Giỏ hàng
@app.route('/giohang')
def giohang():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sp.MaSP, sp.TenSP_, sp.Anh, cgh.SoLuong, cgh.DonGia, cgh.ThanhTien
        FROM CHITIETGIOHANG cgh
        JOIN SANPHAM sp ON sp.MaSP = cgh.MaSP
        WHERE MaGH = 'GH01'
    """)
    items = cursor.fetchall()
    conn.close()
    return render_template('Giohang.html', items=items)

# Thêm sản phẩm vào giỏ hàng
@app.route('/add_to_cart/<ma_sp>')
def add_to_cart(ma_sp):
    conn = get_connection()
    cursor = conn.cursor()

    # Kiểm tra giỏ hàng GH01 đã tồn tại chưa
    cursor.execute("SELECT MaGH FROM GIO_HANG WHERE MaGH = 'GH01'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO GIO_HANG (MaGH, MaKH, NgayTao)
            VALUES ('GH01', 'KH01', GETDATE())
        """)

    ma_sp = ma_sp.strip()

    # Lấy đơn giá sản phẩm
    cursor.execute("SELECT DonGia FROM SANPHAM WHERE MaSP = ?", (ma_sp,))
    sp = cursor.fetchone()

    if not sp:
        conn.close()
        flash("Sản phẩm không tồn tại!", "danger")
        return redirect(url_for("home"))

    don_gia = sp[0]

    # Kiểm tra sản phẩm đã có trong giỏ
    cursor.execute("""
        SELECT SoLuong FROM CHITIETGIOHANG
        WHERE MaGH = 'GH01' AND MaSP = ?
    """, (ma_sp,))
    item = cursor.fetchone()

    if item:
        # Nếu đã tồn tại → tăng số lượng
        so_luong_moi = item[0] + 1
        thanh_tien = so_luong_moi * don_gia

        cursor.execute("""
            UPDATE CHITIETGIOHANG
            SET SoLuong = ?, ThanhTien = ?
            WHERE MaGH = 'GH01' AND MaSP = ?
        """, (so_luong_moi, thanh_tien, ma_sp))
    else:
        # Nếu chưa có → thêm mới
        cursor.execute("""
            INSERT INTO CHITIETGIOHANG (MaGH, MaSP, SoLuong, DonGia, ThanhTien)
            VALUES ('GH01', ?, 1, ?, ?)
        """, (ma_sp, don_gia, don_gia))

    conn.commit()
    conn.close()

    flash("Đã thêm sản phẩm vào giỏ!", "success")
    return redirect(url_for("giohang"))


# Xóa sản phẩm khỏi giỏ hàng
@app.route('/xoa_sanpham/<ma_sp>', methods=['POST'])
def xoa_sanpham(ma_sp):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM CHITIETGIOHANG WHERE MaSP=? AND MaGH='GH01'", (ma_sp),)
    conn.commit()
    conn.close()
    return '', 204  # trả về rỗng để JS remove row

# AJAX cập nhật số lượng
@app.route('/update_cart/<ma_sp>', methods=['POST'])
def update_cart(ma_sp):
    data = request.get_json()
    so_luong = int(data.get('quantity', 1))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DonGia FROM SANPHAM WHERE MaSP=?", (ma_sp),)
    result = cursor.fetchone()
    if not result:
        conn.close()
        return jsonify({"status":"error","message":"Sản phẩm không tồn tại"}), 404

    don_gia = result[0]
    thanh_tien = so_luong * don_gia

    cursor.execute("""
        UPDATE CHITIETGIOHANG
        SET SoLuong=?, ThanhTien=?
        WHERE MaSP=? AND MaGH='GH01'
    """, (so_luong, thanh_tien, ma_sp))

    conn.commit()
    conn.close()
    return jsonify({"status":"ok","thanh_tien":thanh_tien})



@app.route('/checkout', methods=['POST'])
def checkout():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 1️⃣ Lấy sản phẩm trong giỏ hàng
        cursor.execute("""
            SELECT MaSP, SoLuong, DonGia, ThanhTien
            FROM CHITIETGIOHANG
            WHERE MaGH = 'GH01'
        """)
        items = cursor.fetchall()
        if not items:
            conn.close()
            return jsonify({"status": "error", "message": "Giỏ hàng trống!"}), 400

        # 2️⃣ Lấy mã đơn hàng lớn nhất hiện có
        cursor.execute("SELECT TOP 1 MaDH FROM DON_HANG ORDER BY MaDH DESC")
        row = cursor.fetchone()
        if row and row[0]:
            current = int(row[0][2:])  # Bỏ 2 ký tự 'DH', lấy phần số
            next_id = current + 1
        else:
            next_id = 1
        ma_dh = f"DH{next_id:02d}"  # Ví dụ: DH01, DH02, ...

        # 3️⃣ Tính tổng tiền
        tong_tien = sum([item[3] for item in items])

        # 4️⃣ Thêm vào DON_HANG
        from datetime import datetime
        ngay_dat = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO DON_HANG (MaDH, MaKH, NgayDat, TongTien)
            VALUES (?, 'KH01', ?, ?)
        """, (ma_dh, ngay_dat, tong_tien))
        conn.commit()  # ✅ Commit để đảm bảo DON_HANG tồn tại trước khi thêm chi tiết

        # 5️⃣ Thêm các sản phẩm vào CHITIETDONHANG
        for item in items:
            ma_sp, so_luong, don_gia, thanh_tien = item
            cursor.execute("""
                INSERT INTO CHITIETDONHANG (MaDH, MaSP, SoLuong, DonGia, ThanhTien)
                VALUES (?, ?, ?, ?, ?)
            """, (ma_dh, ma_sp, so_luong, don_gia, thanh_tien))

        # 6️⃣ Xóa giỏ hàng sau khi thanh toán
        cursor.execute("DELETE FROM CHITIETGIOHANG WHERE MaGH='GH01'")
        conn.commit()
        conn.close()

        return jsonify({
            "status": "ok",
            "message": f"Đặt hàng thành công! Mã đơn hàng của bạn là {ma_dh}"
        })

    except Exception as e:
        print("❌ Lỗi khi thanh toán:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
