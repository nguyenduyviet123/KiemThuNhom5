import unittest
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE = "http://127.0.0.1:5000"
MA_SAN_PHAM = "SP001"


def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)



class TestDeleteSanPham(unittest.TestCase):

    def setUp(self):
        self.driver = setup_driver()
        self.wait = WebDriverWait(self.driver, 10)

    def tearDown(self):
        self.driver.quit()

        time.sleep(1)


    def test_01_xoa_mem(self):
        print(f"\n[TEST] Xóa mềm sản phẩm {MA_SAN_PHAM} qua giao diện")

        driver = self.driver

        # 1️⃣ Vào trang danh sách sản phẩm
        driver.get(f"{BASE}/sanpham")

        # 2️⃣ Tìm dòng "Mã sản phẩm: 10"
        product_code = self.wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                f"//small[contains(@class,'product-code') and contains(text(), '{MA_SAN_PHAM}')]"
            ))
        )

        # 3️⃣ Đi lên thẻ cha .product-card
        product_card = product_code.find_element(
            By.XPATH, "ancestor::div[contains(@class,'product-card')]"
        )
        time.sleep(2)
        # 4️⃣ Click nút xóa mềm
        delete_btn = product_card.find_element(
            By.CSS_SELECTOR, ".icon-btn.delete"
        )
        delete_btn.click()

        # 5️⃣ Xác nhận alert
        Alert(driver).accept()

        # 6️⃣ Chờ xử lý và vào thùng rác
        time.sleep(1)
        driver.get(f"{BASE}/sanpham/trash")

        # 7️⃣ Kiểm tra sản phẩm đã vào thùng rác
        row = self.wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                f"//tr[starts-with(@id,'row-{MA_SAN_PHAM}')]"
            ))
        )

        self.assertIsNotNone(row)
        print("✅ PASS: Sản phẩm đã vào thùng rác")


    def test_02_xoa_vinh_vien(self):
        print(f"\n[TEST] Xóa vĩnh viễn sản phẩm {MA_SAN_PHAM}")

        driver = self.driver
        driver.get(f"{BASE}/sanpham/trash")

        row = self.wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                f"//tr[starts-with(@id, 'row-{MA_SAN_PHAM}')]"
            ))
        )

        delete_btn = row.find_element(By.CSS_SELECTOR, ".btn-danger")
        delete_btn.click()
        Alert(driver).accept()

        time.sleep(2)
        driver.refresh()

        rows = driver.find_elements(
            By.XPATH,
            f"//tr[starts-with(@id, 'row-{MA_SAN_PHAM}')]"
        )

        self.assertEqual(len(rows), 0)
        print("✅ PASS: Xóa vĩnh viễn thành công")
        


if __name__ == "__main__":
    print("\n=== BẮT ĐẦU KIỂM THỬ XÓA SẢN PHẨM ===")
    unittest.main(verbosity=2)