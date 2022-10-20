import csv
import datetime
import multiprocessing
import os.path
import time

import openpyxl
import pydantic

from cod import json_validator
import fake_useragent
import requests as req
from selenium import webdriver
from selenium.webdriver.common.by import By
from tqdm import tqdm
import json_validator
from loguru import logger

class YouTube_Parser:
    def __init__(self, url: str, multiproc=False):
        self.__multiproc = multiproc
        self.__chanal_url = url
        self.__user_agent = fake_useragent.UserAgent()
        self.__driver = None

        self.href_list = []
        self.all_video_data_list = []
        self.lost_href_list = []
        self.page_source = None

    def page_scroller(self):
        '''Даная функция пролистывает интернет страницу, открытую в драйвере, до самого низа. Основано на подсчёте
        количества ссылок на странице. Если кол-во ссылок не меняется с пролистыванием, то страница пролистана.'''
        start = datetime.datetime.now()
        k = 0  # старое количество страниц
        check = 0
        while True:  # цикл пролистывает страницу до конца
            time.sleep(3)
            hrefs = self.__driver.find_elements(By.TAG_NAME, "a")
            if len(hrefs) == k:
                check += 1
                if check > 3:
                    print("Поиск видео окончен.")
                    break
            else:
                now = datetime.datetime.now()
                if str(now - start) > "0:00:15.000000":
                    start = now
                    print("Поиск продоложается...")
                k = len(hrefs)
                self.__driver.execute_script("window.scrollBy(0,1000000);")

    def get_hrefs(self):
        ''''Данныя функция получает все ссылки на видео со страницы, открытой в драйвере, который создан в
            конструкторе класса и сохраняет их в self.href_list'''
        print("Получение ссылок...")
        html_page = self.__driver.find_element(By.XPATH, '//*[@id="contents"]')  # находим div блок с видео
        # html_page = html_page.find_element(By.TAG_NAME, 'div')
        # print(f"{html_page.get_attribute('id')}")
        html_page = html_page.find_elements(By.ID, "details")

        # html_page = html_page.find_elements(By.TAG_NAME, "h3")
        # print(html_page)
        self.href_list = [i.find_element(By.TAG_NAME, "h3") for i in html_page]
        self.href_list = [i.find_element(By.TAG_NAME, "a") for i in html_page]
        # print("href[0]", self.href_list[0].get_attribute("href"))

        if self.href_list[0].get_attribute("href") == None:
            return None
        # print(self.href_list)
        # self.href_list = html_page.find_elements(By.TAG_NAME, "a")  # Находим в блоке div все ссылки
        # p = [i.get_attribute('title') for i in self.href_list]
        #
        # for i in p:
        #     print(i)

        self.href_list = [i.get_attribute("href") for i in tqdm(self.href_list)]  # if
        # if self.href_list[0] == None:
        #     print("cсылки не полученны")
        # i.get_attribute("id") == "video-title"])  # забираем у всех ссылок атрибут href
        print(F"Полученно {len(self.href_list)} ссылок на видео. ")
        # print(self.href_list)
        return True

    def run(self):
        '''Данная фукнция получает ссылки на все видео с ютуб канала, адрес которого храниться в self.chanal_url и
            сохраняет их в self.href_list'''
        self.__driver = self.__create_driver()
        try:
            print("Идёт поиск всех видео канала.")
            self.__driver.get(self.__chanal_url)  # Получение страницы по указанному url
            time.sleep(10)
            self.__driver.find_element(By.XPATH,
                                       '//*[@id="tabsContent"]/tp-yt-paper-tab[2]/div').click()  # Переход на вкладку видео

            self.page_scroller()  # пролистываем страницу до конца
            self.page_source = self.__driver.page_source
            with open("../data/htlm.txt", "w", encoding="utf-8") as file:
                file.write(self.page_source)

            check = self.get_hrefs()

            if check == None:
                print("Повтор получения ссылок.")
                self.href_list.clear()
                check = self.get_hrefs()

            if self.__multiproc == False:
                self.pars_title_description()
            elif self.__multiproc == True:
                self.pars_title_description_multiprocess()
            elif self.__multiproc == None:
                pass

            self.lost_video_checker()

            if self.all_video_data_list and self.__multiproc != None:
                self.write_to_excel()
            # print(f"время: {datetime.datetime.now() - start}")

        except:
            raise
        finally:
            self.__exit_driver()

    def lost_video_checker(self):
        lost = len(self.lost_href_list)
        print(f"Потери {lost}.")
        if lost:
            self.href_list = self.lost_href_list.copy()
            self.lost_href_list.clear()
            self.pars_title_description(extend_data=True)
            lost2 = len(self.lost_href_list)
            print(f"Сново потеряно:{lost2}.\n Удалось вернуть: {abs(lost2 - lost)}")
            lost = len(self.lost_href_list)
            if lost:
                self.href_list = self.lost_href_list.copy()
                self.lost_href_list.clear()
                self.pars_title_description(extend_data=True)
                lost2 = len(self.lost_href_list)
                print(f"Сново потеряно:{lost2}.\n Удалось вернуть: {abs(lost2 - lost)}")

    def pars_title_description(self, extend_data=False):
        print("Полученик данных.")
        session = self.__create_session()
        self.lost_href_list.clear()
        if self.href_list:
            for href in tqdm(self.href_list):
                response = session.get(href, timeout=10)
                if response.ok:
                    start_json = response.text.find("var ytInitialData")
                    raw_json = response.text[
                               start_json + len("var ytInitialData") + 2:response.text.find("</script>",
                                                                                            start_json) - 1].strip()  # обрезали лишнее, оставили только json
                    # try:
                    data = json_validator.pars_video_data(raw_json)
                    # self.writer_to_csv((data["name"], href, data["description"]))
                    if data["name"] and data["description"]:
                        if extend_data == False:
                            self.all_video_data_list.append((data["name"], href, data["description"]))
                        else:
                            self.all_video_data_list.extend([(data["name"], href, data["description"])])
                    else:
                        self.lost_href_list.append(href)

                    # except pydantic.ValidationError as e:
                    #     print(f"Ошибка {e}")
                    # except Exception as e:
                    #     print(f"Ошибка {e}")

                else:
                    print("Запрос на ютуб не удался")
                    self.lost_href_list.append(href)
            # print(self.all_video_data)
            # self.write_to_excel()
        else:
            print("Список с ссылками пуст")
        if session:
            session.close()

    @staticmethod
    def process(session, href, x: list, y: list):
        response = session.get(href, timeout=10)
        if response.ok:
            start = response.text.find("var ytInitialData")
            page_json = response.text[
                        start + len("var ytInitialData") + 2:response.text.find("</script>",
                                                                                start) - 1].strip()  # обрезали лишнее,
            # оставили только json
            # try:
            data = json_validator.pars_video_data(page_json)  # pars_video_data учитывает ошибки валидации
            if data["name"] and data["description"]:
                x.append((data["name"], href, data["description"]))
            else:
                y.append(href)

            # except Exception as e:
            #     print(f"Ошибка Exception: {e}")
            # except pydantic.ValidationError as e:
            #     print(f"Ошибка валидации: {e}")
        else:
            print("Запрос на ютуб не удался")
            y.append(href)

    def pars_title_description_multiprocess(self, extend_data=False):
        print("Полученик данных.")
        session = self.__create_session()
        self.lost_href_list.clear()
        if self.href_list:
            with multiprocessing.Manager() as manager:
                x = manager.list()
                y = manager.list()
                href_list = [(session, i, x, y) for i in self.href_list]

                with multiprocessing.Pool(multiprocessing.cpu_count() * 3) as pool:
                    pool.starmap(self.process, href_list)
                    pool.close()
                    pool.join()
                if extend_data == False:
                    self.all_video_data_list = list(x)
                else:
                    self.all_video_data_list.extend(list(x))
                self.lost_href_list = list(y)
        else:
            print("Список с ссылками пуст")
        if session:
            session.close()

    def write_to_excel(self):
        dir_name = self.__chanal_url.removeprefix('https://www.youtube.com/c/')
        if not os.path.exists(f"../data/{dir_name}"):
            os.mkdir(f"../data/{dir_name}")
        work_book = openpyxl.Workbook()
        sheat = work_book.create_sheet(title="data")

        sheat["A1"] = "Название"
        sheat["B1"] = "Ссылка"
        sheat["C1"] = "Описание"

        row = 2
        for i in self.all_video_data_list:
            print(i)
            print(type(i))
            sheat.cell(row=row, column=1).value = i[0]
            sheat.cell(row=row, column=2).value = i[1]
            sheat.cell(row=row, column=3).value = i[2]
            row += 1
        work_book.save(f"../data/{dir_name}/{datetime.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.xlsx")

    # def create_new_csv(self):
    #     dir_name = self.__chanal_url.removeprefix('https://www.youtube.com/c/')
    #     if not os.path.exists(f"../data/{dir_name}"):
    #         os.mkdir(f"../data/{dir_name}")
    #     self.name_csv = f"../data/{dir_name}/{datetime.datetime.now().strftime('%d-%m-%Y')}.csv"
    #     with open(self.name_csv, "w", encoding="utf-8") as file:
    #         data = ("Название:", "Ссылка:", "Описание:")
    #         writer = csv.writer(file)
    #         writer.writerow(data)
    #
    # def writer_to_csv(self, data: tuple | list):
    #     with open(self.name_csv, "a", encoding="utf-8") as file:
    #         writer = csv.writer(file)
    #         writer.writerow(data)

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
        # session.headers.update({"user-name": self.__user_agent.chrome, "accept": "/"})
        return session

    def __exit_driver(self):
        if self.__driver:
            self.__driver.close()
            self.__driver.quit()

    # def __del__(self):
    #     if self.__driver:
    #         self.__exit_driver()


if __name__ == '__main__':
    check_list = ("https://www.youtube.com/c/MeDallisTRoyale",

    "https://www.youtube.com/c/QuantumGames",
    # # "https://www.youtube.com/c/MeDallisTRoyale")
    "https://www.youtube.com/c/gosha_dudar",
    "https://www.youtube.com/c/PhysicsisSimple",
    "https://www.youtube.com/c/kuplinovplay")
    with open("test_otchet.txt", "w") as file:
        for url in check_list:
            try:
                parser = YouTube_Parser(url, multiproc=True)
                parser.run()
                file.write(f"{url} - true\n")
            except Exception as e:
                file.write(f"{url} - false\n")
                print(f"Ошибка {e}")
                raise
            except:
                file.write(f"{url} - false\n")
                print("какая-то другая ошибка")
                raise

    token = "5226592225:AAGuyEtD_FOotorITU45tTNOLWhEcR2htVA"
    chat_id = "488216212"
    res = req.get("https://api.telegram.org/bot" + token + "/sendMessage",
                  params={"chat_id": "488216212", "text": "программа завершена"})
    print("-" * 10)
    print(f"{res.ok=}")
    print("программа завершена!")

    # for i in range(15):
    #     x = YouTube_Parser("https://www.youtube.com/c/MeDallisTRoyale")
    #     x.pars_title_description(("https://www.youtube.com/watch?v=OXdzJx0-AW8",))
    #     del x
