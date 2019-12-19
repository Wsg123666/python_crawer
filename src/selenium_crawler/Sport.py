from selenium import webdriver   # 使用webdriver实现的晨跑成绩爬虫
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re

chrome_options = Options()
chrome_options.add_argument('--headless')

driver = webdriver.Chrome("/Users/lyzmaster/Downloads/chromedriver", chrome_options=chrome_options)
driver.get('https://tygl.sspu.edu.cn/SportScore')
driver.find_element_by_id("Button1").click()

username_ele = driver.find_element_by_id("username")
password_ele = driver.find_element_by_id("password")
username_ele.send_keys("20181131104")
password_ele.send_keys("1581365613TS")

driver.find_element_by_xpath(u"(.//*[normalize-space(text()) and normalize-space(.)='忘记密码？'])[1]/following::button[1]").click()
driver.find_element_by_xpath("//a[@id='a1']/img").click()
html = driver.page_source
driver.close()

soup = BeautifulSoup(html, "html.parser")
tbodys = soup.find_all("tbody")
tds = tbodys[2].find_all("td")
inner_tds = tds[48].find_all("td")

data1 = inner_tds[1].text  # 早操
data2 = inner_tds[3].text  # 课外活动
data3 = inner_tds[5].text  # 次数调整
data4 = inner_tds[7].text  # 体育长廊

# print(data1, data2, data3, data4)
num = 0
# for td in tds:
#     num += 1
#     print(num)
#     print(td)
all_runs = tds[70]
each_run = all_runs.find_all("td")

for td_num in range(int(len(each_run)/6)):
    name = each_run[td_num*6+1].text
    date = each_run[td_num*6+2].text
    time = each_run[td_num*6+3].text
    state = each_run[td_num*6+4].text
    print(name, date, time, state)
