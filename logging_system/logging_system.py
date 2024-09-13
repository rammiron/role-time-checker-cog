import os

path = os.path.join(os.path.dirname(__file__),"logs", 'logs.logs')


def WriteLogs(user_name, time, image_url, data_without_processing, data_after_processing):
    text = (f"====НАЧАЛО ЗАПИСИ====  \n"
            f"время: {time}, заказчик: {user_name}\n\n"
            f"изображение: {image_url} \n\n"
            f"текст до обработки: \n{data_without_processing}\n"
            f"\nтекст после обработки: \n{data_after_processing}\n====КОНЕЦ ЗАПИСИ====\n\n ")

    if not os.path.exists(path):
        temp = open(path, "w+")
        temp.close()

    file = open(path, "a+")
    file.write(text)
    file.close()
    return path
