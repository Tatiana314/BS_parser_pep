import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT, OUTPUT_FILE, OUTPUT_PRETTY, RESULTS

STATUS = 'Файл с результатами был сохранён: {file_path}.'


def pretty_output(results, *args):
    '''Печать данных в формате таблицы.'''
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def default_output(results, *args):
    '''Печать данных построчно.'''
    for row in results:
        print(*row)


def file_output(results, cli_args):
    '''Создание директории с результатами парсинга.'''
    results_dir = BASE_DIR / RESULTS
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now().strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now}.csv'
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='utf-8') as f:
        csv.writer(f, csv.unix_dialect).writerows(results)
    logging.info(STATUS.format(file_path=file_path))


OUTPUT_MODE = {
    OUTPUT_PRETTY: pretty_output,
    OUTPUT_FILE: file_output,
    None: default_output,
}


def control_output(results, cli_args):
    '''Определение формат вывода данных.'''
    OUTPUT_MODE[cli_args.output](results, cli_args)
