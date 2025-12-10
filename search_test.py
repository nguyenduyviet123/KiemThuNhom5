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

    # =============TEST 1==================
    #  kiểm tra đăng nhập sang dashbord và chức năng tìm kiếm như 
    # là tìm sản phẩm cụ thể, tìm danh sách dựa trên loại sản phẩm và không tìm thấy sản phẩm nào
    
    # def test_login_and_search(self):
    #     driver = self.driver
    #     self.login_admin()

    #     driver.get("http://127.0.0.1:5000/sanpham")

    #     search_input = WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.ID, "searchInput"))
    #     )

    #     keyword = "Bánh bông lan cuộn"
    #     search_input.send_keys(keyword)
    #     search_input.send_keys(Keys.ENTER)

    #     time.sleep(2)

    #     # ===== TRƯỜNG HỢP 1: Tìm chính xác sản phẩm và mở trang chi tiết =====

    #     try:
    #         detail_title = WebDriverWait(driver, 3).until(
    #             EC.presence_of_element_located((By.CSS_SELECTOR, ".product-detail h2"))
    #         )

    #         if keyword.lower() in detail_title.text.lower():
    #             print("→ TRƯỜNG HỢP 1: MỞ TRANG CHI TIẾT SẢN PHẨM")

    #             # Lấy thông tin chi tiết theo đúng HTML của bạn
    #             name = detail_title.text
    #             code = driver.find_element(By.XPATH, "//p[b[text()='Mã sản phẩm:']]").text
    #             category = driver.find_element(By.XPATH, "//p[b[text()='Loại sản phẩm:']]").text
    #             new_price = driver.find_element(By.CSS_SELECTOR, ".new-price").text
    #             old_price = driver.find_element(By.CSS_SELECTOR, ".old-price").text
    #             desc = driver.find_element(By.CSS_SELECTOR, ".desc").text

    #             print("\n===== THÔNG TIN SẢN PHẨM =====")
    #             print("Tên sản phẩm:", name)
    #             print(code)
    #             print(category)
    #             print("Giá mới:", new_price)
    #             print("Giá cũ:", old_price)
    #             print("Mô tả:", desc)
    #             print("==============================\n")

    #             return

    #     except Exception as e:
    #         print("Lỗi khi lấy thông tin chi tiết:", e)
    #         pass



    #     # ===== TRƯỜNG HỢP 2: HIỂN THỊ DANH SÁCH SẢN PHẨM THEO LOẠI =====
    #     cards = driver.find_elements(By.CLASS_NAME, "product-card")

    #     if len(cards) > 0:
    #         print(f"→ TRƯỜNG HỢP 2: Có {len(cards)} sản phẩm thuộc loại '{keyword}'")

    #         # In danh sách tên sản phẩm (dạng text)
    #         product_names = [c.find_element(By.TAG_NAME, "h4").text for c in cards]

    #         print("Danh sách sản phẩm:")
    #         for name in product_names:
    #             print(" -", name)

    #         # Có danh sách => PASS
    #         self.assertGreater(len(cards), 0)
    #         return


    #     # ===== TRƯỜNG HỢP 3: không tim thấy sản phẩm hợp lệ =====
    #     no_product = WebDriverWait(driver, 5).until(
    #         EC.presence_of_element_located((By.ID, "no-product-msg"))
    #     )
    #     self.assertIn("Không tìm thấy sản phẩm", no_product.text)
    #     print(f"→ TRƯỜNG HỢP 2: Không tìm thấy sản phẩm liên quan '{keyword}'")
 

    # ==============TEST 2: Tìm kiếm không phân biệt chữ hoa/thường================
    # def test_search_case_insensitive(self):
    #     self.login_admin()
    #     driver = self.driver
    #     driver.get("http://127.0.0.1:5000/sanpham")

    #     search_input = WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.ID, "searchInput"))
    #     )
    #     search_input.clear()

    #     # Thay giá trị để test
    #     query = "reD vElVEt" 
    #     search_input.send_keys(query)
    #     search_input.send_keys(Keys.ENTER)

    #     # Chờ DOM render xong (kể cả khi không có product-card)
    #     WebDriverWait(driver, 10).until(
    #         lambda d: d.execute_script("return document.readyState === 'complete'")
    #     )

    #     # Lấy tất cả product-card
    #     cards = driver.find_elements(By.CSS_SELECTOR, "#productGrid .product-card")

    #     if len(cards) == 0:
    #         # Không có sản phẩm nào
    #         print(f"❌ Không tìm thấy sản phẩm nào với từ khóa '{query}'")
    #         self.fail(f"Không tìm thấy sản phẩm nào với từ khóa '{query}'")
    #     else:
    #         # Kiểm tra case-insensitive
    #         found = any(query.lower() in c.text.lower() for c in cards)
    #         if found:
    #             print(f"✅ Đã tìm thấy sản phẩm 'Red Velvet' với từ khóa '{query}'")
    #         else:
    #             print(f"❌ Không tìm thấy sản phẩm 'Red Velvet' với từ khóa '{query}'")
    #             self.fail(f"Không tìm thấy sản phẩm 'Red Velvet' với từ khóa '{query}'")


    #=============TEST 3: kiểm tra kí tự đặc biệt=========
    def test_search_special_characters(self):
        self.login_admin()
        driver = self.driver
        driver.get("http://127.0.0.1:5000/sanpham")

        keyword = "@@@"

        # Nhập ký tự đặc biệt
        search_input = driver.find_element(By.ID, "searchInput")
        search_input.clear()
        search_input.send_keys(keyword)
        search_input.send_keys(Keys.ENTER)

        time.sleep(1)

        # Kiểm tra không có product-card nào
        cards = driver.find_elements(By.CLASS_NAME, "product-card")
        self.assertEqual(len(cards), 0, "Không được có sản phẩm khi nhập ký tự đặc biệt")

        # Kiểm tra thông báo “Không tìm thấy sản phẩm”
        no_msg = driver.find_element(By.ID, "no-product-msg").text
        self.assertIn("Không tìm thấy", no_msg)

        print("✔ Test 4: Tìm ký tự đặc biệt → PASSED")





    #Thoát khỏi sau 2 giây
    def tearDown(self):
        time.sleep(2)
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
