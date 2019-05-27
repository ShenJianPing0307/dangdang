from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import *
from selenium.common.exceptions import TimeoutException
from pyquery import PyQuery as pq
import json
import pymongo

driver = webdriver.Chrome() #driver=webdriver.PhantomJS()无界面浏览器
client=pymongo.MongoClient(MONGO_URL)
db=client[MONGO_DB]

def search():
    """
    获取关键字，并且获取一共有多少页码
    :return:
    """
    try:
        driver.get("http://book.dangdang.com")
        input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#key_S"))
        )
        button=WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#form_search_new > input.button"))
        )
        input.send_keys(key)
        button.click()
        html=driver.page_source
        doc=pq(html)
        li=doc('div.paging > ul > li:nth-last-child(3)')
        total_num=li.text()
        return total_num
    except TimeoutException:
        return search()

def get_one_page():
    """
    获取每一页的信息
    :return:
    """
    html=driver.page_source
    doc=pq(html)
    items=doc('#search_nature_rg ul li').items()
    for item in items:
        yield {
            'title':item.find('a').attr('title'),
            'src':item.find('a').attr('href'),
            'img':item.find('a img').attr('data-original'),
            'price':item.find('.search_pre_price').text(),
            'discount':item.find('.search_discount').text()
        }

def save_to_file(result):
    """
    将字典对象存入到文件中
    :param result:
    :return:
    """
    with open('dangdang.txt','a',encoding='utf-8') as f:
        f.write(json.dumps(result,ensure_ascii=False)+'\n')
        f.close()

def save_to_mongo(result):
    """
    将字典对象存入到数据库
    :param result:
    :return:
    """
    try:
        if db[MONGO_TABLE].insert(result):
            print('存储成功',result)
    except Exception:
        print('存储失败')

def next_page(num):
    """
    获取下一页
    :param num:
    :return:
    """
    try:

        input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#t__cp"))
        )

        button=WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#click_get_page"))
        )
        input.clear()
        input.send_keys(num)
        button.click()

    except TimeoutException:
        return next_page(num)


def main():
    total_num=int(search())
    for i in range(2,total_num+1):
        next_page(i)
        results=get_one_page()
        for result in results:
            save_to_file(result)
            save_to_mongo(result)

if __name__ == "__main__":
    main()