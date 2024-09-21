import os
import json

path_to_json_id = os.path.join(os.path.dirname(__file__), "log_id.json")


def WriteLogs(user_name, message, time, image_url, data_without_processing, data_after_processing):
    with open(path_to_json_id, "r") as read_file:
        data = json.loads(read_file.read())
        log_id = data["id"]

    text = (f"**Запись {log_id}**  \n"
            f"время: {time}, заказчик: {user_name}, сообщение: {message}\n\n"
            f"изображение: {image_url} \n\n"
            f"**текст до обработки:** \n```{data_without_processing}```\n"
            f"\n**текст после обработки:** \n```{data_after_processing}```\n"
            f"**КОНЕЦ ЗАПИСИ**\n\n ")
    with open(path_to_json_id, "w") as read_file:
        log_id += 1
        data_dict = {"id": log_id}
        data_json = json.dumps(data_dict)
        read_file.write(data_json)
    return text
