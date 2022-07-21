from selenium import webdriver
from selenium.webdriver.common.by import By

class Driver(object):

    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        # 使用headless无界面浏览器模式
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.driver.implicitly_wait(5)
        self.driver.maximize_window()

    def open_url(self, url):
        self.driver.get(url)


    def locateElement(self, locate_type, value):
        el = None
        if locate_type == "id":
            el = self.driver.find_element(By.ID, value)
        elif locate_type == "name":
            el = self.driver.find_element(By.NAME, value)
        elif locate_type == "text":
            el = self.driver.find_element(By.LINK_TEXT, value)
        elif locate_type == "xpath":
            el = self.driver.find_element(By.XPATH, value)
        elif locate_type == "css":
            el = self.driver.find_element(By.CSS_SELECTOR, value)
        elif locate_type == "tag_name":
            el = self.driver.find_element(By.TAG_NAME, value)
        return el

    def locateElements(self, locate_type, value):
        els = []
        if locate_type == "id":
            els = self.driver.find_elements(By.ID, value)
        elif locate_type == "name":
            els = self.driver.find_elements(By.NAME, value)
        elif locate_type == "text":
            els = self.driver.find_elements(By.LINK_TEXT, value)
        elif locate_type == "xpath":
            els = self.driver.find_elements(By.XPATH, value)
        elif locate_type == "css":
            els = self.driver.find_elements(By.CSS_SELECTOR, value)
        elif locate_type == "tag_name":
            els = self.driver.find_elements(By.TAG_NAME, value)
        return els

    def switch_iframe(self, iframe_el):
        self.driver.switch_to.frame(iframe_el)

    def click(self,locate_type, value):
        el = self.locateElement(locate_type, value)
        el.click()

    def input_data(self, locate_type, value, data):
        el = self.locateElement(locate_type, value)
        el.send_keys(data)

    def get_text(self,locate_type, value):
        try:
            el = self.locateElement(locate_type, value)
            return el.text
        except Exception as e:
            return ""

    def get_attr(self, locate_type, value, tagAttr):
        el = self.locateElement(locate_type, value)
        return el.get_attribute(tagAttr)

    def get_location(self, locate_type, value):
        el = self.locateElement(locate_type, value)
        return el.rect

    def __del__(self):
        # driver销毁时关闭
        self.driver.close()
