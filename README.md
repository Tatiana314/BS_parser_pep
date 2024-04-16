# Проект парсинга документации Python

Программа осуществляет сбор информации о нововведениях и статусах версий в Python, а также реализует скачивание архива последней версии Python. Реализована возможность подсчета количества PEP (Python Enhancement Proposals) в каждом статусе и общее количество PEP. Сбор информации организован с официального сайта Python.

Программа осуществляет построчный вывод данных в консоль и в виде таблицы, сохраняет данные в формате csv-файла.

## Технологии
Python3, BeautifulSoup, Requests, PrettyTable 

## Режимы работы парсера
1. `whats-new` - сбор информации о нововведениях в Python: ссылка на статью, заголовок, автор;
2. `latest-versions` - сбор информации о статусов версий Python: ссылка на документацию, версия, статус;
3. `download` - сохранение актуальной документации Python в формате pdf;
4. `pep` - подсчет в каждом статусе и общего количества РЕР, сравнение статусов на странице PEP и в общем списке.

Дополнительные аргументы:
1. -h, --help - вызов справки;
2. -c, --clear-cache - очистка кеша;
3. -o {pretty,file}, --output {pretty,file} - дополнительные способы вывод данных
   - pretty - вывод в консоль таблицей
   - file - сохранение в csv-файл

## Запуск проекта
Клонировать репозиторий:
```
git clone https://github.com/Tatiana314/BS_parser_pep.git && cd BS_parser_pep
```
Создать и активировать виртуальное окружение:
```
python -m venv venv
Linux/macOS: source env/bin/activate
windows: source env/scripts/activate
```
Установить зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```
Ознакомиться со справкой и/или запустить проект в нужном режиме:
```
python main.py --help
```
и/или
```
python main.py [-h] [-c] [-o {pretty,file}] {whats-new, latest-versions, download, pep}
```

## Автор
[Мусатова Татьяна](https://github.com/Tatiana314)
