import datetime
import json
import os.path
import time

import json_check
import bs4
import fake_useragent
import requests as req
from selenium import webdriver
from selenium.webdriver.common.by import By
from tqdm import tqdm
from selenium.webdriver.common.keys import Keys


class YouTube_Parser:
    def __init__(self, url: str):
        self.__chanal_url = url
        self.__user_agent = fake_useragent.UserAgent()
        self.__driver = self.__create_driver()
        self.__driver.get("https://www.youtube.com/watch?v=4fOYYbPLg5g&t=3s")
        time.sleep(10)
        self.href_list = []

    def run_parsing(self):
        try:
            print("Идёт поиск всех видео канала...")
            self.__driver.get(self.__chanal_url)  # Получение страницы по указанному url
            # time.sleep(10)
            self.__driver.find_element(By.XPATH,
                                       '//*[@id="tabsContent"]/tp-yt-paper-tab[2]/div').click()  # Переход на вкладку видео
            k = 0  # старое количество страниц
            check = 0
            # self.__driver.implicitly_wait(2)
            start = datetime.datetime.now()

            while True:  # цикл пролистывает страницу до конца
                # self.__driver.implicitly_wait(1)
                time.sleep(1)
                hrefs = self.__driver.find_elements(By.TAG_NAME, "a")
                if len(hrefs) == k:
                    check += 1
                    if check > 3:
                        break
                else:
                    now = datetime.datetime.now()
                    if str(now - start) > "0:00:15.000000":
                        start = now
                        print(f"Найдено {len(hrefs)} видео. Поиск продоложается...")
                    k = len(hrefs)
                    self.__driver.execute_script("window.scrollBy(0,1000000);")
            time.sleep(1000)

            with open("../data/htlm.txt", "w", encoding="utf-8") as file:
                file.write(self.__driver.page_source)

            print("Получение ссылок...")
            html_page = self.__driver.find_element(By.XPATH, '//*[@id="contents"]')  # находим div блок с видео
            self.href_list = html_page.find_elements(By.TAG_NAME, "a")  # Находим в блоке div все ссылки
            self.href_list = tuple(
                [i.get_attribute("href") for i in tqdm(self.href_list)])  # забираем у всех ссылок атрибут href
            print("Полученны следующие ссылки: ")
            print(self.href_list)
            print(len(self.href_list))

            # self.pars_title_description()
            # print(f"время: {datetime.datetime.now() - start}")

        except:
            raise
        finally:
            self.__exit_driver()

    def pars_title_description(self, href_list):

        session = self.__create_session()
        if href_list:
            for href in href_list:
                print(href)
                response = session.get(href)

                if response.ok:
                    # print(response.text)
                    start = response.text.find("var ytInitialData")
                    page_json = response.text[
                                start + len("var ytInitialData") + 2:response.text.find("</script>",
                                                                                        start) - 1].strip().replace(
                        "true", "True")
                    # with open("full_json.json", "w", encoding="utf-8") as file:
                    #     file.write(page_json)
                    # with open("full_json.json", "r", encoding="utf-8") as file:
                    #     page_json = file.read()
                    # print(f"{page_json=}")

                    json_check.Json_valydate(page_json)
                else:
                    print("Нет данных со страницы")

                # print(response.text)

                # page_json_json = json.loads(page_json)
                #
                # # print()
                # print(page_json_json)
                # #
                # with open("json.txt", "w", encoding="utf-8") as file:
                #     json.dump(file, page_json, indent=4, ensure_ascii=False)
                #     file.write(page_json)

                # self.__driver.get(href)
                # # time.sleep(10)
                # div = self.__driver.find_element(By.XPATH, '//*[@id="below"]/div[7]')
                # video_title = self.__driver.find_element(By.XPATH, '//*[@id="container"]/h1/yt-formatted-string').text
                # pr = self.__driver.find_element(By.XPATH, '//*[@id="count"]/ytd-video-view-count-renderer/span[1]').text
                # likes = self.__driver.find_element(By.XPATH, '//*[@id="text"]')
                # channel_title = self.__driver.find_element(By.XPATH, '//*[@id="text"]/a').text
                # subscribers = self.__driver.find_element(By.XPATH, '//*[@id="owner-sub-count"]').text
                # description = self.__driver.find_element(By.XPATH, '//*[@id="description"]/yt-formatted-string')
                #
                # l = []
                # l.append(video_title)
                # l.append(pr)
                # l.append(likes)
                # l.append(channel_title)
                # l.append(subscribers)
                # l.append(description)
                # print("-" * 10)
                # for i, x in enumerate(l):
                #     print(f"{i} = {x}")
                # print("-" * 10)
                # print("конец")

    def __create_driver(self, driver_path: str = "../chromedriver.exe"):
        if os.path.exists(driver_path):
            driver_options = webdriver.ChromeOptions()
            # driver_options.add_argument("--headless")

            driver_options.add_argument("--disable-blink-features=AutoControled")
            driver_options.add_argument(f"user-agent={self.__user_agent.chrome}")
            driver = webdriver.Chrome(executable_path=driver_path, chrome_options=driver_options)
            driver.implicitly_wait(10)
            return driver
        else:
            print("Веб драйвера не обнаружено, проверте правильно ли указан путь до него.")

    def __create_session(self):
        session = req.Session()
        session.headers.update({"user-name": self.__user_agent.chrome, "accept": "/"})
        return session

    def __exit_driver(self):
        self.__driver.close()
        self.__driver.quit()

    def __del__(self):
        if self.__driver:
            self.__exit_driver()


if __name__ == '__main__':
    # check_list = ("https://www.youtube.com/c/MeDallisTRoyale/featured",)
    # # "https://www.youtube.com/c/QuantumGames",
    # # "https://www.youtube.com/c/PythonToday/featured",
    # # "https://www.youtube.com/c/gosha_dudar/featured",
    # # "https://www.youtube.com/c/PhysicsisSimple/featured",
    # # "https://www.youtube.com/c/kuplinovplay")
    # with open("test_otchet.txt", "w") as file:
    #     for url in check_list:
    #         try:
    #             parser = YouTube_Parser(url)
    #             parser.run_parsing()
    #             file.write(f"{url} - true\n")
    #         except Exception as e:
    #             file.write(f"{url} - false\n")
    #             print(f"Ошибка {e}")
    #             raise
    #         except:
    #             file.write(f"{url} - false\n")
    #             print("какая-то другая ошибка")
    #             raise
    #
    # token = "5226592225:AAGuyEtD_FOotorITU45tTNOLWhEcR2htVA"
    # chat_id = "488216212"
    # res = req.get("https://api.telegram.org/bot" + token + "/sendMessage",
    #               params={"chat_id": "488216212", "text": "программа завершена"})
    # print("-" * 10)
    # print(f"{res.ok=}")
    # print("программа завершена!")

    # for i in range(15):
    x = YouTube_Parser("https://www.youtube.com/c/QuantumGames")
    x.pars_title_description(("https://www.youtube.com/watch?v=MfaObpSATPU&t=1s",))
    del x
