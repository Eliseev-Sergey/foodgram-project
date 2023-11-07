# 💡 "Фудрграм" - продуктовый помощник

## Ссылка на развернутый проект:

- Домен: https://foodgramm.webhop.me/
- Логин: admin
- Почта: admin@mail.ru
- Пароль: pass_1234

---

## Описание проекта:

Проект "Фудграм" - продуктовый помощник

Сервис позволяет:

- [x] Создавать рецепты
- [x] Подписаться на авторов
- [x] Добавляйте рецепты в избранное и список покупок.
- [x] Скачать список покупок

---

## Инструкция по установке на локальной машине:

1. Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Eliseev-Sergey/foodgram-project.git
```

```
cd backend
```

2. Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если у вас Linux/macOS
    ```
    source env/bin/activate
    ```
* Если у вас windows
    ```
    source env/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

3. Установить зависимости из файла `requirements.txt`:

```
pip install -r requirements.txt
```
4. Выполнить миграции:

```
python3 manage.py migrate
```

5. Запустить проект:

```
python3 manage.py runserver
```

## Инструкция по установке на удаленном сервере:

1. Подключиться к серверу:

```
ssh -i путь_до_файла_с_SSH_ключом/название_файла_закрытого_SSH-ключа login@ip
```

2. Устанавить Docker Compose на сервер:

```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin
```

3. Скопировать на сервер в файл docker-compose.yml.

4. Настроить переменные среды `.env` по примеру указанному в файле `env.example`

5. Выполните команду запуска Docker Compose в режиме «демона»:

```
sudo docker compose -f up -d
```

Проверьте, что все нужные контейнеры запущены:

```
sudo docker compose -f ps
```

## Технологии:

- Python 3.11.1, 
- Django 3.2.3, 
- djangorestframework==3.12.4, 
- PostgreSQL 13.10, 
- Docker.
- python-decouple - Защита секретных данных с помощью пакета [Decouple](https://dontrepeatyourself.org/post/how-to-use-python-decouple-with-django/)

## Автор: Eliseev-Sergey