# db.py
import pyodbc

# ==============================================
# KẾT NỐI SQL SERVER (Windows Authentication)
# Server: NGUYENDUYVIET20\SQLEXPRESS
# Database: DeMo
# ==============================================

# Nếu bạn cài ODBC Driver 18 thì thay 17 → 18
DRIVER = "{ODBC Driver 17 for SQL Server}"
SERVER = "NGUYENDUYVIET20\\SQLEXPRESS"   # lưu ý cần 2 dấu \\ trong chuỗi
DATABASE = "DeMo"

def get_connection():
    """
    Hàm tạo kết nối tới SQL Server bằng Trusted_Connection (Windows Authentication)
    """
    try:
        conn_str = f"DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes"
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as e:
        print("❌ Lỗi kết nối SQL Server:", e)
        raise

# Kiểm tra nhanh khi chạy trực tiếp file này
if __name__ == "__main__":
    try:
        conn = get_connection()
        print("✅ Kết nối SQL Server thành công!")
        conn.close()
    except Exception as ex:
        print("❌ Không thể kết nối:", ex)