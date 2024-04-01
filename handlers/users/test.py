import json
import os
print("Current Directory:", os.getcwd())
def load_language(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)
    
def get_language_file(language_code):
    if language_code == 'ru':
        return load_language('handlers/users/ru.json')
    elif language_code == 'uz':
        return load_language('handlers/users/uz.json')
    else:
        return load_language('handlers/users/en.json')