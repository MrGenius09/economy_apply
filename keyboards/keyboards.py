from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from loader import db
from datetime import datetime
from aiogram import types
import json
import os

def load_language(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)
    
def get_language_file(language_code):
    if language_code == 'ru':
        return load_language('ru.json')
    elif language_code == 'uz':
        return load_language('uz.json')
    else:
        return load_language('en.json')

async def category_lang(id):
    try:
        language = await db.select_lang(telegram_id = int(id))
    finally:
        await db.close_pool()
    for i in language:
        language = i[2]
    language_file = get_language_file(language)
    category = ReplyKeyboardMarkup(row_width=1, resize_keyboard = True)
    category.insert(KeyboardButton(text=language_file["royxat"]))
    category.insert(KeyboardButton(text=language_file["anonim_f"]))
    
    return category    

async def numbers_lang(id):
    try:
        language = await db.select_lang(telegram_id = int(id))
    finally:
        await db.close_pool()
    for i in language:
        language = i[2]
    language_file = get_language_file(language)
    numbers = ReplyKeyboardMarkup(row_width=1, resize_keyboard = True)
    numbers.insert(KeyboardButton(text=language_file["numbers"], request_contact = True))

    return numbers

async def course_lang(id):
    try:
        language = await db.select_lang(telegram_id = int(id))
    finally:
        await db.close_pool()
    for i in language:
        language = i[2]
    language_file = get_language_file(language)
    course = ReplyKeyboardMarkup(row_width=2, resize_keyboard = True)
    course.insert(KeyboardButton(text=language_file["1_kurs"]))
    course.insert(KeyboardButton(text=language_file["2_kurs"]))
    course.insert(KeyboardButton(text=language_file["3_kurs"]))
    course.insert(KeyboardButton(text=language_file["4_kurs"]))

    return course

async def menu_lang(id):
    try:
        language = await db.select_lang(telegram_id = int(id))
    finally:
        await db.close_pool()
    for i in language:
        language = i[2]
    language_file = get_language_file(language)
    menu = ReplyKeyboardMarkup(row_width=1, resize_keyboard = True)
    menu.insert(KeyboardButton(text=language_file["talaba"]))
    menu.insert(KeyboardButton(text=language_file["o'qituvchi"]))
    menu.insert(KeyboardButton(text=language_file["boshqa"]))

    return menu

async def get_group_id(course):
    month = datetime.now().strftime("%m")
    year = datetime.now().strftime("%Y")
    course = int(course[0])
    if int(month) >= 7:
        group_year = int(year) - course + 1
    else :
        group_year = int(year) - course
    
    try:
        group = await db.select_group(group_year=int(group_year))
    finally:
        await db.close_pool()
    
    group_btn = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for i in group:
        group_name = i[1] + (course * 100)
        group_btn.insert(KeyboardButton(text=f"{group_name}-{i[4]}"))
    return group_btn

async def get_department_name():
    try:
        department = await db.select_department_all()
    finally:
        await db.close_pool()
    
    department_btn = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for i in department:
        department_btn.insert(KeyboardButton(text=i[2]))
        
    return department_btn

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='🇺🇸English'),
            KeyboardButton(text="🇷🇺Русский"), 
            KeyboardButton(text="🇺🇿O'zbek")
        ]
    ],
    resize_keyboard=True
)