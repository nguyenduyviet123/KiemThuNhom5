import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

BASE = "http://127.0.0.1:5000"
MA_SAN_PHAMS = ["SP001", "SP005", "SP006"]


def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)


class TestDeleteSanPhamUI(unittest.TestCase):

    def setUp(self):
        self.driver = setup_driver()
        self.wait = WebDriverWait(self.driver, 10)

    def tearDown(self):
        self.driver.quit()
        time.sleep(1)


    def test_03_xoa_mem_nhieu_sp(self):
        print("\n[TEST 03] Xóa mềm nhiều sản phẩm")

        driver = self.driver
        driver.get(f"{BASE}/sanpham")

        deleted = []

        for ma in MA_SAN_PHAMS:
            with self.subTest(ma=ma):
                print(f"  ➜ Xóa mềm sản phẩm {ma}")
                try:
                    product_code = self.wait.until(
                        EC.presence_of_element_located((
                            By.XPATH,
                            f"//small[contains(@class,'product-code') and contains(text(), '{ma}')]"
                        ))
                    )

                    product_card = product_code.find_element(
                        By.XPATH, "ancestor::div[contains(@class,'product-card')]"
                    )

                    delete_btn = product_card.find_element(
                        By.CSS_SELECTOR, ".icon-btn.delete"
                    )

                    delete_btn.click()
                    Alert(driver).accept()
                    time.sleep(1)

                    deleted.append(ma)
                    print(f"    ✅ Đã xóa mềm {ma}")

                except TimeoutException:
                    print(f"    ⚠️ Không tìm thấy {ma} → bỏ qua")

            print(f"✔️ Danh sách xóa mềm: {deleted}")
            self.assertGreater(len(deleted), 0, "Không xóa mềm được sản phẩm nào")

    

    def test_04_xoa_vinh_vien_nhieu_sp(self):
        print("\n[TEST 04] Xóa VĨNH VIỄN nhiều sản phẩm")

        driver = self.driver

        # 🔹 BƯỚC 1: đảm bảo sản phẩm đã nằm trong thùng rác
        driver.get(f"{BASE}/sanpham")
        for ma in MA_SAN_PHAMS:
            with self.subTest(ma=ma):
                try:
                    product_code = self.wait.until(
                        EC.presence_of_element_located((
                            By.XPATH,
                            f"//small[contains(@class,'product-code') and contains(text(), '{ma}')]"
                        ))
                    )

                    product_card = product_code.find_element(
                        By.XPATH, "ancestor::div[contains(@class,'product-card')]"
                    )

                    delete_btn = product_card.find_element(
                        By.CSS_SELECTOR, ".icon-btn.delete"
                    )
                    delete_btn.click()
                    Alert(driver).accept()
                    time.sleep(0.8)

                except TimeoutException:
                    pass  # có thể đã bị xóa mềm trước đó

        # 🔹 BƯỚC 2: vào thùng rác
        driver.get(f"{BASE}/sanpham/trash")

        deleted_hard = []

        for ma in MA_SAN_PHAMS:
            with self.subTest(ma=ma):
                print(f"  ➜ Xóa vĩnh viễn sản phẩm {ma}")
                try:
                    row = self.wait.until(
                        EC.presence_of_element_located((
                            By.XPATH,
                            f"//tr[starts-with(@id,'row-{ma}')]"
                        ))
                    )

                    hard_delete_btn = row.find_element(
                        By.CSS_SELECTOR, ".btn-danger"
                    )

                    hard_delete_btn.click()
                    Alert(driver).accept()
                    time.sleep(1)

                    deleted_hard.append(ma)
                    print(f"    ✅ Đã xóa vĩnh viễn {ma}")

                except TimeoutException:
                    print(f"    ⚠️ Không tìm thấy {ma} trong thùng rác")

            print(f"✔️ Danh sách xóa vĩnh viễn: {deleted_hard}")
            self.assertGreater(
                len(deleted_hard), 0,
                "Không có sản phẩm nào được xóa vĩnh viễn"
            )


if __name__ == "__main__":
    print("\n=== BẮT ĐẦU KIỂM THỬ XÓA SẢN PHẨM (UI) ===")
    unittest.main(verbosity=2)