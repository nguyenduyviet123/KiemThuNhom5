import threading
import time
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from app import app   # Flask app của bạn

URL = "http://127.0.0.1:5000/sanpham/add"


# ================== CHẠY FLASK ==================
def run_flask(): 
    app.run(debug=False, use_reloader=False)


# ================== TEST CLASS ==================
class TestAddProductAuto(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Chạy Flask trong thread riêng
        cls.flask_thread = threading.Thread(target=run_flask)
        cls.flask_thread.daemon = True
        cls.flask_thread.start()
        time.sleep(5)

        # Mở Chrome
        cls.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install())
        )
        cls.driver.maximize_window()

        cls.results = [] #lưu kết quả  test

    # ================== HÀM THÊM SẢN PHẨM ==================
    def add_product(self, ma, ten, gia, gia_cu, mota, anh):
        d = self.driver
        d.get(URL)
        time.sleep(5)

        d.find_element(By.NAME, "MaSP").clear()
        d.find_element(By.NAME, "MaSP").send_keys(ma)

        d.find_element(By.NAME, "TenSP_").clear()
        d.find_element(By.NAME, "TenSP_").send_keys(ten)

        d.find_element(By.NAME, "DonGia").clear()
        d.find_element(By.NAME, "DonGia").send_keys(str(gia))

        d.find_element(By.NAME, "GiaCu").clear()
        d.find_element(By.NAME, "GiaCu").send_keys(str(gia_cu))

        d.find_element(By.NAME, "MoTa").clear()
        d.find_element(By.NAME, "MoTa").send_keys(mota)

        d.find_element(By.NAME, "Anh").clear()
        d.find_element(By.NAME, "Anh").send_keys(anh)

        d.find_element(By.TAG_NAME, "button").click()
        time.sleep(5)

        # 🔥 BẮT FLASH MESSAGE (KHÔNG DÙNG id="message")
        alerts = d.find_elements(By.CLASS_NAME, "alert")
        if alerts:
            return alerts[0].text.lower()
        return ""

    # ================== CHẠY 1 TEST CASE ==================
    def run_case(self, case_name, ma, ten, gia, gia_cu, mota, anh, expected):
        self.add_product(ma, ten, gia, gia_cu, mota, anh)

        # ✅ Thành công = redirect sang trang danh sách
        actual = self.driver.current_url.endswith("/sanpham")

        self.results.append({
            "case": case_name,
            "expected": expected,
            "actual": actual
        })


    # ================== TEST TỔNG ==================
    def test_themsp_01(self):
        self.run_case("Thêm sản phẩm hợp lệ",
                      "SP001", "Bánh A", 10000, 20000, "Ngon", "https://product.hstatic.net/200000411281/product/banh_cuon_dao_2_e3015be4e7e642988dffcda4fb5f8c3e_master.png", True)
    def test_themsp_02(self):
        self.run_case("Thêm sản phẩm trùng mã",
                            "SP001", "Bánh B", 90000, 20000, "Ngon", "anh2.png", False)
    def test_themsp_03(self):
        self.run_case("Thêm sản phẩm tên trống",
                      "SP002", "", 70000, 20000, "Ngon", "anh3.png", False)
    def test_themsp_04(self):
        self.run_case("Thêm sản phẩm giá < 0",
                      "SP003", "Bánh C", -20000, 30000, "Ngon", "anh4.png", False)
    def test_themsp_05(self):
        self.run_case("Thêm sản phẩm mô tả trống",
                      "SP004", "Bánh D", 30000, 40000, "", "anh5.png", False)
    def test_themsp_06(self):
        self.run_case("Thêm sản phẩm ảnh trống",
                      "SP005", "Bánh E", 40000, 50000, "Ngon", "", False)
    def test_themsp_07(self):
        self.run_case("Thêm sản phẩm giá = 0",
                      "SP006", "Bánh F", 0, 60000, "Ngon", "https://product.hstatic.net/200000411281/product/banh_cuon_so_co_la_2_ffe70b00519b40afb89dc669b28468a5_master.png", True)



    # ================== IN KẾT QUẢ ==================
    @classmethod
    def tearDownClass(cls):
        print("\n====== KẾT QUẢ KIỂM THỬ ======")
        for r in cls.results:
            status = "PASS" if r["expected"] == r["actual"] else "FAIL"
            print(f'{r["case"]} | Expected={r["expected"]} | Actual={r["actual"]} | {status}')

        cls.driver.quit()


# ================== RUN ==================
if __name__ == "__main__":
    unittest.main()