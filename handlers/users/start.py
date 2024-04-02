from aiogram import types, bot
from aiogram.dispatcher.filters.builtin import CommandStart
from keyboards.keyboards import category_lang, menu_lang, numbers_lang, course_lang, get_group_id, get_department_name, keyboard
from loader import dp, db
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from states.all_states import Register, Anonim, Student, Teacher, Others, Language
from datetime import datetime
import json
import os


def load_language(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)
    
def get_language_file(language_code):
    os.chdir(os.path.dirname(__file__))
    if language_code == 'ru':
        return load_language('ru.json')
    elif language_code == 'uz':
        return load_language('uz.json')
    else:
        return load_language('en.json')


#Start buyruq
@dp.message_handler(CommandStart(), state = '*')
async def start(message: types.Message, state: FSMContext ):
    await state.finish()
    try:
        is_user_lang = await db.select_lang(telegram_id=int(message.from_user.id))
    finally :
        await db.close_pool()    
    if is_user_lang == []:
        await message.answer(f"""Hello, {message.from_user.full_name}! Welcome to the application bot of the "Economics" faculty.\nЗдравствуйте, {message.from_user.full_name}! Добро пожаловать в прикладной бот факультета «Экономика».\nSalom, {message.from_user.full_name}! "Iqtisodiyot" fakultetining murojaat botiga xush kelibsiz.""")
        await message.answer("Choose your language:\nВыберите ваш язык:\nTilni tanlang:", reply_markup=keyboard)
        await Language.lang.set()
    else:
        try:
            is_user_member = await db.select_user(telegram_id=int(message.from_user.id))
        finally:
            await db.close_pool()
        for i in is_user_lang:
            language = i[2]
        if language == 'en' or language == 'uz' or language == 'ru':
            language_file = get_language_file(language)
            if is_user_member == []:
                await message.answer(language_file["start"], reply_markup=await category_lang(message.from_user.id))
            else:
                await message.answer(language_file["menu"], reply_markup=await menu_lang(message.from_user.id))
        else: 
            await message.answer(f"""Hello, {message.from_user.full_name}! Welcome to the application bot of the "Economics" faculty.\nЗдравствуйте, {message.from_user.full_name}! Добро пожаловать в прикладной бот факультета «Экономика».\nSalom, {message.from_user.full_name}! "Iqtisodiyot" fakultetining murojaat botiga xush kelibsiz.""")
            await message.answer("Choose your language:\nВыберите ваш язык:\nTilni tanlang:", reply_markup=keyboard)
            await Language.lang.set()

#Set language
@dp.message_handler(state=Language.lang)
async def get_number(message: types.Message, state : FSMContext):
    if message.text == '🇷🇺Русский' or '🇺🇸English' or "🇺🇿O'zbek":
        try:
            is_user_member = await db.select_user(telegram_id=int(message.from_user.id))
        finally :
            await db.close_pool()
        if message.text == '🇺🇸English':
            language = 'en'
        elif message.text == '🇷🇺Русский':
            language = 'ru'
        else :
            language = 'uz'
        language_file = get_language_file(language)
        try:
            is_user_lang = await db.select_lang(telegram_id=int(message.from_user.id))
        finally :
            await db.close_pool()
        if is_user_lang == []:  
            try:
                await db.add_lang(message.from_user.id, language)
            finally:
                await db.close_pool()
        else:
            try:
                await db.update_lang(language, message.from_user.id)
            finally:
                await db.close_pool()
        if is_user_member == []:
            await message.answer(language_file["start"], reply_markup=await category_lang(message.from_user.id))
        else:
            await message.answer(language_file["menu"], reply_markup=await menu_lang(message.from_user.id))
        await state.finish()
    else : 
        await message.answer("Wrong command Choose your language:\nНеправильная командаВыберите ваш язык:\nNoto'g'ri buyruq. Tilni tanlang:", reply_markup=keyboard)
        await Language.lang.set()

#Normal ECHO
@dp.message_handler(state=None)
async def get_main_goal(msg : types.Message):
    try:
        language = await db.select_lang(telegram_id = msg.from_user.id)
    finally:
        await db.close_pool()
    for i in language:
            language = i[2]
    language_file = get_language_file(language)
    if msg.text == 'Anonim foydalanuvchi' or msg.text == "Anonymous user" or msg.text == "Анонимный пользователь" or msg.text == '/anonim_message':
        await msg.answer(language_file['anonim'], reply_markup=ReplyKeyboardRemove())
        await Anonim.goal.set()
    elif msg.text == "Ro'yxatdan o'tish" or msg.text == "Sign up" or msg.text == "Зарегистрироваться":
        await msg.answer(language_file["register"], reply_markup=await numbers_lang(msg.from_user.id))
        await Register.number.set()
    elif msg.text == "👨‍🎓👩‍🎓Fakultut talabasi" or msg.text == "👨‍🎓👩‍🎓Faculty student" or msg.text == "👨‍🎓👩‍🎓Студент факультета":
        await msg.answer(language_file["kurs"], reply_markup=await course_lang(msg.from_user.id))
        await Student.course.set()
    elif msg.text == "👩‍🏫👨‍🏫Fakultet o'qituvchisi" or msg.text == "👩‍🏫👨‍🏫Faculty teacher" or msg.text == "👩‍🏫👨‍🏫Преподаватель факультета":
        await msg.answer(language_file["kafedra"], reply_markup=await get_department_name())
        await Teacher.department.set()
    elif msg.text == "Boshqa" or msg.text == "Other" or msg.text == "Другой":
        await msg.answer(language_file["other"], reply_markup=ReplyKeyboardRemove())
        await Others.goal.set()
    elif msg.text == "/lang":
        await msg.answer("Choose your language:\nВыберите ваш язык:\nTilni tanlang:", reply_markup=keyboard)
        await Language.lang.set()
    else:
        await msg.answer(language_file["false"])


#Anonim xabar
@dp.message_handler(state=Anonim.goal)
async def get_anonim_goal(msg : types.Message, state : FSMContext):
    role = 'anonim'
    try:
        await db.add_anonymous(msg.from_user.id, role, msg.text, msg.from_user.username)
    finally :
        await db.close_pool()
    month = datetime.now().strftime("%m")
    year = datetime.now().strftime("%Y")
    try:
        stat = await db.get_last_row()
    finally:
        await db.close_pool()
    if stat == None:
        try: 
            await db.get_all_stat(int(month), int(year), int(0), int(0), int(0), int(0), int(0), int(0), int(1), int(1), int(0), int(0))
        finally:
            await db.close_pool()
    elif int(month) == stat[1] and int(year) == stat[2]:
        anonim_m = int(stat[10]) + 1
        anonim_a = int(stat[9]) + 1
        all_data = int(stat[12]) + 1
        try:
            await db.update_stat_anonim(int(anonim_m), int(anonim_a), int(all_data), int(stat[0]))
        finally:
            await db.close_pool()
    else :
        anonim_m = int(stat[10]) + 1
        anonim_a = int(stat[9]) + 1
        all_data = int(stat[12]) + 1
        try:
            await db.get_all_stat(int(month), int(year), stat[3], stat[4], stat[5], stat[6], stat[7], stat[8], int(anonim_m), int(anonim_a), int(11), int(all_data))
        finally:
            await db.close_pool()
    try:
        language = await db.select_lang(telegram_id = msg.from_user.id)
    finally:
        await db.close_pool()
    for i in language:
        language = i[2]
    language_file = get_language_file(language)
    await msg.answer(language_file["anonim_last"])
    await state.finish()
    

#Registratsiya
@dp.message_handler(state=Register.number, content_types=['contact']) 
async def get_number(message: types.Message, state : FSMContext):
    number = message['contact']
    try:
        language = await db.select_lang(telegram_id = message.from_user.id)
    finally:
        await db.close_pool()
    for i in language:
        language = i[2]
    language_file = get_language_file(language)
    await state.update_data(
        {"phone_number": number['phone_number']}
    )
    await message.answer(language_file["register_last"], reply_markup=ReplyKeyboardRemove())
    await Register.name.set()
    
    
@dp.message_handler(state=Register.name)
async def get_full_name(message: types.Message, state: FSMContext):
    try:
        language = await db.select_lang(telegram_id = message.from_user.id)
    finally:
        await db.close_pool()
    for i in language:
        language = i[2]
    language_file = get_language_file(language)
    await state.update_data(
        {'name' : message.text}
    )
    data = await state.get_data()
    name = data.get("name")
    phone_number = data.get("phone_number")
    await state.finish()
    try:
        await db.add_user(message.from_user.id, name, phone_number, message.from_user.username)
    finally :
        await db.close_pool()
    await message.answer(language_file["register_l"], reply_markup=await menu_lang(message.from_user.id))
    

#Menu Student type  
@dp.message_handler(state=Student.course)
async def get_course(msg : types.Message, state : FSMContext):
    try:
        language = await db.select_lang(telegram_id = msg.from_user.id)
    finally:
        await db.close_pool()
    for i in language:
        language = i[2]
    language_file = get_language_file(language)
    await state.update_data(
        {'course' : msg.text}
    )
    await msg.answer(language_file["guruh"], reply_markup = await get_group_id(msg.text))
    await Student.group.set()
        
        
@dp.message_handler(state=Student.group)
async def get_group(msg : types.Message, state : FSMContext):
    data = await state.get_data()
    course_main = data.get("course")
    month = datetime.now().strftime("%m")
    year = datetime.now().strftime("%Y")
    course = int(course_main[0])
    if int(month) >= 7:
        group_year = int(year) - course + 1
    else :
        group_year = int(year) - course
    try: 
        group = await db.select_group(group_year=int(group_year))
    finally :
        await db.close_pool()
    genius = 0
    for i in group:
        group_name = i[1] + (course * 100)
        if msg.text == f"{group_name}-{i[4]}":
            await state.update_data(
                {"group" : msg.text}
            )
            genius = 1
    try:
        language = await db.select_lang(telegram_id = msg.from_user.id)
    finally:
        await db.close_pool()
    for i in language:
        language = i[2]
    language_file = get_language_file(language)        
    if genius == 1:        
        await msg.answer(language_file["other"], reply_markup=ReplyKeyboardRemove())
        await state.set_state(Student.goal)
    else :       
        await msg.answer(language_file["false"], reply_markup = await get_group_id(course_main)) 
        await Student.group.set()   
    
        
@dp.message_handler(state=Student.goal )
async def get_group(msg : types.Message, state : FSMContext):
    await state.update_data(
        {"goal" : msg.text}
    )
    data = await state.get_data()
    course = data.get("course")
    group = data.get("group")
    goal = data.get("goal")
    try:
        await db.add_students(msg.from_user.id, course, group, goal)
    finally :
        await db.close_pool()
    month = datetime.now().strftime("%m")
    year = datetime.now().strftime("%Y")
    try:
        stat = await db.get_last_row()
    finally:
        await db.close_pool()
    if stat == None:
        try: 
            await db.get_all_stat(int(month), int(year), int(1), int(1), int(0), int(0), int(0), int(0), int(0), int(0), int(0), int(0))
        finally:
            await db.close_pool()
    elif int(month) == stat[1] and int(year) == stat[2]:
        anonim_m = int(stat[3]) + 1
        anonim_a = int(stat[4]) + 1
        all_data = int(stat[12]) + 1
        try:
            await db.update_stat_student(int(anonim_m), int(anonim_a), int(all_data), int(stat[0]))
        finally:
            await db.close_pool()
    else :
        anonim_m = int(stat[3]) + 1
        anonim_a = int(stat[4]) + 1
        all_data = int(stat[12]) + 1
        try:
            await db.get_all_stat(int(month), int(year), int(anonim_m), int(anonim_a), stat[5], stat[6], stat[7], stat[8], stat[9], stat[10], int(11), int(all_data))
        finally:
            await db.close_pool()
    try:
        language = await db.select_lang(telegram_id = msg.from_user.id)
    finally:
        await db.close_pool()
    for i in language:
        language = i[2]
    language_file = get_language_file(language)
    await msg.answer(language_file["student_last"])
    await state.finish()
 

#Menu Teacher type  
@dp.message_handler(state=Teacher.department)
async def get_department(msg : types.Message, state : FSMContext):
    try:
        language = await db.select_lang(telegram_id = msg.from_user.id)
    finally:
        await db.close_pool()
    for i in language:
        language = i[2]
    language_file = get_language_file(language)
    try:
        departments = await db.select_department_all()
    finally :
        await db.close_pool()
    economy = 0
    for i in departments:
        if msg.text == i[2]:
            await state.update_data(
                {'department' : msg.text}
            )
            await msg.answer(language_file["other"], reply_markup=ReplyKeyboardRemove())
            economy = 1
            break
        else :
            continue
    if economy == 1:
        await Teacher.goal.set()
    else:
        await msg.answer(language_file["false"], reply_markup=await get_department_name())    
    

@dp.message_handler(state=Teacher.goal)
async def get_teacher_goal(msg : types.Message, state : FSMContext):
    await state.update_data(
        {'goal' : msg.text}
        )     
    data = await state.get_data()
    department = data.get("department")
    goal = data.get("goal")
    try:
        await db.add_teacher_goal(msg.from_user.id, department, goal, msg.from_user.username)
    finally :
        await db.close_pool()
    month = datetime.now().strftime("%m")
    year = datetime.now().strftime("%Y")
    try:
        stat = await db.get_last_row()
    finally:
        await db.close_pool()
    if stat == None:
        try: 
            await db.get_all_stat(int(month), int(year), int(0), int(0), int(1), int(1), int(0), int(0), int(0), int(0), int(0), int(0))
        finally:
            await db.close_pool()
    elif int(month) == stat[1] and int(year) == stat[2]:
        teacher_m = int(stat[5]) + 1
        teacher_a = int(stat[6]) + 1
        all_data = int(stat[12]) + 1
        try:
            await db.update_stat_teacher(int(teacher_m), int(teacher_a), int(all_data), int(stat[0]))
        finally:
            await db.close_pool()
    else :
        teacher_m = int(stat[5]) + 1
        teacher_a = int(stat[6]) + 1
        all_data = int(stat[12]) + 1
        try:
            await db.get_all_stat(int(month), int(year), stat[3], stat[4], int(teacher_m), int(teacher_a), stat[7], stat[8], stat[9], stat[10], int(11), int(all_data))
        finally:
            await db.close_pool()
    try:
        language = await db.select_lang(telegram_id = msg.from_user.id)
    finally:
        await db.close_pool()
    for i in language:
        language = i[2]
    language_file = get_language_file(language)
    await msg.answer(language_file["student_last"])
    await state.finish()

#Menu Other type
@dp.message_handler(state=Others.goal)
async def get_other_goal(msg : types.Message, state : FSMContext):
    role = 'registred'
    try:
        await db.add_anonymous(msg.from_user.id, role, msg.text, msg.from_user.username)
    finally :
        await db.close_pool()
    month = datetime.now().strftime("%m")
    year = datetime.now().strftime("%Y")
    try:
        stat = await db.get_last_row()
    finally:
        await db.close_pool()
    if stat == None:
        try: 
            await db.get_all_stat(int(month), int(year), int(0), int(0), int(0), int(0), int(1), int(1), int(0), int(0), int(0), int(1))
        finally:
            await db.close_pool()
    elif int(month) == stat[1] and int(year) == stat[2]:
        other_m = int(stat[7]) + 1
        other_a = int(stat[8]) + 1
        all_data = int(stat[12]) + 1
        print(other_m)
        print(other_a)
        try:
            await db.update_stat_other(int(other_m), int(other_a), int(all_data), int(stat[0]))
        finally:
            await db.close_pool()
    else :
        other_m = int(stat[7]) + 1
        other_a = int(stat[8]) + 1
        all_data = int(stat[12]) + 1
        try:
            await db.get_all_stat(int(month), int(year), stat[3], stat[4], stat[6], stat[7], int(other_m), int(other_a), stat[9], stat[10], int(11), int(all_data))
        finally:
            await db.close_pool()
    try:
        language = await db.select_lang(telegram_id = msg.from_user.id)
    finally:
        await db.close_pool()
    for i in language:
        language = i[2]
    language_file = get_language_file(language)
    await msg.answer(language_file["student_last"])
    await state.finish()