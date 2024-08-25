import io
import gc
import os
import random
from Levenshtein import distance
import discord
import easyocr
from PIL import Image, ImageEnhance
from discord.ext import commands

symbols_replace = {
    "б": "6", "о": "0", "з": "3", "ч": "4"
}
numeric_replace = {
    "6": "б", "0": "о", "3": "з", "4": "ч"
}

roles = [
    "капитан",
    "глава персонала",
    "глава службы безопасности",
    "старший инженер",
    "научный руководитель",
    "главный врач",
    "квартирмейстер",
    "магистрат",
    "агент Внутренних Дел",
    "юрист",
    "смотритель",
    "инструктор СБ",
    "детектив",
    "пилот СБ",
    "офицер СБ",
    "бригмедик",
    "кадет СБ",
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
    "киборг",
    "искусственный интеллект",
    "офицер «Синий щит»"
]


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


def output_handler(text):
    to_array = []
    temp = ""

    for i in range(0, len(text) - 1):
        if text[i] == "\n":
            if temp not in roles:
                smallest = len(temp)
                role_name = ""
                for role in roles:
                    dst = distance(temp, role)
                    if dst < smallest:
                        smallest = dst
                        role_name = role
                if smallest < 2:
                    temp = role_name
            to_array.append(temp)
            temp = ""
        else:
            temp += text[i]
    buffer = []
    output = " "
    index = 0
    print(to_array)
    while index < len(to_array) - 1:
        next = index + 1
        if to_array[index][0].isnumeric():
            buffer.append(to_array[index])
            index += 1
            continue
        if not to_array[index][0].isnumeric() and next > len(to_array) - 1:
            if len(buffer) == 0:
                index += 2
                continue
            output += f"{to_array[index]}: {buffer.pop()}"
        if not to_array[index][0].isnumeric() and not to_array[next][0].isnumeric():
            if len(buffer) == 0:
                index += 2
                continue
            output += f"{to_array[index]}: {buffer.pop()}"
        output += f"{to_array[index]}: {to_array[next]}\n"
        index += 2

    return output


class RoleTimeCheckerCog(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.message_command(name="Извлечь время ролей.")
    async def get_time(self, ctx: discord.ApplicationContext, message: discord.Message):

        reader = easyocr.Reader(['ru'], gpu=True)
        if not message.attachments:
            await ctx.respond("Скриншот не обнаружен.", ephemeral=True)

            return
        await ctx.defer()
        for attachment in message.attachments:

            temp_name = f"temp{random.randint(0, 1000) + random.randint(0, 1000)}.jpg"

            image_data = await attachment.read()
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
            result = reader.readtext(temp_name, detail=0)
            os.remove(temp_name)
            temp = ""
            for item in result:
                temp += item + "\n"
            gc.collect()
            output = text_handler(temp.lower())
            await ctx.send(output_handler(output))
        gc.collect()
        del reader
        await ctx.respond("Готово.", ephemeral=True)
