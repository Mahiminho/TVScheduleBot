import telebot
from telebot import types
from datetime import datetime, time
import time as t
import requests
from bs4 import BeautifulSoup as BS
from PIL import Image, ImageDraw, ImageFont



channels = [
    {'name': 'Новий канал', 'link': 'https://novy.tv/ua/tv/', 'hour': '.current .d-program .v3-dp-link .v3-dp-time', 'program': '.current .d-program .v3-dp-link .v3-dp-details .v3-dp-title'},
    {'name': 'ТЕТ', 'link': 'https://tet.tv/teleprograma/', 'hour': '.container .schedule-item-wrapper .schedule-item .schedule-item__time', 'program': '.container .schedule-item-wrapper .schedule-item .schedule-item__text-container .schedule-item__title'},
    {'name': 'ICTV', 'link': 'https://ictv.ua/ua/programs/#/', 'hour': '.active .tv-program-day-item .tv-program-day-time', 'program': '.active .tv-program-day-item .tv-program-day-additional .tv-program-day-title'},
    {'name': '2+2', 'link': 'https://2plus2.ua/teleprograma/', 'hour': '.tv-items .tv-item .tv-item__left .tv-item__left-inner .tv-item__time', 'program': '.tv-items .tv-item .tv-item__right .tv-item__body .tv-item__title'}
]

def parseChanel(name, link, hour, program):
    site = requests.get(link)
    html = BS(site.content, 'html.parser')

    hours = []
    programs = []
    message = " " * 25 + name + "\n\n"

    for el in html.select(hour):
        time = el.get_text(strip=True)
        hours.append(f"{time[:2]}:{time[-2:]}")

    for el in html.select(program):
        programs.append(el.get_text(strip=True))
    
    for i in range(len(hours)):
        message += hours[i] + " - " + programs[i] + "\n"

    return message

def create_title_image():
    text = "Програма телеканалів станом на\n\n" + " " * 15 + datetime.today().date().strftime("%d.%m.%Y")
    font_size = 30
    image_width = 550
    image_height = 700
    font_path = "verdana.ttf"

    font = ImageFont.truetype(font_path, font_size)

    image = Image.new("RGB", (image_width, image_height), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    text_box = draw.textbbox((0, 0), text, font=font)

    x = (image_width - text_box[2]) // 2
    y = (image_height - text_box[3]) // 2
    draw.text((x, y), text, font=font, fill=(0, 0, 0))

    return image

def create_image_with_text(text, font_size, image_width, image_height, font_path):
    font = ImageFont.truetype(font_path, font_size)

    image = Image.new("RGB", (image_width, image_height), (0, 0, 0))
    draw = ImageDraw.Draw(image)

    text_box = draw.textbbox((0, 0), text, font=font)

    x = (image_width - text_box[2]) // 2
    y = (image_height - text_box[3]) // 2
    draw.text((x, y), text, font=font, fill=(255, 255, 255))

    return image

def createShedules():
    font_size = 20
    target_image_width = 550
    target_image_height = 700
    custom_font_path = "verdana.ttf"
    imageset = []

    img = create_title_image()
    img.save("images/image_title.png")
    imageset.append("images/image_title.png")

    for i in range(len(channels)):
        text = parseChanel(channels[i]['name'], channels[i]['link'], channels[i]['hour'], channels[i]['program'])
        image = create_image_with_text(text, font_size, target_image_width, target_image_height, custom_font_path)
        image.save("images/image_" + str(i) + ".png")
        imageset.append("images/image_" + str(i) + ".png")

    return imageset





bot = telebot.TeleBot('TOKEN')

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Програма телеканалів приходитиме щодня о 8:00.")



    daily_time = time(11, 15)

    while True:
        current_time = datetime.now().time()

        if current_time.hour == daily_time.hour and current_time.minute == daily_time.minute:
            image_paths = createShedules()
            media = [types.InputMediaPhoto(open(image_path, 'rb')) for image_path in image_paths]
            bot.send_media_group(message.chat.id, media)

        t.sleep(60)



bot.polling(none_stop=True)