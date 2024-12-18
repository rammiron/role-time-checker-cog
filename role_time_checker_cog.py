import io
import datetime
import gc
import os
import random
from Levenshtein import distance
import discord
import easyocr
from PIL import Image, ImageEnhance
from discord.ext import commands

if "cogs" in __name__:
    from .logging_system.logging_system import WriteLogs
else:
    from logging_system.logging_system import WriteLogs

user_id_for_send_logs = 1048600490562293850

# словарь для исправления ошибок замены цифр на буквы
symbols_replace = {
    "б": "6", "о": "0", "з": "3", "ч": "4", "а": "4"
}

# словарь для исправления ошибок замены букв на цифры
numeric_replace = {
    "6": "б", "0": "о", "3": "з", "4": "ч"
}

# словарь для замены имен ролей на действующие
role_names_replace = {
    "технический ассистент": "инженер-стажёр",
    "инженер-стажер": "инженер-стажёр",
    "борг": "киборг",
    "инженер станции": "инженер",
    "боксер": "боксёр",
    "пассажир": "ассистент",
    "научный ассистент": "лаборант",
    "научный руководитель": "науч. рук.",
    "старший научный сотрудник": "ведущий учёный",
    "ученый": "учёный",
    "доктор": "врач",
    "патологоанатом": "коронёр",
    "общее игровое время": "всё",
    "гв": "главный врач",
    "си": "старший инженер",
    "кэп": "капитан"
}

# список имен ролей для того, чтобы сверяться при проверки грамматики
roles = [
    "общее игровое время",
    "капитан",
    "глава персонала",
    "старший инженер",
    "научный руководитель",
    "главный врач",
    "квартирмейстер",
    "ведущий врач",
    "химик",
    "врач",
    "парамедик",
    "коронер",
    "психолог",
    "интерн",
    "ведущий учёный",
    "учёный",
    "лаборант",
    "ведущий инженер",
    "атмосферный техник",
    "инженер",
    "технический ассистент",
    "ведущий утилизатор",
    "утилизатор",
    "грузчик",
    "администратор сервиса",
    "шеф-повар",
    "ботаник",
    "бармен",
    "сервисный работник",
    "боксер",
    "уборщик",
    "библиотекарь",
    "священник",
    "зоотехник",
    "репортёр",
    "музыкант",
    "ассистент",
    "мим",
    "клоун",
    "киборг"
]

# эти роли не будут добавляться в вывод
black_list = ["агент внутренних дел", "магистрат", "юрист", "глава службы безопасности", "офицер сб", "инструктор сб",
              "кадет сб", "смотритель", "бригмедик", "бригмед", "кадет", "сб", "адвокат", "пилот", "детектив", "cб",
              "служба безопасности",
              "службы безопасности", 'офицер "синий щит"',
              '"синий щит"', "офицер", "адъютант", "робототехник", "инженерный борг", "медицинский борг"]


# функция для устранения ошибок из текста, к примеру в случае, когда "о" распознается как "0"
def text_handler(text):
    output = text
    for i in range(0, len(output) - 1):
        if not output[i].isnumeric():
            if i + 1 > len(output) - 1 or i - 1 < 0:
                continue
            next_item = i + 1
            prev_item = i - 1
            if output[next_item].isnumeric():
                if not output[next_item].isnumeric() and not output[prev_item].isnumeric():
                    continue

                try:
                    output = output[:i] + symbols_replace[output[i]] + output[i + 1:]
                except:
                    continue
            elif output[next_item] == "м" or output[next_item] == "ч":
                if not output[prev_item].isnumeric() and output[prev_item] != " " and output[prev_item] != "\n":
                    continue
                try:
                    output = output[:i] + symbols_replace[output[i]] + output[i + 1:]
                except:
                    continue
            elif output[prev_item] == " " or output[prev_item] == "\n" or output[prev_item] == "":

                try:
                    tmp = symbols_replace[output[next_item]]
                    output = output[:i] + symbols_replace[output[i]] + output[i + 1:]
                except:
                    continue
            else:
                if not output[prev_item].isnumeric() and output[i].isnumeric():
                    try:
                        output = output[:i] + numeric_replace[output[i]] + output[i + 1:]
                    except:
                        continue
    return output


# функция для конечной обработки сообщения, которое подгоняет всё под необходимый формат и избавляет выход от лишнего
def output_handler(text):
    to_array = []
    temp = ""
    for i in range(0, len(text)):
        if text[i] == "\n":
            if len(temp) < 1:
                temp = ""
                continue
            if temp in black_list:
                temp = ""
                continue
            if temp in to_array and not temp[0].isnumeric():
                temp = ""
                continue
            if temp not in roles:
                if distance(temp, "время") < 2 or distance(temp, "должность") < 2 or "сб" in temp:
                    temp = ""
                    continue

                if distance(temp, "игпееве епемя пельэпвптеля") <= 5 or distance(temp,
                                                                                 "игпшвпе впемя пельзпвптеля") <= 5:
                    temp = ""
                    continue

                smallest = len(temp) * 2
                role_name = ""
                for role in roles:
                    dst = distance(temp, role)
                    if dst < smallest:
                        smallest = dst
                        role_name = role
                if smallest < 2:
                    temp = role_name
                if temp in black_list or role_name in black_list:
                    temp = ""
                    continue
                if temp.startswith("0бщ") or temp.startswith("06щ") or temp.startswith("Общ") or temp.startswith("О6щ"):
                    if ":" not in temp:
                        temp = ""
                        continue
                    split = temp.split(":")

                    to_array.append(f"\nвсё")
                    to_array.append(split[1].replace(" ", ""))
                    temp = ""
                    continue
            if temp in black_list:
                temp = ""
                continue
            if temp in role_names_replace:
                to_array.append(role_names_replace[temp])
                temp = ""
                continue
            to_array.append(temp)
            temp = ""
        else:
            temp += text[i]
    buffer = ""
    output = " "
    index = 0
    # здесь происходит компоновка названий ролей и времени, для понятного выхода соответствующего шаблону
    while index < len(to_array) - 1:
        next = index + 1
        if len(to_array[index]) < 1:
            index += 1

            continue
        if to_array[index][0].isnumeric():
            if len(to_array[index]) < 3:
                index += 1

                continue

            if (not to_array[index][1].isnumeric() and not to_array[index][1] == "ч" and not to_array[index][1] == "м"
                    and to_array[index][2] != " "):

                if to_array[next][0].isnumeric():
                    if to_array[index] in black_list:
                        index += 2

                        continue
                    try:
                        to_array[index] = numeric_replace[to_array[index][0]] + to_array[index][1:]
                    except:
                        pass
                    output += f"{to_array[index]}: {to_array[next]}\n"
                    index += 2

                    continue
                elif buffer != "":

                    to_array[index] = numeric_replace[to_array[index][0]] + to_array[index][1:]
                    output += f"{to_array[index]}: {buffer}\n"
                    buffer = ""
                    index += 2
                    continue
                index += 2

                continue

            buffer = to_array[index][0]
            index += 1

            continue
        if not to_array[index][0].isnumeric() and next > len(to_array) - 1:
            index += 2

            continue
        if len(to_array[next]) == 0:
            to_array.remove(to_array[next])

        if not to_array[index][0].isnumeric() and not to_array[next][0].isnumeric():

            if next + 1 > len(to_array) - 1:
                index += 2

                continue
            if to_array[next + 1][0].isnumeric() and (
                    to_array[next + 1][1].isnumeric() or to_array[next + 1][1] == "ч"):
                if f"{to_array[index]} {to_array[next]}" in roles:
                    output += f"{to_array[index]} {to_array[next]}: {to_array[next + 1]}\n"
                    index += 3
                    continue
                elif f"{to_array[index]} {to_array[next]}" in black_list:
                    index += 3
                    continue
                output += f"{to_array[index]}: {to_array[next + 1]}\n"
                index += 3
                continue
            index += 2
            continue
        output += f"{to_array[index]}: {to_array[next]}\n"
        index += 2
    return output


class RoleTimeCheckerCog(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.message_command(name="Извлечь время ролей.")
    async def get_time(self, ctx: discord.ApplicationContext, message: discord.Message):

        if not message.attachments:
            await ctx.respond("Скриншот не обнаружен.", ephemeral=True)

            return
        await ctx.defer()
        reader = easyocr.Reader(['ru'], gpu=True)
        readed_text = ""
        for attachment in message.attachments:

            temp_name = f"temp{random.randint(0, 1000) + random.randint(0, 1000)}.jpg"

            image_data = await attachment.read()
            # обрабатываем входяшее изображение для последующей обработки уже нейросетью
            with Image.open(io.BytesIO(image_data)) as img:
                img = img.convert('L')
                obj = ImageEnhance.Contrast(img)
                obj.enhance(100)
                obj = ImageEnhance.Sharpness(img)
                obj.enhance(2)
                obj = ImageEnhance.Brightness(img)
                obj.enhance(4)
                img.save(temp_name)
                del obj
                del img
            del image_data
            # вычленяем текст из изображения с помощью EasyOCR
            result = reader.readtext(temp_name, detail=0)
            # удаляем сохраненное изображение
            os.remove(temp_name)
            for item in result:
                if item not in readed_text:
                    readed_text += item + "\n"
            gc.collect()

        # обрабатываем полученный текст
        output = text_handler(readed_text.lower())
        # отправляем сообщение обработав его для выхода
        handled_for_output = output_handler(output)
        logs_text = ""
        respond: discord.WebhookMessage = await ctx.respond(handled_for_output)
        for attachment in message.attachments:
            logs_text += WriteLogs(ctx.author.global_name, respond.jump_url, datetime.datetime.now(), attachment.url,
                                   readed_text, handled_for_output)

        gc.collect()
        del reader
        if len(logs_text) < 2000:
            await ctx.guild.get_member(user_id_for_send_logs).send(logs_text)
            return
        with open("logs.txt", "w+", encoding='utf-8') as temp_file:
            temp_file.write(logs_text)
        with open("logs.txt", "r", encoding='utf-8'):
            await ctx.guild.get_member(user_id_for_send_logs).send(file=discord.File("logs.txt"))
        os.remove("logs.txt")
