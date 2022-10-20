import time
import tkinter as tk


def button_parse_button_func(b1: tk.Button, root: tk.Tk, radio_button):
    b1.config(text="попа")
    root.update()
    print(radio_button.get())


# def button_parse_button_func(b1: tk.Button, root: tk.Tk):
#     b1.config(text="попа")
#     root.update()


def main_window_create():
    root = tk.Tk()
    root.geometry("300x300+100+100")
    root.title("You_Tube parser")
    # root.resizable(False,False)

    lable_1 = tk.Label(root, text="Введите ссылку")

    entry_1 = tk.Entry(justify=tk.CENTER)

    frame = tk.Frame(root, background="green")
    frame_radio_button_1 = tk.Frame(root)

    button_pars = tk.Button(frame, text="Начать парсить",
                            command=lambda: button_parse_button_func(button_cancel, root, r_var1))
    button_cancel = tk.Button(frame, text="Отмена")

    r_var1 = tk.IntVar()
    r_var1.set(0)
    radio_button_url = tk.Radiobutton(frame_radio_button_1, text="url", variable=r_var1, value=0)
    radio_button_file = tk.Radiobutton(frame_radio_button_1, text="file", variable=r_var1, value=1)
    radio_button_lost_list = tk.Radiobutton(frame_radio_button_1, text="lost_list", variable=r_var1, value=2)

    button_pars.pack(side=tk.LEFT, padx=10, pady=10)
    button_cancel.pack(side=tk.LEFT, padx=10, pady=10)

    radio_button_url.pack(side=tk.LEFT, padx=10, pady=10)
    radio_button_file.pack(side=tk.LEFT, padx=10, pady=10)
    radio_button_lost_list.pack(side=tk.LEFT, padx=10, pady=10)

    lable_1.pack()
    entry_1.pack()
    frame_radio_button_1.pack()
    frame.pack()
    return root


def main():
    main_window_create().mainloop()


if __name__ == '__main__':
    main()
