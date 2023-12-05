import argparse
import logging
import sys
from logging.handlers import RotatingFileHandler

from constants import (DATETIME_FORMAT, LOG_DIR, LOG_FILE, OUTPUT_FILE,
                       OUTPUT_PRETTY)

LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'


def configure_argument_parser(available_modes):
    '''Аргументы парсера.'''
    parser = argparse.ArgumentParser(description='Парсер документации Python')
    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера'
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша'
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=(OUTPUT_PRETTY, OUTPUT_FILE),
        help='Дополнительные способы вывода данных'
    )
    return parser


def configure_logging():
    '''Конфигурация логирования.'''
    LOG_DIR.mkdir(exist_ok=True)
    rotating_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=10 ** 6, backupCount=5
    )
    logging.basicConfig(
        datefmt=DATETIME_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler(sys.stdout))
    )
