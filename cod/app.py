import cProfile
import pstats
import tkinter as tk
from tkinter import filedialog as fd
import controler
import my_exception


root = tk.Tk()
root.title("YouTube Parser")
root.resizable(False, False)
root.geometry("550x370+100+100")


def func_button_pars(text_palace: tk.Text, entry: tk.Entry, rad: tk.IntVar):
    try:
        text_palace.delete(1.0, tk.END)
        controler.func_pars(rad, entry, text_palace)
    except my_exception.Url_Error_Domen as e:
        text_palace.insert(1.0, f"{e}")
    except FileNotFoundError:
        text_palace.insert(1.0, "Не правильный путь к файлу.")
    except IndexError:
        text_palace.insert(1.0, "Вы не ввели ссылку.")
    except my_exception.Sruct_File_Error:
        text_palace.insert(1.0, "Не верная структура файла.")
    except my_exception.Not_file:
        text_palace.insert(1.0, "Файл не выбран.")
    except OSError:
        text_palace.insert(1.0, "Не правильный путь к файлу.")
    except:
        text_palace.insert(1.0, "Не предвиденная ошибка.")





def func_button_cancel():
    controler.kill_process()


def func_button_file(text_palace: tk.Text, entry: tk.Entry, rad: tk.IntVar):
    text_palace.delete(1.0, tk.END)
    mb_file = fd.askopenfilename()
    entry.delete(0, tk.END)
    entry.insert(0, mb_file)


def func_radiobutton_file_lost_file(button_1, window):
    button_1.pack(side=tk.LEFT)
    label_1.config(text="Название файла")
    window.update()


def func_rediobutton_pars(button_1: tk.Button, window):
    button_1.pack_forget()
    label_1.config(text="Введите ссылку")
    window.update()


label_1 = tk.Label(root, text="Введите ссылку")
entry_url = tk.Entry(root, justify=tk.CENTER, width=70)

radiobutton_frame = tk.Frame(root)
r_var_1 = tk.IntVar()
r_var_1.set(0)
radiobutton_url = tk.Radiobutton(radiobutton_frame, text="url", variable=r_var_1, value=0,
                                 command=lambda: func_rediobutton_pars(button_file, root))
radiobutton_file = tk.Radiobutton(radiobutton_frame, text="file", variable=r_var_1, value=1,
                                  command=lambda: func_radiobutton_file_lost_file(button_file, root))

button_frame = tk.Frame(root)
button_pars = tk.Button(button_frame, text="Начать парсинг",
                        command=lambda: func_button_pars(text_place, entry_url, r_var_1))
button_cancel = tk.Button(button_frame, text="Отмена", command=func_button_cancel)
button_file = tk.Button(button_frame, text="Выберите файл",
                        command=lambda: func_button_file(text_place, entry_url, r_var_1))

text_place = tk.Text(root, width=60, height=15, wrap=tk.WORD)

label_1.pack()
entry_url.pack()
radiobutton_frame.pack()
radiobutton_url.pack(side=tk.LEFT)
radiobutton_file.pack(side=tk.LEFT)
button_frame.pack()
button_pars.pack(side=tk.LEFT, padx=10, pady=10)
button_cancel.pack(side=tk.LEFT, padx=10, pady=10)
text_place.pack()

if __name__ == '__main__':
    profiler = cProfile.Profile()
    profiler.enable()
    root.mainloop()
    profiler.disable()
    print(pstats.Stats(profiler).sort_stats("ncalls").strip_dirs())
