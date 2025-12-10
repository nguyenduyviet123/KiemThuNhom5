from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unittest
import time

class AdminSearchTests(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()

    def login_admin(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000") 
        time.sleep(1)
        driver.get("http://127.0.0.1:5000/dangnhap")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "loginUsername"))
        )

        driver.find_element(By.ID, "loginUsername").send_keys("Nguyen Duy Viet")
        driver.find_element(By.ID, "loginPassword").send_keys("viet123!@#")

        login_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#loginForm .btn"))
        )
        login_btn.click()

        WebDriverWait(driver, 10).until(EC.url_contains("/dashboard"))
        time.sleep(2)

    # Test 1: kiểm tra đăng nhập sang dashbord và chức năng tìm kiếm như 
    # là tìm sản phẩm cụ thể, tìm danh sách dựa trên loại sản phẩm và không tìm thấy sản phẩm nào
    def test_login_and_search(self):
        driver = self.driver
        self.login_admin()

        driver.get("http://127.0.0.1:5000/sanpham")

        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchInput"))
        )

        keyword = "Bánhhhhhhhhhhh"
        search_input.send_keys(keyword)
        search_input.send_keys(Keys.ENTER)

        time.sleep(2)

        # ===== TRƯỜNG HỢP 1:Tìm chính xác sản phẩm đó và chuyển sang chi tiết=====
        try:
            detail_title = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".product-detail h2"))
            )
            if keyword.lower() in detail_title.text.lower():
                print("→ Mở trang chi tiết sản phẩm")
                return
        except:
            pass

        # ===== TRƯỜNG HỢP 2: hiển thị danh sách sản phẩm theo loại =====
        cards = driver.find_elements(By.CLASS_NAME, "product-card")
        if len(cards) > 0:
            print("→ Có danh sách sản phẩm:", len(cards))
            self.assertGreater(len(cards), 0)
            return
        
        # ===== TRƯỜNG HỢP 3: không tim thấy sản phẩm hợp lệ =====
        no_product = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "no-product-msg"))
        )
        self.assertIn("Không tìm thấy sản phẩm", no_product.text)
        print("→ Trường hợp không tìm thấy sản phẩm")
 

    # Test 2: Tìm kiếm không phân biệt chữ hoa/thường
    def test_search_case_insensitive(self):
        self.login_admin()
        driver = self.driver
        driver.get("http://127.0.0.1:5000/sanpham")

        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchInput"))
        )
        search_input.clear()
        search_input.send_keys("rEd vElVeT")
        time.sleep(1.5)
        search_input.send_keys(Keys.ENTER)
        time.sleep(2)

        cards = driver.find_elements(By.CLASS_NAME, "product-card")
        self.assertTrue(any("Red Velvet" in c.text for c in cards))
        print("→ Test tìm kiếm không phân biệt chữ hoa/thường OK")

    # Test 3: Nhập ký tự đặc biệt / SQL Injection
    def test_search_special_characters(self):
        self.login_admin()
        driver = self.driver
        driver.get("http://127.0.0.1:5000/sanpham")

        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchInput"))
        )
        search_input.clear()
        search_input.send_keys("' OR 1=1 --")
        time.sleep(1.2)
        search_input.send_keys(Keys.ENTER)
        time.sleep(2)

        no_product = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "no-product-msg"))
        )
        self.assertIn("Không tìm thấy sản phẩm", no_product.text)
        print("→ Test nhập ký tự đặc biệt OK")




    #Thoát khỏi sau 2 giây
    def tearDown(self):
        time.sleep(2)
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
