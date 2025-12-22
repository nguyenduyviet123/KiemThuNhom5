import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE_URL = "http://127.0.0.1:5000"
PRODUCT_ID = "2"

class TestSanPhamEdit(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(5)

    def tearDown(self):
        self.driver.quit()

    def open_edit_page(self):
        self.driver.get(f"{BASE_URL}/sanpham/edit/{PRODUCT_ID}")
        time.sleep(1) # Dừng lại để xem trang được tải

    def fill_common_fields(self, ten="Bánh Test", dongia="50000", giacu="60000"):
        ten_input = self.driver.find_element(By.NAME, "TenSP_")
        gia_input = self.driver.find_element(By.NAME, "DonGia")
        giacu_input = self.driver.find_element(By.NAME, "GiaCu")

        ten_input.clear()
        time.sleep(0.3)
        ten_input.send_keys(ten)
        time.sleep(0.7)

        gia_input.clear()
        time.sleep(0.3)
        gia_input.send_keys(dongia)
        time.sleep(0.7)

        giacu_input.clear()
        time.sleep(0.3)
        giacu_input.send_keys(giacu)
        time.sleep(0.7)

    def submit_form(self):
        self.driver.find_element(By.XPATH, "//button[contains(text(),'Lưu')]").click()
        time.sleep(1) # Dừng lại sau khi click Lưu

    def wait_success(self):
        return WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "alert-success"))
        )

    def wait_error(self):
        return WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "alert-danger"))
        )

    def test_TC01_sua_sanpham_hop_le(self):
        self.open_edit_page()
        self.fill_common_fields()
        self.submit_form()

        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.url_contains("/sanpham"))
        alert = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "alert-success")))
        self.assertIn("cập nhật thành công", alert.text.lower())
        time.sleep(2)

    def test_TC02_gia_co_dau_phay(self):
        self.open_edit_page()
        self.fill_common_fields(dongia="65,000")
        self.submit_form()

        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.url_contains("/sanpham"))
        alert = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "alert-success")))
        self.assertIn("cập nhật thành công", alert.text.lower())
        time.sleep(2)

    def test_TC03_gia_am(self):
        self.open_edit_page()
        self.fill_common_fields(dongia="-10000")
        self.submit_form()

        alert = self.wait_error()
        self.assertIn("giá không được nhỏ hơn 0", alert.text.lower())
        self.assertIn(f"/sanpham/edit/{PRODUCT_ID}", self.driver.current_url)
        time.sleep(2)
    def test_TC04_nhap_chu_vao_gia(self):
        self.open_edit_page()
        self.fill_common_fields(dongia="abcxyz")
        self.submit_form()

        alert = self.wait_error()
        self.assertIn("đơn giá phải là số hợp lệ", alert.text.lower())
        time.sleep(2)

    def test_TC05_bo_trong_ten(self):
        self.open_edit_page()
        self.fill_common_fields(ten="")
        self.submit_form()

        alert = self.wait_error()
        self.assertIn("tên không được để trống", alert.text.lower())
        time.sleep(2)

    def test_TC06_bo_trong_gia(self):
        self.open_edit_page()
        self.fill_common_fields(dongia="", giacu="0")
        self.submit_form()

        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.url_contains("/sanpham"))
        alert = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "alert-success")))
        self.assertIn("cập nhật thành công", alert.text.lower())
        time.sleep(2)

    def test_TC07_gia_cu_am(self):
        self.open_edit_page()
        self.fill_common_fields(giacu="-5000")
        self.submit_form()

        alert = self.wait_error()
        self.assertIn("giá cũ không được nhỏ hơn 0", alert.text.lower())
        time.sleep(2)

    def test_TC08_nhap_chu_vao_gia_cu(self):
        self.open_edit_page()
        self.fill_common_fields(giacu="gia cu loi")
        self.submit_form()

        alert = self.wait_error()
        self.assertIn("giá cũ phải là số hợp lệ", alert.text.lower())
        time.sleep(2)

if __name__ == "__main__":
    unittest.main()
