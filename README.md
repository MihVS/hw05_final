# **Yatube**
### **Описание**
Социальная сеть. **Учебный проект**.

Социальная сеть, с возможностью публикации постов, комментирования постов, 
подпиской на авторов и группы. 

### **Стек**
![python version](https://img.shields.io/badge/Python-3.9-yellowgreen?logo=python)
![django version](https://img.shields.io/badge/Django-2.2-yellowgreen?logo=django)
![pytest version](https://img.shields.io/badge/pytest-6.2-yellowgreen?logo=pytest)
![pytest version](https://img.shields.io/badge/Unittest--yellowgreen?logo=unittest)
![pytest version](https://img.shields.io/badge/SQLite-3-yellowgreen?logo=sqlite)
![sorl-thumbnail version](https://img.shields.io/badge/Bootstrap-3-yellowgreen?logo=bootstrap)
![sorl-thumbnail version](https://img.shields.io/badge/HTML--yellowgreen?logo=html5)
![sorl-thumbnail version](https://img.shields.io/badge/thumbnail-12.7-yellowgreen)
![requests version](https://img.shields.io/badge/requests-2.26-yellowgreen)

### **Запуск проекта**

1. Склонируйте репозиторий.

2. Перейдите в папку с кодом и создайте виртуальное окружение:
```
python -m venv venv
```

3. Активируйте виртуальное окружение:
```
source venv\scripts\activate
```
4. Установите зависимости:
```
python -m pip install -r requirements.txt
```
5. Выполните миграции:
```
python manage.py migrate
```
6. Создайте суперпользователя:
```
python manage.py createsuperuser
```
7. Запустите сервер:
```
python manage.py runserver
```
Проект запущен и доступен по адресу: [localhost:8000](http://localhost:8000/)


