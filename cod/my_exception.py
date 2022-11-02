class Url_Error_Domen(Exception):
    def __init__(self, url):
        if url:
            self.message = url
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f"Проверте ссылку которую вы вводите ({self.message}). В ней отсутствует 'https://' 'www.youtube.com'."
        else:
            return f"Проверте ссылку которую вы вводите. В ней отсутствует 'https://' 'www.youtube.com'."


class Url_Error_End_Href(Exception):
    def __init__(self, url):
        if url:
            self.message = url
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f"Проверте ссылку которую вы вводите ({self.message}). Возможно она не оканчивается названием канала. Возможно она не с главной страницы канала."
        else:
            return f"Проверте ссылку которую вы вводите. Возможно она не оканчивается названием канала. Возможно она не с главной страницы канала."


class Sruct_File_Error(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "Файл с не правильной структурой. Файл не содержит списка ссылок."


class Not_file(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "Файл не выбран."


class Not_url(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "Не удалось получить ссылки так как отсутствует атрибут href"
