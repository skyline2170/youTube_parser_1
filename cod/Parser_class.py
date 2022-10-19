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


class YouTube_Parser:
    def __init__(self, url: str, multiproc=False):
        self.__multiproc = multiproc
        self.__chanal_url = url
        self.__user_agent = fake_useragent.UserAgent()
        self.__driver = self.__create_driver()

        time.sleep(10)
        self.href_list = []
        self.all_video_data = []
        self.lost_list = []

    def run_parsing(self):
        '''Данная фукнция получает ссылки на все видео с ютуб канала, адрес которого храниться в self.chanal_url и
            сохраняет их в self.href_list'''
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
                time.sleep(3)
                # hrefs = self.__driver.find_elements(By.TAG_NAME, "a")
                hrefs = self.__driver.find_elements(By.ID, "details")
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
            # time.sleep(1000)

            with open("../data/htlm.txt", "w", encoding="utf-8") as file:
                file.write(self.__driver.page_source)

            print("Получение ссылок...")
            html_page = self.__driver.find_element(By.XPATH, '//*[@id="contents"]')  # находим div блок с видео
            # html_page = html_page.find_element(By.TAG_NAME, 'div')
            # print(f"{html_page.get_attribute('id')}")
            html_page = html_page.find_elements(By.ID, "details")
            print("qqq", len(html_page))

            # html_page = html_page.find_elements(By.TAG_NAME, "h3")
            # print(html_page)
            self.href_list = [i.find_element(By.TAG_NAME, "h3") for i in html_page]
            self.href_list = [i.find_element(By.TAG_NAME, "a") for i in html_page]
            print("href[0]", self.href_list[0].get_attribute("href"))
            # print(self.href_list)
            # self.href_list = html_page.find_elements(By.TAG_NAME, "a")  # Находим в блоке div все ссылки
            # p = [i.get_attribute('title') for i in self.href_list]
            #
            # for i in p:
            #     print(i)

            self.href_list = tuple(
                [i.get_attribute("href") for i in tqdm(self.href_list)])  # if
            # if self.href_list[0] == None:
            #     print("cсылки не полученны")
            # i.get_attribute("id") == "video-title"])  # забираем у всех ссылок атрибут href
            print(F"Полученно {len(self.href_list)} ссылок: ")
            print(self.href_list)

            # if self.__multiproc == False:
            #     self.pars_title_description()
            # elif self.__multiproc == True:
            #     self.pars_title_description_multiprocess()
            # print(f"время: {datetime.datetime.now() - start}")

        except:
            raise
        finally:
            self.__exit_driver()

    def pars_title_description(self):
        session = self.__create_session()
        self.lost_list.clear()
        href_list = self.href_list
        if href_list:
            for href in tqdm(href_list):
                response = session.get(href, timeout=10)
                if response.ok:
                    start = response.text.find("var ytInitialData")
                    page_json = response.text[
                                start + len("var ytInitialData") + 2:response.text.find("</script>",
                                                                                        start) - 1].strip()  # обрезали лишнее,
                    # оставили только json
                    try:
                        data = json_validator.pars_video_data(page_json)
                        # self.writer_to_csv((data["name"], href, data["description"]))
                        if data["name"] and data["description"]:
                            self.all_video_data.append((data["name"], href, data["description"]))
                        else:
                            self.lost_list.append(href)

                    except pydantic.ValidationError as e:
                        print(f"Ошибка {e}")
                    except Exception as e:
                        print(f"Ошибка {e}")

                else:
                    print("Запрос на ютуб не удался")
                    self.lost_list.append(href)
            # print(self.all_video_data)
            self.write_to_excel()
        else:
            print("Список с ссылками пуст")

    @staticmethod
    def process(session, href, x: list, y: list):
        response = session.get(href, timeout=10)
        if response.ok:
            start = response.text.find("var ytInitialData")
            page_json = response.text[
                        start + len("var ytInitialData") + 2:response.text.find("</script>",
                                                                                start) - 1].strip()  # обрезали лишнее,
            # оставили только json
            try:
                data = json_validator.pars_video_data(page_json)
                if data["name"] and data["description"]:
                    x.append((data["name"], href, data["description"]))
                else:
                    y.append(href)

            except Exception as e:
                print(f"Ошибка Exception: {e}")
            except pydantic.ValidationError as e:
                print(f"Ошибка валидации: {e}")
        else:
            print("Запрос на ютуб не удался")
            y.append(href)

    def pars_title_description_multiprocess(self):
        self.session = self.__create_session()
        self.lost_list.clear()
        href_list = self.href_list
        if href_list:
            with multiprocessing.Manager() as manager:
                x = manager.list()
                y = manager.list()
                href_list = [(self.session, i, x, y) for i in href_list]

                with multiprocessing.Pool(multiprocessing.cpu_count() * 3) as pool:
                    pool.starmap(self.process, href_list)
                    pool.close()
                    pool.join()
                self.all_video_data = list(x)
                self.lost_list = list(y)
                self.write_to_excel()
                print(self.lost_list)
                print("Длина lost_list = ", len(self.lost_list))
                if len(self.lost_list) > 0:
                    time.sleep(60)
                    self.href_list = self.lost_list[:]
                    self.pars_title_description()
        else:
            print("Список с ссылками пуст")

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
        for i in self.all_video_data:
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
        self.__driver.close()
        self.__driver.quit()

    def __del__(self):
        if self.__driver:
            self.__exit_driver()


if __name__ == '__main__':
    check_list = ("https://www.youtube.com/c/MeDallisTRoyale",

                  "https://www.youtube.com/c/QuantumGames",
                  # "https://www.youtube.com/c/MeDallisTRoyale")
                  "https://www.youtube.com/c/gosha_dudar",
                  "https://www.youtube.com/c/PhysicsisSimple",
                  "https://www.youtube.com/c/kuplinovplay")
    with open("test_otchet.txt", "w") as file:
        for url in check_list:
            try:
                parser = YouTube_Parser(url, multiproc=True)
                parser.run_parsing()
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
