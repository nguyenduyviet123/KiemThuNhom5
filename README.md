KiemThuNhom5 — Hệ Thống Quản Lý Sản Phẩm (Bánh Ngọt)
> Dự án kiểm thử phần mềm — Nhóm 5  
> Ứng dụng web quản lý sản phẩm bánh ngọt, xây dựng bằng \*\*Flask\*\* + \*\*SQL Server\*\*, kiểm thử tự động bằng \*\*Selenium\*\*.
---
Mục Lục
Giới thiệu
Công nghệ sử dụng
Cấu trúc dự án
Cài đặt & Chạy ứng dụng
Các chức năng chính
Kiểm thử tự động
---
Giới Thiệu
Dự án xây dựng một ứng dụng web quản lý sản phẩm với các chức năng CRUD đầy đủ, đồng thời viết bộ kiểm thử tự động 
sử dụng Selenium WebDriver để kiểm tra các nghiệp vụ quan trọng của hệ thống.
---
Công Nghệ Sử Dụng
Backend:	Python — Flask
Database:	Microsoft SQL Server (Express)
Giao diện: 	HTML, CSS
Kết nối DB:	`pyodbc` (ODBC Driver 17)
Kiểm thử:	`selenium`, `unittest`, `webdriver-manager`
Trình duyệt test	Google Chrome (ChromeDriver)
---
Cấu Trúc Dự Án
```
KiemThuNhom5/
│
├── app.py                  # Flask app chính (routes, logic)
├── db.py                   # Kết nối SQL Server
├── requirements.txt        # Danh sách thư viện Python
│
├── templates/              
│
├── static/
│   └── css/                
│
├── search\_test.py          # Test: Tìm kiếm sản phẩm
├── test\_themsp.py          # Test: Thêm sản phẩm 
├── test\_edit\_sp.py         # Test: Sửa sản phẩm
├── test\_xoa\_sp.py          # Test: Xóa mềm \& xóa vĩnh viễn
├── test\_xoa\_nhieu\_sp.py    # Test: Xóa nhiều sản phẩm cùng lúc
└── test\_scheduler.py       
```
Cài Đặt & Chạy Ứng Dụng
1. Clone dự án
```bash
git clone https://github.com/nguyenduyviet123/KiemThuNhom5.git
cd KiemThuNhom5
```
2. Cài đặt thư viện
```bash
pip install -r requirements.txt
```
3. Cấu hình kết nối SQL Server (xem bên dưới)
4. Chạy ứng dụng Flask
```bash
python app.py
```
Ứng dụng sẽ chạy tại: http://127.0.0.1:5000
---
Cấu Hình Cơ Sở Dữ Liệu
File `db.py` chứa thông tin kết nối. Mặc định sử dụng Windows Authentication:
```python
DRIVER   = "{ODBC Driver 17 for SQL Server}"
SERVER   = "NGUYENDUYVIET20\\\\SQLEXPRESS"   # Thay bằng tên server của bạn
DATABASE = "DeMo"
```
Kiểm tra kết nối nhanh:
```bash
python db.py
# ✅ Kết nối SQL Server thành công!
```
---
Các Chức Năng Chính
Chức năng	Mô tả
🔐 Đăng nhập	Xác thực người dùng quản trị
📦 Xem sản phẩm	Hiển thị danh sách toàn bộ sản phẩm
➕ Thêm sản phẩm	Thêm sản phẩm mới (mã, tên, giá, mô tả, hình ảnh)
✏️ Sửa sản phẩm	Chỉnh sửa thông tin sản phẩm hiện có
🗑️ Xóa mềm	Chuyển sản phẩm vào thùng rác
♻️ Khôi phục	Khôi phục sản phẩm từ thùng rác
❌ Xóa vĩnh viễn	Xóa hoàn toàn khỏi hệ thống
🔍 Tìm kiếm	Tìm kiếm theo tên, loại sản phẩm (AJAX)
🗂️ Thùng rác	Quản lý sản phẩm đã xóa mềm
---
Kiểm Thử Tự Động
Dự án sử dụng Selenium WebDriver + unittest để kiểm thử giao diện web tự động (end-to-end testing).
Chạy từng file test
> Đảm bảo Flask app đang chạy tại `http://127.0.0.1:5000` trước khi chạy test.
```bash
# Kiểm thử tìm kiếm sản phẩm
python -m unittest search\_test.py -v

# Kiểm thử thêm sản phẩm
python -m unittest test\_themsp.py -v

# Kiểm thử sửa sản phẩm
python -m unittest test\_edit\_sp.py -v

# Kiểm thử xóa sản phẩm
python -m unittest test\_xoa\_sp.py -v

# Kiểm thử xóa nhiều sản phẩm
python -m unittest test\_xoa\_nhieu\_sp.py -v
```
=> Dự án được xây dựng phục vụ mục đích học tập môn Kiểm Thử Phần Mềm.
