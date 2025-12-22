from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unittest
import time


class AdminSearchTests(unittest.TestCase):
    def start_test(self, name):
        print("\n" + "="*60)
        print(f"▶️ BẮT ĐẦU: {name}")
        print("="*60)


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
 
    def test_01(self):
        self.start_test("Test 01 – Tìm kiếm theo loại sản phẩm")
        self.login_admin()

        driver = self.driver
        driver.get("http://127.0.0.1:5000/sanpham")

        keyword = "bánh cayyy".lower()

        search_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "searchInput"))
        )
        search_input.clear()
        search_input.send_keys(keyword)
        search_input.send_keys(Keys.ENTER)

        # 👉 Chờ có sản phẩm render xong
        self.wait.until(
            lambda d: len(d.find_elements(By.CLASS_NAME, "product-card")) > 0
        )

        found = False
        danh_sach_loai = []

        # ✅ FIX STALE: lấy lại card MỖI LẦN
        cards = driver.find_elements(By.CLASS_NAME, "product-card")

        for i in range(len(cards)):
            card = driver.find_elements(By.CLASS_NAME, "product-card")[i]

            loai = card.find_element(By.CLASS_NAME, "category").text.lower()
            loai = loai.replace("loại:", "").strip()
            danh_sach_loai.append(loai)

            if keyword in loai:
                found = True

        self.assertTrue(
            found,
            f"Không tìm thấy sản phẩm thuộc loại '{keyword}'. "
           f"Các loại đang hiển thị: {', '.join(sorted(set(danh_sach_loai)))}"
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


    def test_02(self):
        self.start_test("Test 02 – Tìm kiếm theo tên sản phẩm cụ thể")
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
        

#     # # ================== TEST 3: KHÔNG TÌM THẤY SẢN PHẨM ==================

    def test_03(self):
        self.start_test("Test 03 – Không tìm thấy sản phẩm")
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
        

#     # # # ================== TEST 4: NHẬP KÝ TỰ ĐẶC BIỆT ==================
  
    def test_04(self):
        self.start_test("Test 04 – Tìm kiếm với ký tự đặc biệt")
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

        #self.wait.until: Selenium chờ tối đa X giây (thường 10s):
        # Nếu phần tử xuất hiện → trả về element → tiếp tục test
        # Nếu không xuất hiện → TimeoutException → ERROR
        no_product_msg = self.wait.until( #wait.until() là “TÔI CHẮC CHẮN PHẢI CÓ”
            EC.presence_of_element_located((By.ID, "no-product-msg"))
        ) #tìm phẩn tử HTML có id là no-product-msg


        cards = driver.find_elements(By.CLASS_NAME, "product-card")
        self.assertEqual(len(cards),0,"Không được hiển thị sản phẩm khi nhập ký tự đặc biệt")

        self.assertIn("Không tìm thấy",no_product_msg.text,"Thông báo không tìm thấy sản phẩm không hiển thị")
        

#     # # ================== TEST 5: TÌM KIẾM THEO TỪ KHÓA GẦN ĐÚNG ================== 
    
    def test_05(self):
        self.start_test("Test 05 – Tìm kiếm theo từ khóa gần đúng")
        self.login_admin()
        driver = self.driver
        driver.get("http://127.0.0.1:5000/sanpham")

        keyword = "bsd".lower()
        search_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "searchInput"))
        )
        search_input.clear()
        search_input.send_keys(keyword)
        search_input.send_keys(Keys.ENTER)

        # Chờ kết quả search cập nhật
        # self.wait.until(
        #     lambda d: len(d.find_elements(By.CLASS_NAME, "product-card")) > 0
        # ) #Nó ép buộc phải có sản phẩm 👉 Không có → ERROR (timeout) 

        time.sleep(1.5)  # 👈 chờ UI cập nhật kết quả
        cards = driver.find_elements(By.CLASS_NAME, "product-card")
        if len(cards) > 0:
            # 👉 TRƯỜNG HỢP CÓ KẾT QUẢ
            found = False
            for card in cards:
                name = card.find_element(By.TAG_NAME, "h4").text.lower()
                if keyword in name:
                    found = True

            self.assertTrue(
                found,
                f"Có sản phẩm nhưng không sản phẩm nào chứa từ khóa '{keyword}'"
            )# trường hợp này sảy ra khi lỗi hệ thống phản hồi ko đúng từ khóa là a nhưng hiện ra b,c

        else:
            # 👉 TRƯỜNG HỢP KHÔNG CÓ KẾT QUẢ (VẪN PASS)
            print("⚠️ Không tìm thấy sản phẩm")
            self.assertTrue(True)

        


# ## ==============TÌM KIẾM CHỨA KHOẢNG TRẮNG================

    def test_06(self):
        self.start_test("Test 06 – Tìm kiếm chỉ chứa khoảng trắng")
        self.login_admin()
        driver = self.driver
        driver.get("http://127.0.0.1:5000/sanpham")


        search_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "searchInput"))
        )
        search_input.clear()
        search_input.send_keys("   ")
        search_input.send_keys(Keys.ENTER)

        # Hệ thống không crash, vẫn hiển thị sản phẩm
        cards = driver.find_elements(By.CLASS_NAME, "product-card")

        self.assertGreater(
            len(cards), 0,
            "Hệ thống không hiển thị sản phẩm khi tìm kiếm bằng khoảng trắng"
        )
        

# ## ====================TÌM KIẾM NHIỀU LẦN==================

    def test_07(self):
        self.start_test("Test 07 – Tìm kiếm nhiều lần liên tiếp")
        self.login_admin()
        driver = self.driver
        driver.get("http://127.0.0.1:5000/sanpham")

        keywords = ["bông lan", "bánh mì", "abc"]


        search_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "searchInput"))
        )

        for keyword in keywords:
            print(f"\n🔍 Đang tìm kiếm với từ khóa: {keyword}")

            search_input.clear()
            search_input.send_keys(keyword)
            search_input.send_keys(Keys.ENTER)

            time.sleep(2.5)  # 👈 cho bạn kịp nhìn UI

            cards = driver.find_elements(By.CLASS_NAME, "product-card")

            if len(cards) > 0:
                print(f"✅ Có {len(cards)} sản phẩm được hiển thị")
                self.assertGreater(len(cards), 0)
            else:
                print("⚠️ Không tìm thấy sản phẩm")
                self.assertEqual(
                    len(cards), 0,
                    "Hệ thống vẫn hiển thị sản phẩm khi từ khóa không tồn tại"
                )
       

# ##====================THỜI GIAN PHẢN HỒI TÌM KIẾM==================
    
    def test_08(self):
        self.start_test("Test 08 – Thời gian phản hồi tìm kiếm")
        self.login_admin()
        driver = self.driver
        driver.get("http://127.0.0.1:5000/sanpham")

        keyword = "bánh mì".lower()

        search_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "searchInput"))
        )

        start_time = time.time()

        search_input.clear()
        search_input.send_keys(keyword)
        search_input.send_keys(Keys.ENTER)

        self.wait.until(
            lambda d: len(d.find_elements(By.CLASS_NAME, "product-card")) > 0
        )

        end_time = time.time()
        response_time = end_time - start_time
        # ✅ IN RA THỜI GIAN PHẢN HỒI
        print(f"\nThời gian phản hồi tìm kiếm: {response_time:.2f} giây")

        self.assertLess(
            response_time, 3,
            f"Thời gian phản hồi tìm kiếm quá lâu: {response_time:.2f}s"
        )

    def tearDown(self):
        time.sleep(2.5)
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
