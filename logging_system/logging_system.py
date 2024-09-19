import os
import json

path = os.path.join(os.path.dirname(__file__), "logs", 'logs.logs')
path_to_json_id = os.path.join(os.path.dirname(__file__), "log_id.json")


def WriteLogs(user_name, time, image_url, data_without_processing, data_after_processing):
    with open(path_to_json_id, "r") as read_file:
        data = json.loads(read_file.read())
        log_id = data["id"]

    text = (f"====НАЧАЛО ЗАПИСИ #{log_id}====  \n"
            f"время: {time}, заказчик: {user_name}\n\n"
            f"изображение: {image_url} \n\n"
            f"текст до обработки: \n{data_without_processing}\n"
            f"\nтекст после обработки: \n{data_after_processing}\n====КОНЕЦ ЗАПИСИ====\n\n ")

    with open(path_to_json_id, "w") as read_file:
        log_id += 1
        data_dict = {"id": log_id}
        data_json = json.dumps(data_dict)
        read_file.write(data_json)

    if not os.path.exists(path):
        file_temp = open(path, "w+")

        file_temp.close()
    if os.path.getsize(path) >= 204800:
        file_temp = open(path, "w")
        file_temp.write("")
        file_temp.close()
    file = open(path, "a+")
    file.write(text)
    file.close()
    return path
