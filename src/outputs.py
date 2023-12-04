import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT

STATUS = 'Файл с результатами был сохранён: {file_path}.'


def control_output(results, cli_args):
    '''Определение формат вывода данных.'''
    output = cli_args.output
    if output == 'pretty':
        pretty_output(results)
    elif output == 'file':
        file_output(results, cli_args)
    else:
        default_output(results)


def pretty_output(results):
    '''Печать данных в формате таблицы.'''
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def default_output(results):
    '''Печать данных построчно.'''
    for row in results:
        print(*row)


def file_output(results, cli_args):
    '''Создание директории с результатами парсинга.'''
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now().strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now}.csv'
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, dialect='unix')
        writer.writerows(results)
    logging.info(STATUS.format(file_path=file_path))
