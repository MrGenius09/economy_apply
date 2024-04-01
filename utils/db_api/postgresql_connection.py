from typing import Union
import aiogram
import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool
from data import config
from datetime import datetime


class Db_connection:
    def __init__(self) -> None:
        self.pool : Union[Pool, None] = None
    
    async def create(self):
        self.pool = await asyncpg.create_pool(
            user = config.DB_USER,
            password = config.DB_PASS,
            host = config.DB_HOST,
            database = config.DB_NAME
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False,
                      ):
            await self.create()
            async with self.pool.acquire() as connection:
                connection: Connection
                
                async with connection.transaction():
                    if fetch:
                        result = await connection.fetch(command, *args)
                    elif fetchrow:
                        result = await connection.fetchrow(command, *args)
                    elif fetchval:
                        result = await connection.fetchval(command, *args)
                    elif execute:
                        result = await connection.execute(command, *args)
            
            return result
            
    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
        id SERIAL PRIMARY KEY,
        telegram_id BIGINT NOT NULL UNIQUE,
        telegram_name VARCHAR(255) NULL,
        telephone VARCHAR(255) NULL,
        username VARCHAR(255) NULL
        );
        """
        await self.execute(sql, execute=True)
     
    async def create_table_groups(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Groups (
        id SERIAL PRIMARY KEY,
        group_id BIGINT NOT NULL,
        group_year BIGINT NOT NULL,
        group_desc VARCHAR(255) NOT NULL,
        group_full VARCHAR(255) NOT NULL
        );
        """
        await self.execute(sql, execute=True)
               
    async def create_table_anonymous(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Anonymous (
        id SERIAL PRIMARY KEY,
        telegram_id BIGINT NOT NULL,
        role VARCHAR(255) NOT NULL,
        goal VARCHAR(10000) NOT NULL,
        username VARCHAR(255) NULL
        );
        """
        await self.execute(sql, execute=True)
          
    async def create_table_departments(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Departments (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        short_name VARCHAR(255) NOT NULL
        );
        """
        await self.execute(sql, execute=True)
           
    async def create_table_students(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Students (
        id SERIAL PRIMARY KEY,
        telegram_id BIGINT NOT NULL,
        course VARCHAR(255) NOT NULL,
        group_name VARCHAR(250) NULL,
        goal VARCHAR(10000) NOT NULL,
        username VARCHAR(255) NULL
        );
        """
        await self.execute(sql, execute=True)
       
    async def create_table_teachers(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Teachers (
        id SERIAL PRIMARY KEY,
        telegram_id BIGINT NOT NULL,
        department VARCHAR(255) NOT NULL,
        goal VARCHAR(10000) NOT NULL,
        username VARCHAR(255) NULL
        );
        """
        await self.execute(sql, execute=True)
   
    async def create_table_statistics(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Statistics (
        id SERIAL PRIMARY KEY,
        month BIGINT NOT NULL,
        year BIGINT NOT NULL,
        student_m_id BIGINT NULL,
        student_a_id BIGINT NULL, 
        teacher_m_id BIGINT NULL,
        teacher_a_id BIGINT NULL,
        other_m_id BIGINT NULL,
        other_a_id BIGINT NULL,
        anonymous_m_id BIGINT NULL,
        anonymous_a_id BIGINT NULL,
        registred BIGINT NULL,
        all_data BIGINT NULL
        )
        """
        await self.execute(sql, execute=True)

    async def create_language(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Language (
        id SERIAL PRIMARY KEY,
        telegram_id BIGINT NOT NULL UNIQUE,
        language VARCHAR(5) NOT NULL
        )
        """
        await self.execute(sql, execute=True)
       
    async def close_pool(self):
        if self.pool is not None:
            await self.pool.close()
            self.pool = None
    
    @staticmethod ### Shunga tushunish kerak
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(), start=1)
        ])
        return sql, tuple(parameters.values())

    #User qo'shish
    async def add_user(self, telegram_id, name, telephone, username):
        sql = """
        INSERT INTO Users(telegram_id, telegram_name, telephone, username) VALUES($1, $2, $3, $4) returning *
        """
        return await self.execute(sql, telegram_id, name, telephone, username, fetchrow=True)

    #user qidirish
    async def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    #group qoshish
    async def add_group(self, group_id, group_year, group_desc, group_full):
        sql = """
        INSERT INTO Groups(group_id, group_year, group_desc, group_full) VALUES($1, $2, $3, $4) returning *
        """
        return await self.execute(sql, group_id, group_year, group_desc, group_full, fetchrow=True)
    
    #group qidirish
    async def select_group(self, **kwargs):
        sql = "SELECT * FROM Groups WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)
    
    #get group all
    async def select_group_all(self, group_year):
        sql = """
            SELECT * FROM Groups WHERE group_year >= $1
        """
        return await self.execute(sql, group_year, fetch=True)

    #Delete group
    async def delete_group(self, **kwargs):
        sql = "DELETE FROM Groups WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    #kafedra qoshish
    async def add_department(self, full_name, short_name):
        sql = """
        INSERT INTO Departments(full_name, short_name) VALUES($1, $2) returning *
        """
        return await self.execute(sql, full_name, short_name, fetchrow=True)
    
    #kafedra qidirish
    async def select_department(self, **kwargs):
        sql = "SELECT * FROM Departments WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)
    
    #kafedraning hammasini olish
    async def select_department_all(self, **kwargs):
        sql = "SELECT * FROM Departments"
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    #Delete DEPARTMENT
    async def delete_department(self, **kwargs):
        sql = "DELETE FROM Departments WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    #student xabarlarini qoshish
    async def add_students(self, telegram_id, course, group, goal):
        sql = """
        INSERT INTO Students(telegram_id, course, group_name, goal) VALUES($1, $2, $3, $4) returning *
        """
        return await self.execute(sql, telegram_id, course, group, goal, fetchrow=True)
    
    #teacher xabarlarini qoshish
    async def add_teacher_goal(self, telegram_id, department, goal, username):
        sql = """
        INSERT INTO Teachers(telegram_id, department, goal, username) VALUES($1, $2, $3, $4) returning *
        """
        return await self.execute(sql, telegram_id, department, goal, username, fetchrow=True)

    #anonim va boshqa user uchun xabarni saqlash
    async def add_anonymous(self, telegram_id, role, goal, username):
        sql = """
        INSERT INTO Anonymous(telegram_id, role, goal, username) VALUES($1, $2, $3, $4) returning *
        """
        return await self.execute(sql, telegram_id, role, goal, username, execute=True)
    
    #statistika uchun qidirish
    async def select_statistic(self, **kwargs):
        sql = "SELECT * FROM Statistics WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)
    
    #stat get last row
    async def get_last_row(self):
        sql = "SELECT * FROM Statistics ORDER BY id DESC LIMIT 1"
        return await self.execute(sql, fetchrow=True)
    
    #New Register add to Statistic
    async def get_register_stat(self, month, year, registr):
        sql = """INSERT INTO Statistics(month, year, registred) VALUES($1, $2, $3) returning *"""
        return await self.execute(sql, month, year, registr, fetchrow=True)
    
    #New Register add to a new month
    async def get_all_stat(self, month, year, student_m, student_a, teacher_m, teacher_a, other_m, other_a, anonym_m, anonym_a, register, all):
        sql = "INSERT INTO Statistics(month, year, student_m_id, student_a_id, teacher_m_id, teacher_a_id, other_m_id, other_a_id, anonymous_m_id, anonymous_a_id, registred, all_data) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12) returning *"
        return await self.execute(sql, month, year, student_a, student_m, teacher_m, teacher_a, other_m, other_a, anonym_m, anonym_a, register, all, fetchrow=True)
    
    #Data update register
    async def update_stat_register(self, registr, stat_id):
        sql = "UPDATE Statistics SET registred = $1 WHERE id = $2 "
        return await self.execute(sql, registr, stat_id, execute=True)
    
    #Data update anonim
    async def update_stat_anonim(self, anonim_m, anonim_a, all_data, stat_id):
        sql = "UPDATE Statistics SET anonymous_m_id = $1, anonymous_a_id = $2, all_data = $3 WHERE id = $4 "
        return await self.execute(sql, anonim_m, anonim_a, all_data, stat_id, execute=True)
    
    #Data update student
    async def update_stat_student(self, student_m, student_a, all_data, stat_id):
        sql = "UPDATE Statistics SET student_m_id = $1, student_a_id = $2, all_data = $3 WHERE id = $4 "
        return await self.execute(sql, student_m, student_a, all_data, stat_id, execute=True)
    
    #Data update teacher
    async def update_stat_teacher(self, student_m, student_a, all_data, stat_id):
        sql = "UPDATE Statistics SET teacher_m_id = $1, teacher_a_id = $2, all_data = $3 WHERE id = $4 "
        return await self.execute(sql, student_m, student_a, all_data, stat_id, execute=True)
    
    #Data update student
    async def update_stat_other(self, other_m, other_a, all_data, stat_id):
        sql = "UPDATE Statistics SET other_m_id = $1, other_a_id = $2, all_data = $3 WHERE id = $4 "
        return await self.execute(sql, other_m, other_a, all_data, stat_id, execute=True)
    
    #Statistikaning hammasini olish
    async def select_statistics_all(self, **kwargs):
        sql = "SELECT * FROM Statistics"
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)
    
    #Users All
    async def select_user_all(self, **kwargs):
        sql = "SELECT * FROM Users"
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)
    
    #Language add
    async def add_lang(self, telegram_id, lang):
        sql = "INSERT INTO Language(telegram_id, language) VALUES($1, $2) returning *"
        return await self.execute(sql, telegram_id, lang, fetchrow=True)
    
    #Language search
    async def select_lang(self, **kwargs):
        sql = "SELECT * FROM Language WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)
    
    #language update
    async def update_lang(self, lang, telegram_id):
        sql = "UPDATE Language SET language = $1 WHERE telegram_id = $2"
        return await self.execute(sql, lang, telegram_id, execute=True)
