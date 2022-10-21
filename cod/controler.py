import Parser_class
import tkinter
import my_exception
import datetime
import multiprocessing as mp


def validate_file(path_name: str):
    try:
        with open(path_name, "r", encoding="utf-8") as file:  # "FileNotFoundError"
            input_date = file.readlines()
        for i in input_date:
            validate_url(i)
        return input_date
    except IndexError:
        raise my_exception.Sruct_File_Error


def validate_url(url: str):
    data = url.split("//")
    if len(data) > 1 and "https:" in url:
        data_2 = data[1].split("/")

        # print(data, data_2)
        if all((data[0] == "https:", data_2[0] == "www.youtube.com")):
            if all((data_2[-1] != "featured", data_2[-1] != "videos", data_2[-1] != "playlists",
                    data_2[-1] != "community",
                    data_2[-1] != "channels", data_2[-1] != "about")):
                return url
            else:
                raise my_exception.Url_Error_End_Href(url)
        else:
            raise my_exception.Url_Error_Domen(url)
    else:
        raise IndexError


def func_button_pars_url(url):
    check = True
    while check:
        start = datetime.datetime.now()
        try:
            parser = Parser_class.YouTube_Parser(url, multiproc=True)
            parser.run()

            print("статистика:")
            print(len(parser.all_video_data_list))
            x = [i[0] for i in parser.all_video_data_list]
            y = [i[1] for i in parser.all_video_data_list]
            z = [i[2] for i in parser.all_video_data_list]
            print("Длины:", len(x), len(y), len(z))
            x = set(x)
            y = set(y)
            z = set(z)
            print("Длины:", len(x), len(y), len(z))

            check = False
        except Exception as e:
            # print(f"Ошибка {e}")
            raise
        except:
            # print("Неожиданная ошибка")
            raise
        print(f"Время на парсинг {url} = {datetime.datetime.now() - start}")


def func_button_pars_file(href_list):
    if href_list:
        for url in href_list:
            check = True
            while check:
                start = datetime.datetime.now()
                try:
                    parser = Parser_class.YouTube_Parser(url, multiproc=True)
                    parser.run()

                    print("статистика:")
                    print(len(parser.all_video_data_list))
                    x = [i[0] for i in parser.all_video_data_list]
                    y = [i[1] for i in parser.all_video_data_list]
                    z = [i[2] for i in parser.all_video_data_list]
                    print("Длины:", len(x), len(y), len(z))
                    x = set(x)
                    y = set(y)
                    z = set(z)
                    print("Длины:", len(x), len(y), len(z))

                    check = False
                except Exception as e:
                    # print(f"Ошибка {e}")
                    raise
                except:
                    # print("Неожиданная ошибка")
                    raise
                print(f"Время на парсинг {url} = {datetime.datetime.now() - start}")


def func_pars(radiobutton: tkinter.IntVar, data: tkinter.Entry, text: tkinter.Text, process_list):
    data = data.get()

    rad = radiobutton.get()
    # data = validate(rad, data)

    match rad:
        case 0:
            text.insert(1.0, "Проверка ссылки...\n")
            url = validate_url(data)
            p = mp.Process(target=func_button_pars_url, args=(url,))
            process_list.append(p)
            p.start()
        case 1:
            if not data:
                raise my_exception.Not_file
            href_list = validate_file(data)
            text.insert(1.0, "Проверка файла...\n")
            # p = mp.Process(target=func_button_pars_url, args=(url,))
            # process_list.append(p)
            # p.start()
            print(href_list)

