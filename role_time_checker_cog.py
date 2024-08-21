import os
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

black_list = ["капитан", "магистрат", "юрист", "агент внутренних дел", "смотритель", "офицер сб", "детектив",
              "кадет сб", "глава службы безопасности", "пилот"]


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
            to_array.append(temp)
            temp = ""
        else:
            temp += text[i]
    buffer = []
    output = ""
    index = 0
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
        if not message.attachments:
            await ctx.respond("Скриншот не обнаружен.", ephemeral=True)
            return
        attachment = message.attachments[0]
        filename = attachment.filename
        await ctx.defer()
        reader = easyocr.Reader(['en', 'ru'], gpu=True)
        await attachment.save('temp.jpg')
        with Image.open('temp.jpg') as img:
            img = img.convert('L')
            obj = ImageEnhance.Contrast(img)
            obj.enhance(100)
            obj = ImageEnhance.Sharpness(img)
            obj.enhance(2)
            obj = ImageEnhance.Brightness(img)
            obj.enhance(4)
            img.save('temp.jpg')
        result = reader.readtext('temp.jpg', detail=0)
        os.remove('temp.jpg')

        temp = ""
        for item in result:
            temp += item + "\n"
        output = text_handler(temp.lower())

        await ctx.respond(output_handler(output))
