from aiogram.dispatcher.filters.state import State, StatesGroup

    
class Anonim(StatesGroup):
    goal = State()
   
    
class Register(StatesGroup):
    number = State()
    name = State()
  
  
class AddCourse(StatesGroup):
    course_number = State()
    course_year = State()
    course_direction = State() 
    
    
class Department(StatesGroup):
    full_name = State()
    short_name = State()
    
    
class Student(StatesGroup):
    course = State()
    group = State()
    goal = State() 


class Teacher(StatesGroup):
    department = State()
    goal = State()
    
class Others(StatesGroup):
    goal = State()

class ExcelGroup(StatesGroup):
    file = State()

class DeleteGroup(StatesGroup):
    id = State()
    full = State()

class DeleteDepartment(StatesGroup):
    short = State()
    full = State()

class Language(StatesGroup):
    lang = State()