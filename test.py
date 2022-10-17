import json

import requests as req
import pydantic






def get_json(res: req.Response):
    html_text = res.text
    # print(html_text)
    start = html_text.find("var ytInitialData = ")
    html_text = html_text[
                html_text.find("var ytInitialData = ") + len("var ytInitialData = "): html_text.find("</script>",
                                                                                                     start) - 1]
    # html_text=
    # print(html_text)
    # with open("json.json", "w", encoding="utf-8") as file:
    #     file.write(html_text)
    json_file = json.loads(html_text)
    # print(json_file)
    data = Json_Data.parse_raw(html_text)
    print(data)



if __name__ == '__main__':
    response = req.get("https://www.youtube.com/watch?v=dOO3GmX6ukU&t=1186s")
    if response.ok:
        get_json(response)
    else:
        print("Не работает ссылка")
