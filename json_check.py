import json

import pydantic
from pydantic import Field


class Title_video_3(pydantic.BaseModel):
    text: str


class Title_video_2(pydantic.BaseModel):
    runs: list[Title_video_3]


class Title_video_0(pydantic.BaseModel):
    title: Title_video_2


class Title_video(pydantic.BaseModel):
    videoPrimaryInfoRenderer: Title_video_0


# class Content_in1(pydantic.BaseModel):
#     videoPrimaryInfoRendererdict: dict
#     itemSectionRenderer: dict
#     itemSectionRenderer: dict
#     itemSectionRenderer: dict


# class Content_in2(pydantic.BaseModel):
#     # videoPrimaryInfoRenderer: dict
#     itemSectionRenderer: dict

class F4(pydantic.BaseModel):
    contents: list | tuple


class F3(pydantic.BaseModel):
    results: F4


class F2(pydantic.BaseModel):
    results: F3
    # secondaryResults: dict
    # autoplay: dict


class F1(pydantic.BaseModel):
    twoColumnWatchNextResults: F2


class Json_Data(pydantic.BaseModel):
    # response_context: dict = pydantic.Field(alias="responseContext")
    contents: F1


# class Json_valydate():
#     def __init__(self, json_page: str):
#         try:
#             json_data = Json_Data.parse_raw(json_page)
#             # print(json_data.json())
#
#             print(json_data)
#             json_data = json_data.dict()["contents"]["twoColumnWatchNextResults"]["results"]["results"]["contents"]
#             # with open("new_json.json", "w", encoding="utf-8") as file:
#             #     json.dump(json_data.dict()["contents"]["twoColumnWatchNextResults"]["results"]["results"]["contents"][0], file,
#             #               indent=4, ensure_ascii=False)
#
#             # json_data = Title_video.parse_file("new_json.json")
#             # print(json_data)
#         except pydantic.ValidationError as e:
#             # print(e.json())
#             raise


if __name__ == '__main__':
    import requests as req

    response = req.get("https://www.youtube.com/watch?v=MfaObpSATPU&t=1s")
    if response.ok:
        start = response.text.find("var ytInitialData")
        page_json = response.text[
                    start + len("var ytInitialData") + 2:response.text.find("</script>",
                                                                            start) - 1].strip()

        # print(page_json)
        x=Json_Data.parse_raw(page_json)
        print(x)



    else:
        print("Жопа")
    # try:
    #     x = Json_Data.parse_file("json.json", encoding="utf-8")
    #     print(x.json())
    #     with open("new_json.json", "w", encoding="utf-8") as file:
    #         json.dump(x.dict()["contents"]["twoColumnWatchNextResults"]["results"]["results"]["contents"][0], file,
    #                   indent=4, ensure_ascii=False)
    #
    #     x = Title_video.parse_file("new_json.json")
    #     print(x.dict())
    #
    #
    # except pydantic.ValidationError as e:
    #     print(e.json())
