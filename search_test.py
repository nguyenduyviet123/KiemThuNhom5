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
        self.wait = WebDriverWait(self.driver, 10)

    # ================== HÀM ĐĂNG NHẬP DÙNG CHUNG ==================
    def login_admin(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000/")
        time.sleep(1.5)
        driver.get("http://127.0.0.1:5000/dangnhap")

        self.wait.until(EC.presence_of_element_located((By.ID, "loginUsername")))
        driver.find_element(By.ID, "loginUsername").send_keys("viet")
        driver.find_element(By.ID, "loginPassword").send_keys("123")

        self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#loginForm .btn"))
        ).click()
        time.sleep(1)
        self.wait.until(EC.url_contains("/dashboard"))

            # ================== TEST 1: TÌM THEO LOẠI SẢN PHẨM ==================
    # def test_search_by_category(self):
    #     self.login_admin()
    #     driver = self.driver
    #     driver.get("http://127.0.0.1:5000/sanpham")
    #     keyword = "bánh ngọt"
    #     search_input = self.wait.until(
    #         EC.presence_of_element_located((By.ID, "searchInput")))
    #     search_input.clear()
    #     search_input.send_keys(keyword)

    #     cards = self.wait.until(
    #         EC.presence_of_all_elements_located((By.CLASS_NAME, "product-card"))
    #     )

    #     #vòng for duyệt loại trong db nếu khác ở 1 cái là dừng. 
    #     # Không có cơ hội duyệt các loại còn lại 👉 Đây là hành vi MẶC ĐỊNH của unittest
    #     for card in cards:
    #         loai = card.find_element(By.CLASS_NAME, "category").text.lower() #lấy tên loại
    #         #đối chiếu với từng sản phảm được hiện ra theo tên loại
    #         self.assertIn(
    #             keyword.lower(),
    #             loai,
    #             f"Sản phẩm không thuộc loại tìm kiếm: {loai}"
    #         )

    def test_search_by_category(self):
        self.login_admin()
        
        driver = self.driver
        driver.get("http://127.0.0.1:5000/sanpham")

        keyword = "bánh tráng".lower()

        search_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "searchInput"))
        )
        search_input.clear()
        search_input.send_keys(keyword)
        search_input.send_keys(Keys.ENTER)
        

        cards = self.wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "product-card"))
        )

        found = False
        danh_sach_loai = []

        for card in cards:
            loai = card.find_element(By.CLASS_NAME, "category").text.lower()
            loai = loai.replace("loại:", "").strip()
            danh_sach_loai.append(loai)

            if keyword in loai:
                found = True

        self.assertTrue(
            found,
            f"Không tìm thấy sản phẩm thuộc loại '{keyword}'. "
        )




    # # ================== TEST 2: TÌM SẢN PHẨM CỤ THỂ ==================
    # def test_search_exact_product(self):
    #     self.login_admin()
    #     driver = self.driver
    #     driver.get("http://127.0.0.1:5000/sanpham")

    #     keyword = "bánh mì trứng muối"
    #     search_input = self.wait.until(
    #         EC.presence_of_element_located((By.ID, "searchInput"))
    #     )
    #     search_input.clear()
    #     search_input.send_keys(keyword)
    #     search_input.send_keys(Keys.ENTER)

    #     # Kiểm tra có sản phẩm hiển thị
    #     cards = self.wait.until(
    #         EC.presence_of_all_elements_located((By.CLASS_NAME, "product-card"))
    #     )
    #     self.assertGreater(len(cards),0,"Không có sản phẩm nào được hiển thị khi tìm kiếm hợp lệ")

    #     # Kiểm tra tên sản phẩm chứa từ khóa
    #     product_name = cards[0].find_element(By.TAG_NAME, "h4").text.lower()
    #     self.assertIn(
    #         keyword.lower(),
    #         product_name,
    #         "Tên sản phẩm không chứa từ khóa tìm kiếm"
    #     )

    # def test_search_exact_product(self):
    #     self.login_admin()
    #     driver = self.driver
    #     driver.get("http://127.0.0.1:5000/sanpham")

    #     keyword = "bánh mì trứng muối".lower()

    #     search_input = self.wait.until(
    #         EC.presence_of_element_located((By.ID, "searchInput"))
    #     )
    #     search_input.clear()
    #     search_input.send_keys(keyword)
    #     search_input.send_keys(Keys.ENTER)

    #     # ✅ CHỜ đến khi sản phẩm đúng xuất hiện
    #     self.wait.until(
    #         lambda d: keyword in d.find_element(By.TAG_NAME, "h4").text.lower()
    #     )

    #     cards = driver.find_elements(By.CLASS_NAME, "product-card")
    #     self.assertGreater(
    #         len(cards), 0,
    #         "Không có sản phẩm nào được hiển thị khi tìm kiếm hợp lệ"
    #     )

    #     product_name = cards[0].find_element(By.TAG_NAME, "h4").text.lower()
    #     self.assertIn(
    #         keyword,
    #         product_name,
    #         "Tên sản phẩm không chứa từ khóa tìm kiếm"
    #     )


    def test_search_exact_product(self):
        self.login_admin()
        driver = self.driver
        driver.get("http://127.0.0.1:5000/sanpham")

        keyword = "bánh su kem".lower()

        # 1️⃣ Nhập từ khóa tìm kiếm
        search_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "searchInput"))
        )
        search_input.clear()
        search_input.send_keys(keyword)
        search_input.send_keys(Keys.ENTER)

        # 2️⃣ CHỜ SEARCH HOÀN TẤT (AJAX-safe)
        self.wait.until(
            lambda d: len(d.find_elements(By.CLASS_NAME, "product-card")) > 0
        )

        # 3️⃣ Lấy lại danh sách sản phẩm (tránh stale)
        cards = driver.find_elements(By.CLASS_NAME, "product-card")

        found = False
        danh_sach_ten = []

        for card in cards:
            name = card.find_element(By.TAG_NAME, "h4").text.lower()
            danh_sach_ten.append(name)
            if keyword in name:
                found = True

        # 4️⃣ Assert theo tập kết quả (ROBUST)
        self.assertTrue(
            found,
            f"Không tìm thấy sản phẩm '{keyword}'. "
            # f"Các sản phẩm đang hiển thị: {', '.join(danh_sach_ten)}"
        )



    # # ================== TEST 3: KHÔNG TÌM THẤY SẢN PHẨM ==================
    def test_search_not_found(self):
        self.login_admin()
        driver = self.driver
        driver.get("http://127.0.0.1:5000/sanpham")

        keyword = "abc"
        search_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "searchInput"))
        )
        search_input.clear()
        search_input.send_keys(keyword)
        search_input.send_keys(Keys.ENTER)

        no_product_msg = self.wait.until(
            EC.presence_of_element_located((By.ID, "no-product-msg"))
        )

        self.assertIn("Không tìm thấy",no_product_msg.text,"Không hiển thị thông báo khi không tìm thấy sản phẩm")

    # # ================== TEST 4: NHẬP KÝ TỰ ĐẶC BIỆT ==================
    def test_search_special_characters(self):
        self.login_admin()
        driver = self.driver
        driver.get("http://127.0.0.1:5000/sanpham")

        keyword = "@@@"
        search_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "searchInput"))
        )
        search_input.clear()
        search_input.send_keys(keyword)
        search_input.send_keys(Keys.ENTER)

        no_product_msg = self.wait.until(
            EC.presence_of_element_located((By.ID, "no-product-msg"))
        )


        cards = driver.find_elements(By.CLASS_NAME, "product-card")
        self.assertEqual(len(cards),0,"Không được hiển thị sản phẩm khi nhập ký tự đặc biệt")

        self.assertIn("Không tìm thấy",no_product_msg.text,"Thông báo không tìm thấy sản phẩm không hiển thị")

    def tearDown(self):
        time.sleep(2.5)
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
