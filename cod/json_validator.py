import json

import requests as req
import pydantic
from loguru import logger

# region Логирование

logger.remove()
logger.add("log_error.log", level="ERROR", encoding="utf-8")
logger.remove()
logger.debug("-" * 50)
logger.debug(f"Проверка работы {__file__}")


# endregion


# region Классы для валидирования через pydantic

class F33(pydantic.BaseModel):
    text: str


class F22(pydantic.BaseModel):
    runs: list[F33, ...]


class F11(pydantic.BaseModel):
    description: F22


class Description_validata(pydantic.BaseModel):
    videoSecondaryInfoRenderer: F11


class Title_video_3(pydantic.BaseModel):
    text: str


class Title_video_2(pydantic.BaseModel):
    runs: list[Title_video_3, ...]


class Title_video_0(pydantic.BaseModel):
    title: Title_video_2


class Title_video(pydantic.BaseModel):
    videoPrimaryInfoRenderer: Title_video_0


class F4(pydantic.BaseModel):
    contents: list


class F3(pydantic.BaseModel):
    results: F4


class F2(pydantic.BaseModel):
    results: F3


class F1(pydantic.BaseModel):
    twoColumnWatchNextResults: F2


class Json_Data(pydantic.BaseModel):
    contents: F1


# endregion xth

def pars_video_data(page_json: str):
    video_name = None
    video_description = None
    # response = req.get(url)  # получаем станичку
    # if response.ok:
    try:
        # start = response.text.find("var ytInitialData")
        # page_json = response.text[
        #             start + len("var ytInitialData") + 2:response.text.find("</script>",
        #                                                                     start) - 1].strip()  # обрезали лишнее,
        # оставили только json

        json_content_raw = Json_Data.parse_raw(page_json)  # проверили json до второго contents

        logger.debug(f"{json_content_raw.dict()=}")

        json_content_name_raw = json_content_raw.dict()["contents"]["twoColumnWatchNextResults"]["results"][
            "results"]["contents"][0]  # получили первый элемент contents, там где есть название видео
        json_name_raw = Title_video.parse_obj(json_content_name_raw)  # получили json с названием видео

        logger.debug(f"{json_name_raw.dict()=}")

        video_name = json_name_raw.dict()["videoPrimaryInfoRenderer"]["title"]["runs"][0][
            "text"]  # получение названия видео

        logger.debug(f"{video_name=}")

        json_content_description = json_content_raw.dict()["contents"]["twoColumnWatchNextResults"]["results"][
            "results"]["contents"][1]  # получили второй элемент contents, там где есть описание видео
        json_description_raw = Description_validata.parse_obj(
            json_content_description)  # получили json  с описанием видео

        logger.debug(f"{json_description_raw.dict()=}")

        video_description_list = json_description_raw.dict()["videoSecondaryInfoRenderer"]["description"]["runs"]
        video_description_list = [i["text"].strip() for i in video_description_list]
        video_description = " ".join(video_description_list)

        logger.debug(f"{video_description=}")



    except pydantic.ValidationError as e:
        logger.error(f"{e.json()=}")
        # print(e.json())
        logger.debug("Некорекный json.Не удалость провалидировань данные.")
        logger.error("Некорекный json.Не удалость провалидировань данные.")
        # return {"name": None, "description": None}
        # raise
    except:
        logger.debug("Неизвестная ошибка")
        logger.error("Неизвестная ошибка")
        # return {"name": None, "description": None}
        # raise
    finally:
        return {"name": video_name, "description": video_description}


# else:
#     logger.debug("Запрос на ютуб не удачен")
#     return None


if __name__ == '__main__':
    pass
    # x = 12
    # logger.error(f"{x=}")
    # with open("../t.json", "r", encoding="utf-8") as file:
    #     x = file.write()
    # pars_video_data(x)
