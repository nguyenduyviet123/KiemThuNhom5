import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE_URL = "http://127.0.0.1:5000"
PRODUCT_ID = "SP005"

# Mã màu cho đẹp (ANSI Escape Codes)
GREEN = "\033[92m"
RESET = "\033[0m"

class TestSanPhamEdit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
        cls.driver.implicitly_wait(5)
        cls.driver.maximize_window() # Mở rộng màn hình cho dễ nhìn

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def setUp(self):
        print("\n" + "="*70)

    def open_edit_page(self, product_id=PRODUCT_ID):
        self.driver.get(f"{BASE_URL}/sanpham/edit/{product_id}")
        time.sleep(1)

    def fill_common_fields(self, ten="Bánh Test", dongia="50000", giacu="60000"):
        ten_input = self.driver.find_element(By.NAME, "TenSP_")
        gia_input = self.driver.find_element(By.NAME, "DonGia")
        giacu_input = self.driver.find_element(By.NAME, "GiaCu")

        ten_input.clear()
        ten_input.send_keys(ten)
        
        gia_input.clear()
        gia_input.send_keys(dongia)
        
        giacu_input.clear()
        giacu_input.send_keys(giacu)
        time.sleep(0.5) # Giảm time sleep xuống chút cho chạy nhanh hơn

    def submit_form(self):
        # Tìm nút có type='submit' hoặc nút chứa chữ Lưu
        try:
            btn = self.driver.find_element(By.XPATH, "//button[contains(text(),'Lưu')]")
        except:
            btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        # Cuộn xuống nút rồi bấm (tránh bị che)
        self.driver.execute_script("arguments[0].scrollIntoView();", btn)
        time.sleep(0.5)
        btn.click()
        time.sleep(1)

    def wait_success(self):
        return WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "alert-success"))
        )

    def wait_error(self):
        return WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "alert-danger"))
        )

    # =================================================================
    # CÁC TEST CASE
    # =================================================================

    def test_TC01_sua_sanpham_hop_le(self):
        """TC01 - Sửa sản phẩm thành công (Dữ liệu hợp lệ)"""
        
        self.open_edit_page()
        self.fill_common_fields()
        self.submit_form()

        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.url_contains("/sanpham"))
        alert = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "alert-success")))
        self.assertIn("cập nhật thành công", alert.text.lower())
        print(f"{GREEN}✅ KẾT QUẢ: OK (Đã chuyển trang và hiện thông báo thành công){RESET}")

    def test_TC02_gia_co_dau_phay(self):
        """TC02 - Nhập giá có dấu phẩy (65,000)"""
        
        self.open_edit_page()
        self.fill_common_fields(dongia="65,000")
        self.submit_form()

        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.url_contains("/sanpham"))
        alert = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "alert-success")))
        self.assertIn("cập nhật thành công", alert.text.lower())
        print(f"{GREEN}✅ KẾT QUẢ: OK (Hệ thống tự xử lý dấu phẩy thành công){RESET}")

    def test_TC03_gia_am(self):
        """TC03 - Nhập Đơn giá là số âm (-10000)"""
        
        self.open_edit_page()
        self.fill_common_fields(dongia="-10000")
        self.submit_form()

        alert = self.wait_error()
        self.assertIn("giá không được nhỏ hơn 0", alert.text.lower())
        self.assertIn(f"/sanpham/edit/{PRODUCT_ID}", self.driver.current_url)
        print(f"{GREEN}✅ KẾT QUẢ: OK (Đã chặn được giá âm){RESET}")

    def test_TC04_nhap_chu_vao_gia(self):
        """TC04 - Nhập chữ vào ô Đơn giá (abcxyz)"""
        
        self.open_edit_page()
        self.fill_common_fields(dongia="abcxyz")
        self.submit_form()

        alert = self.wait_error()
        self.assertIn("đơn giá phải là số hợp lệ", alert.text.lower())
        print(f"{GREEN}✅ KẾT QUẢ: OK (Đã chặn được ký tự chữ){RESET}")

    def test_TC05_bo_trong_ten(self):
        """TC05 - Bỏ trống Tên sản phẩm"""
        
        self.open_edit_page()
        self.fill_common_fields(ten="")
        # Cần tắt validate client-side để test server (nếu có required)
        try:
            self.driver.execute_script("document.getElementsByName('TenSP_')[0].removeAttribute('required');")
        except:
            pass
        self.submit_form()

        alert = self.wait_error()
        self.assertIn("tên không được để trống", alert.text.lower())
        print(f"{GREEN}✅ KẾT QUẢ: OK (Đã báo lỗi tên trống){RESET}")

    def test_TC06_bo_trong_gia(self):
        """TC06 - Bỏ trống Giá (Chấp nhận giá cũ hoặc 0)"""
        
        self.open_edit_page()
        self.fill_common_fields(dongia="", giacu="0")
        self.submit_form()

        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.url_contains("/sanpham"))
        alert = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "alert-success")))
        self.assertIn("cập nhật thành công", alert.text.lower())
        print(f"{GREEN}✅ KẾT QUẢ: OK (Hệ thống xử lý giá rỗng thành công){RESET}")

    def test_TC07_gia_cu_am(self):
        """TC07 - Nhập Giá cũ là số âm (-5000)"""
        
        self.open_edit_page()
        self.fill_common_fields(giacu="-5000")
        self.submit_form()

        alert = self.wait_error()
        self.assertIn("giá cũ không được nhỏ hơn 0", alert.text.lower())
        print(f"{GREEN}✅ KẾT QUẢ: OK (Đã chặn được giá cũ âm){RESET}")

    def test_TC08_nhap_chu_vao_gia_cu(self):
        """TC08 - Nhập chữ vào Giá cũ"""
        
        self.open_edit_page()
        self.fill_common_fields(giacu="gia cu loi")
        self.submit_form()

        alert = self.wait_error()
        self.assertIn("giá cũ phải là số hợp lệ", alert.text.lower())
        print(f"{GREEN}✅ KẾT QUẢ: OK (Đã chặn được ký tự chữ ở giá cũ){RESET}")

    def test_TC09_sua_hang_loat_data_driven(self):
        """TC09 - Sửa hàng loạt sản phẩm (Data Driven Testing)"""

        # 1. Chuẩn bị dữ liệu test (Danh sách các sản phẩm cần sửa)
        # Bạn hãy thay ID bằng các ID có thật trong database của bạn
        danh_sach_test = [
            {"id": "1", "ten": "Bánh Mì Việt Nam Update 1", "gia": "20000", "giacu": "25000"},
            {"id": "2", "ten": "Bánh Kem Việt Nam Update 2", "gia": "150000", "giacu": "180000"},
            {"id": "3", "ten": "Bánh Quy Việt Nam Update 3", "gia": "30000", "giacu": "35000"}
        ]

        # 2. Chạy vòng lặp qua từng sản phẩm
        for data in danh_sach_test:
            print(f"\n🔹 Đang xử lý sản phẩm ID: {data['id']}...")
            
            # Bước 1: Mở trang sửa của ID tương ứng
            self.open_edit_page(product_id=data['id'])
            
            # Bước 2: Điền dữ liệu từ danh sách vào form
            self.fill_common_fields(ten=data['ten'], dongia=data['gia'], giacu=data['giacu'])
            
            # Bước 3: Lưu
            self.submit_form()

            # Bước 4: Kiểm tra kết quả
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.url_contains("/sanpham"))
            alert = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "alert-success")))
            
            # Assert: Kiểm tra xem có thông báo thành công không
            self.assertIn("cập nhật thành công", alert.text.lower())
            print(f"   -> {GREEN}✅ ID {data['id']}: Cập nhật thành công!{RESET}")
            
            time.sleep(1) # Nghỉ xíu trước khi qua sản phẩm tiếp theo

if __name__ == "__main__":
    # verbosity=2 để hiển thị tên test case và kết quả OK/FAIL chuẩn
    unittest.main(verbosity=2)