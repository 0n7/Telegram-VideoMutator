# Импортируем необходимые библиотеки
import asyncio

import cv2
import numpy as np
import os
import aiogram
import random
import datetime
import mutagen
import zipfile
bot = aiogram.Bot(token="6340080842:AAGqUFscMontCHNzOfBFGeXAyav0DTQ0npc")
dp = aiogram.Dispatcher(bot)
keyboard = aiogram.types.InlineKeyboardMarkup()
button = aiogram.types.InlineKeyboardButton(text="Добавить шум", callback_data="info")
keyboard.add(button)

@dp.message_handler(commands=["start"])
async def start(message: aiogram.types.Message):
    await message.answer("Добро пожаловать в Video Mutator",reply_markup=keyboard)

@dp.callback_query_handler(lambda query: query.data == "info")
async def info(message:aiogram.types.Message):
    await message.answer("Отправьте MOV или MP4 файл в виде документа")

@dp.message_handler(content_types=["document"])
async def get_video_document(message: aiogram.types.Message):
    print("g")
    # Получаем file_id документа
    file_id = message.document.file_id
    # Получаем объект файла с помощью file_id
    file_path = await bot.get_file(file_id)
    file_naming = str(file_path["file_unique_id"]) + ".zip"
    file_clear_naming = str(file_path["file_unique_id"])
    naming = str(file_path["file_unique_id"]) + "." + (str(file_path["file_path"]).split(".")[-1])
    print(naming)
    print(file_naming)
    zip = zipfile.ZipFile("output/" + file_naming, 'w')
    format = ["MP4","MOV","mp4","mov"]
    if str(file_path["file_path"]).split(".")[-1] in format:

        await bot.download_file(file_path.file_path, naming)

        # Вызываем функцию add_noise с входным и выходным файлами
        for i in range(6):
            add_noise(cv2.VideoCapture(naming), "output", naming,file_clear_naming + "_" + str(i) + ".MP4", i)
            zip.write("output/" + (file_clear_naming + "_" + str(i) + ".MP4"), (file_clear_naming + "_" + str(i) + ".MP4"))
        # add_noise(cv2.VideoCapture(naming), "output",naming)
        # zip.write("output/" + naming, naming),print("output/" + naming)
        zip.close()

        # Отправляем обратно файл с видео с шумом
        await bot.send_document(message.chat.id, open("output/" + file_naming, "rb"))

        # Удаляем локальные файлы
        for i in range(6):
            try:
                os.remove(naming),print("Video Input Deleted")
            except:
                pass
            try:
                os.remove("output/" + file_naming), print("Zip Output Deleted")
            except:
                pass
            os.remove("output/" + (file_clear_naming + "_" + str(i) + ".MP4")),print(str(i) + " Video Output Deleted")
    else:
        print("nothing")

def add_noise(video, output_folder,filename,new_file,videonum):
    print(filename,videonum, new_file)
    # Создаем объект для записи видео в формате MOV
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(os.path.join(output_folder, new_file), fourcc, video.get(cv2.CAP_PROP_FPS),
                          (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))))

    # Читаем видео по кадрам
    while True:
        ret, frame = video.read()
        if not ret:
            break
        nums = [0.001,0.002,0.0026,0.0008,0.003]
        # Генерируем случайный шум с нормальным распределением
        noise = np.random.normal(0, 2, frame.shape[:2])

        # Добавляем шум к кадру с коэффициентом 0.5 и преобразуем в целые числа
        noisy = frame + noise[:, :, np.newaxis] * 0.05 + nums[random.randrange(0,4)]
        noisy = noisy.astype(np.uint8)

        # Записываем кадр в выходной файл
        out.write(noisy)
    file = filename
    metadata = mutagen.File(file)
    print(metadata)
    # Создаем список возможных моделей iPhone
    iphones = ["iPhone 11", "iPhone 11 Pro", "iPhone 11 Pro Max", "iPhone SE (2nd generation)", "iPhone 12",
               "iPhone 12 Pro", "iPhone 12 Pro Max", "iPhone 12 Mini", "iPhone 13", "iPhone 13 Pro",
               "iPhone 13 Pro Max", "iPhone 13 Mini", "iPhone 14", "iPhone 14 Pro", "iPhone 14 Pro Max",
               "iPhone 14 Plus"]

    # Выбираем случайную модель из списка и присваиваем ее полю Make и Model
    metadata['\xa9mak'] = 'Apple'  # Поле Make в формате MP4
    metadata['\xa9mod'] = random.choice(iphones)  # Поле Model в формате MP4

    # Генерируем случайную дату создания в пределах 4-8 дней до текущей даты
    today = datetime.date.today()
    delta = random.randint(4, 8)
    creation_date = today - datetime.timedelta(days=delta)

    # Присваиваем дату создания полю CreationDate в формате YYYY-MM-DDTHH:MM:SSZ
    metadata['CreationDate'] = creation_date.strftime('%Y-%m-%dT%H:%M:%SZ')

    # Генерируем случайные значения для других полей метаданных
    metadata['ExposureTime'] = str(random.uniform(0.01, 0.1))  # Время экспозиции в секундах
    metadata['FNumber'] = str(random.uniform(1.4, 2.8))  # Диафрагма
    metadata['ISO'] = str(random.randint(100, 800))  # Чувствительность ISO
    metadata['FocalLength'] = str(random.uniform(4.2, 6.0))  # Фокусное расстояние в мм
    metadata['GPSLatitude'] = str(random.uniform(-90, 90))  # Широта в градусах
    metadata['GPSLongitude'] = str(random.uniform(-180, 180))  # Долгота в градусах

    # Сохраняем новые метаданные в видеофайл с помощью mutagen
    metadata.save()
    print("saved")
    # Освобождаем ресурсы
    video.release()
    out.release()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())