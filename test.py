# import csv
#
# name_1 = "Anna"
# name_2 = "Victor"
#
# with open("data.csv", "w") as file:
#     writer = csv.writer(file)
#     writer.writerow(
#         ("user-name", "user-address")
#     )
# user_data = [("user-name1", "user-address1"),
#              ("user-name2", "user-address2"),
#              ("user-name3", "user-address3")]
#
# with open("data.csv", "a") as file:
#     writer = csv.writer(file)
#     for i in user_data:
#         writer.writerow(i)
import multiprocessing
import multiprocessing as mp
import time

import requests as req

import fake_useragent as fu


def process_1(session, url, x):
    # print(mp.current_process)
    x.append(multiprocessing.current_process)
    response = session.get(url, timeout=10)
    print(response.ok)
    return None


if __name__ == '__main__':
    l = ["https://www.youtube.com/watch?v=Fx-v9UnbxHQ&t=50s" for i in range(50)]
    print("-" * 10)
    print(l)
    print("-" * 10)

    user_agent = fu.UserAgent()
    session = req.Session()
    session.headers.update({"user": user_agent.chrome})

    with multiprocessing.Manager() as manager:
        x = manager.list()
        l = [(session, i, x) for i in l]
        with mp.Pool(mp.cpu_count() * 4) as pool:
            pool.starmap(process_1, l)
            pool.close()
            pool.join()
        print(x)
        print("программа завершена")
