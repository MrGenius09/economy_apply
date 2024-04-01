from data.config import ADMINS
from aiogram import types
from aiogram.types import ContentType, ReplyKeyboardRemove
from aiogram.dispatcher.filters import Command
from loader import bot, dp, db
from aiogram.dispatcher import FSMContext
from pathlib import Path
from states.all_states import AddCourse, Department, DeleteGroup, DeleteDepartment
import pandas as pd
from datetime import datetime 
import os

#add group
@dp.message_handler(Command("addgroup", prefixes="?/"), user_id=ADMINS)
async def get_course(message: types.Message, state: FSMContext):
    await message.answer("Assalom aleykum yangi guruh qo'shish uchun Guruhni nomini kiriting:", reply_markup=ReplyKeyboardRemove())
    await AddCourse.course_number.set()
    
#add group take name
@dp.message_handler(state=AddCourse.course_number)
async def get_course_year(message: types.Message, state: FSMContext):
    main = message.text
    if main.isdigit():
        await state.update_data(
            {"course_name": message.text}
        )
        await message.answer("Guruh yilini  kiriting:")
        await AddCourse.course_year.set()
    else : 
        await message.answer("Noto'g'ri formatda malumot kiritdingiz. Qayta kiriting:")
        await AddCourse.course_number.set()
    
#add group take year
@dp.message_handler(state=AddCourse.course_year)
async def get_course(message: types.Message, state: FSMContext):
    main = message.text
    if main.isdigit():
        await state.update_data(
            {"course_year": message.text}
        )
        await message.answer("Guruh yo'nalishini  kiriting:")
        await AddCourse.course_direction.set()
    else : 
        await message.answer("Noto'g'ri formatda malumot kiritdingiz. Qayta kiriting:")
        await AddCourse.course_number.set()

#add group finish
@dp.message_handler(state=AddCourse.course_direction)
async def get_course_year(message: types.Message, state: FSMContext):
    await state.update_data(
        {"course_direction" : message.text}
    )
    data = await state.get_data()
    await state.finish()
    
    course_id = data.get("course_name")
    course_year = data.get("course_year")
    course_direction = data.get("course_direction")
    course_full = f'{course_year} {course_direction}'
    try:
        is_group = await db.select_group(group_full = str(course_full), group_id = int(course_id))
    finally :
        await db.close_pool()
    if is_group == []:
        try:
            await db.add_group(int(course_id), int(course_year), course_direction, course_full)
        finally :
            await db.close_pool()
        await message.answer("Guruh bazaga yaratildi.")
    else :
        await message.answer("Guruh bazada avval yaratilgan.")

#add group by ecxel
@dp.message_handler(Command("addgroupexcel", prefixes="?/"), user_id=ADMINS)
async def get_send_excel(msg : types.Message, state : FSMContext):
    await msg.answer("Guruhni bazaga yaratish uchun excel faylni jo'nating!", reply_markup=ReplyKeyboardRemove())

#add group excel
@dp.message_handler(content_types=ContentType.DOCUMENT, user_id=ADMINS)
async def get_group_excel(msg = types.Message):
    os.chdir(os.path.dirname(__file__)) 
    if msg.document.mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        file = await bot.get_file(msg.document.file_id)
        file_path = file.file_path
        await bot.download_file(file_path, 'file.xlsx')
        try:

            df = pd.read_excel('file.xlsx')
        except Exception as ex:
            await msg.answer(str(ex))
        error_list = []
        for index, row in df.iterrows():
            group_id = row['Group_id']
            if not str(group_id).isdigit():
                data = {
                    "status" : False,
                    "message" : "Group id is wrong",
                    "error_id" : f'{row["T/r"]}'
                }
                error_list.append(data)
                continue
            group_year = row["Group_year"]
            if not str(group_year).isdigit():
                data = {
                    "status" : False,
                    "message" : "Group year is wrong",
                    "error_id" : f'{row["T/r"]}'
                }
                error_list.append(data)
                continue
            group_desc = row["Group_desc"]
            group_full = f'{group_year} {group_desc}'
            try:
                is_group = await db.select_group(group_full = str(group_full), group_id = int(group_id))
            finally :
                await db.close_pool()
            if is_group == []:
                try:
                    await db.add_group(int(group_id), int(group_year), group_desc, group_full)
                finally :
                    await db.close_pool()
            else :
                data = {
                    "status" : False,
                    "message" : "Group already exists",
                    "error_id" : f'{row["T/r"]}'
                }
                error_list.append(data)
                continue
        await msg.answer("Guruhlar bazaga muvaffaqiyatli yaratildi.")
        if not len(error_list) == 0:
            await msg.answer("Ammo quyidagi qatorlarda muammolar mavjud!")
            for i in error_list:
                await msg.answer(f"""tartib raqami = {i.get("error_id")} sababi = {i.get("message")}""")
    
#Get group all
@dp.message_handler(Command("groupall", prefixes='?/'), user_id=ADMINS)
async def get_all_group(msg : types.Message):
    month = datetime.now().strftime("%m")
    year = datetime.now().strftime("%Y")
    if int(month) >= 7:
        group_year = int(year) - 3
    else :
        group_year = int(year) - 4
    
    try:
        groups = await db.select_group_all(group_year)
    finally:
        await db.close_pool()
    await msg.answer("Bu yerda bazada mavjud guruhlar ro'yxati")
    group_all = []
    for i in groups:
        group_name = i[1] + (int(year) - i[2]) * 100
        text=f"{group_name}-{i[4]}"
        group_all.append(text)
    text = ', '.join(group_all)
    await msg.answer(text)

#Delete group
@dp.message_handler(Command("deletegroup", prefixes="?/"), user_id=ADMINS)
async def get_delete_group(msg:types.Message, state:FSMContext):
    await msg.answer("Guruhni o'chirish uchun idsini jo'nating:")
    await DeleteGroup.id.set()

#Delete group id
@dp.message_handler(state=DeleteGroup.id)
async def get_delete_group_id(msg:types.Message, state:FSMContext):
    message = msg.text
    if message.isdigit():
        await state.update_data(
            {"id" : msg.text}
        )
        await msg.answer("guruhning full shaklini jo'nating:")
        await DeleteGroup.full.set()
    else: 
        await msg.answer("Noto'g'ri format qayta jo'nating!")
        await DeleteGroup.id.set()

#Delete Group full
@dp.message_handler(state=DeleteGroup.full)
async def get_delete_group_full(msg:types.Message, state: FSMContext):
    await state.update_data(
        {"full" : msg.text}
    )
    data = await state.get_data()
    await state.finish()
    id = data.get("id")
    full = data.get("full")
    try:
        await db.delete_group(group_full = str(full), group_id = int(id))
    finally :
        await db.close_pool()
    await msg.answer("Guruh Muvaffaqiyatli bazadan o'chirildi.")

#add depatment
@dp.message_handler(Command("adddepartment", prefixes="?/"), user_id=ADMINS)
async def get_course_name(message: types.Message, state: FSMContext):
    await message.answer("Assalom aleykum yangi kafedra qo'shish uchun Kafedra nomini kiriting:")
    await Department.full_name.set()
    
#add department take name
@dp.message_handler(state=Department.full_name)
async def get_course_name(message: types.Message, state: FSMContext):
    await state.update_data(
        {"department_name": message.text}
    )
    await message.answer("Kafedraning qisqa nomini kiriting:")
    await Department.short_name.set()
    
#add department finish
@dp.message_handler(state=Department.short_name)
async def get_course_name(message: types.Message, state: FSMContext):
    await state.update_data(
        {"department_name_short": message.text}
    )
    data = await state.get_data()
    await state.finish()
    
    full_name = data.get("department_name")
    short_name = data.get("department_name_short")
    try:
        is_group = await db.select_department(full_name = str(full_name))
    finally :
        await db.close_pool()
    if is_group == []:
        try:
            await db.add_department(full_name, short_name)
        finally :
            await db.close_pool()
        await message.answer("Kafedra bazaga yaratildi.")
    else :
        await message.answer("Kafedra bazada avval yaratilgan.")
        
#departments all
@dp.message_handler(Command("alldepartments", prefixes="?/"), user_id = ADMINS)
async def get_all_departments(msg:types.Message):
    try:
        departments = await db.select_department_all()
    finally:
        await db.close_pool()
    departments_all = []
    for i in departments:
        text = f"{i[2] - i[1]}"
        departments_all.append(text)
    text = ', '.join(departments_all)
    await msg.answer(text)

#Delete department
@dp.message_handler(Command("deletedepartment", prefixes="?/"), user_id=ADMINS)
async def get_delete_group(msg:types.Message, state:FSMContext):
    await msg.answer("Kafedrani o'chirish uchun qisqa nomini jo'nating:")
    await DeleteDepartment.short.set()

#Delete department short
@dp.message_handler(state=DeleteDepartment.short)
async def get_delete_group_id(msg:types.Message, state:FSMContext):
    await state.update_data(
        {"short" : msg.text}
    )
    await msg.answer("Kafedraning to'liq shaklini jo'nating:")
    await DeleteDepartment.full.set()

#Delete department full
@dp.message_handler(state=DeleteGroup.full)
async def get_delete_group_full(msg:types.Message, state: FSMContext):
    await state.update_data(
        {"full" : msg.text}
    )
    data = await state.get_data()
    await state.finish()
    short = data.get("short")
    full = data.get("full")
    try:
        await db.delete_department(full_name = str(full), gshort_name = str(short))
    finally :
        await db.close_pool()
    await msg.answer("Kafedra Muvaffaqiyatli bazadan o'chirildi.")

#Statistika olish
@dp.message_handler(Command("statistics", prefixes="?/"), user_id = ADMINS)
async def get_statistics(msg: types.Message):
    os.chdir(os.path.dirname(__file__)) 
    chat_id = msg.from_user.id
    try:
        users = await db.select_user_all()
    finally:
        await db.close_pool()
    month = datetime.now().strftime("%m")
    year = datetime.now().strftime("%Y")
    try:
        stat = await db.get_last_row()
    finally:
        await db.close_pool()
    if stat == None:
        try: 
            await db.get_all_stat(int(month), int(year), int(0), int(0), int(0), int(0), int(0), int(0), int(0), int(0), int(1), int(0))
        finally:
            await db.close_pool()
    elif int(month) == stat[1] and int(year) == stat[2]:
        try:
            await db.update_stat_register(int(len(users)), int(stat[0]))
        finally:
            await db.close_pool()
    else :
        register = int(stat[11]) + int(1)
        try:
            await db.get_all_stat(int(month), int(year), stat[3], stat[4], stat[5], stat[6], stat[7], stat[8], stat[9], stat[10], int(len(users)), stat[12])
        finally:
            await db.close_pool()
    try:
        data = await db.select_statistics_all()
    finally:
        await db.close_pool()
    df = pd.DataFrame(data, columns=['id', 'month', 'year', 'student_m_id', 'student_a_id', "teacher_m_id", "teacher_a_id", "other_m_id", "other_a_id", "anonymous_m_id", "anonymous_a_id", "registered", "all_data"])
    month = datetime.now().strftime("%m")
    year = datetime.now().strftime("%Y")
    file_name = f"Statistika_{month}_{year}.xlsx"
    df.to_excel(file_name, index=False)
    await bot.send_document(chat_id = chat_id, document=open(file_name, 'rb'))
