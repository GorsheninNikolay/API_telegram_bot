API_telegram_bot
==

Данный проект представляет собой бот в telegram, который сообщает о статусе проверки домашнего задания. Если ревьюер отклонил или же принял проект, отправляется информационное сообщение лично мне в telegram. Токены надежно спрятаны :smiley:

# Развертывание проекта

1. Зайдите в GitBash, при необходимости установите
2. При помощи команд 

Перейти в каталог:
```
cd "каталог"
```
Подняться на уровень вверх:
```
cd .. 
```
:exclamation: Перейдите в нужный каталог для клонирования репозитория :exclamation:

3. Клонирование репозитория:
```
git clone https://github.com/GorsheninNikolay/API_telegram_bot
```
4. Перейти в каталог:
```
cd API_telegram_bot
```
5. Создание виртуальной среды:
```
python -m venv venv 
```
6. Активация виртуальной среды:
```
source venv/Scripts/activate
```
7. Установить зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
8. Запуск проекта:
```
python homework.py
```

Готово! 😉

Системные требования
----

- Python 3.7.3

- GitBash

