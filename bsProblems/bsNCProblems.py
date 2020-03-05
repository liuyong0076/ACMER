from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup

def bsNCProblem():
    chrome_driver_path = '''E:\chromedriver.exe'''
    driver = webdriver.Chrome(executable_path=chrome_driver_path)
    ncusername, ncpwd = '18600761633', 'liuyong'
    url = 'https://ac.nowcoder.com/acm/contest/950/K'
    driver.get(url)

    try:
        username_element = WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.ID,"jsEmailIpt"))
        )
        pwd_element = driver.find_element_by_id('jsPasswordIpt')
        loginbtn_element = driver.find_element_by_id('jsLoginBtn')

        username_element.send_keys(ncusername)
        pwd_element.send_keys(ncpwd)

        loginbtn_element.click()
        driver.refresh()

        time.sleep(3)
        
        title_element = driver.find_element(By.CLASS_NAME,'terminal-topic-title')
        limit_element = driver.find_element(By.CLASS_NAME,'subject-item-wrap')
        describe_element = driver.find_element(By.CLASS_NAME,'subject-describe')
        print(title_element.text)
        print(limit_element.text)
        print(describe_element.text)

        driver.close()
    finally:
        pass


if __name__ == "__main__":    
    bsNCProblem()