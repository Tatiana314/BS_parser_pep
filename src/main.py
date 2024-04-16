import logging
import re
from collections import defaultdict
from urllib.parse import urljoin

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, DOWNLOADS, MAIN_DOC_URL, PEPS_MAIN_URL
from outputs import control_output
from requests_cache import CachedSession
from src.exceptions import ParserFindTagException
from tqdm import tqdm
from utils import find_tag, get_response, making_soup

ARGUMENTS = 'Аргументы командной строки: {args}'
DOWNLOAD_STATUS = 'Архив был загружен и сохранён: {archive_path}'
ERROR_STATUS = (
    '\nНесовпадающий статус: {url}.\n'
    'Статус в карточке: {status_card}.\n'
    'Ожидаемый статус: {status}.\n'
)
MESSAGE_ERROR = 'Сбой в работе программы: {error}'
DATA_ERROR = 'Не найден список c версиями Python.'
PARSER_START = 'Парсер запущен!'
PARSER_END = 'Парсер завершил работу.'


def whats_new(session):
    '''
    Парсинг информации из статей о нововведениях в Python.
    '''
    logs = ''
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for url in tqdm(
        making_soup(session, whats_new_url)
        .select('li.toctree-l1 > a[href!="changelog.html"]')
    ):
        version_link = urljoin(whats_new_url, url['href'])
        try:
            soup = making_soup(session, version_link)
        except ConnectionError as error:
            logs += error
            continue
        results.append((
            version_link,
            find_tag(soup, 'h1').text,
            find_tag(soup, 'dl').text.replace('\n', ' ')
        ))
    if logs:
        logging.error(logs)
    return results


def latest_versions(session):
    '''
    Парсинг статусов версий Python.
    '''
    soup = making_soup(session, MAIN_DOC_URL)
    ul_tags = soup.select('.sphinxsidebarwrapper ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        else:
            logging.error(DATA_ERROR, exc_info=True)
            raise ParserFindTagException(DATA_ERROR)
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        text_match = re.search(pattern, a_tag.text)
        if text_match:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((a_tag['href'], version, status))
    return results


def download(session):
    '''
    Парсинг - скачивает архив документации Python.
    '''
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    soup = making_soup(session, downloads_url)
    archive_url = urljoin(
        downloads_url,
        soup.select_one('table.docutils a[href$="pdf-a4.zip"]')['href']
    )
    DOWNLOADS_DIR = BASE_DIR / DOWNLOADS
    DOWNLOADS_DIR.mkdir(exist_ok=True)
    archive_path = DOWNLOADS_DIR / archive_url.split('/')[-1]
    response = get_response(session, archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(DOWNLOAD_STATUS.format(archive_path=archive_path))


def pep(session):
    '''
    Парсинг - подсчет общего количества РЕР и в каждом статусе.
    '''
    quantity_peps = defaultdict(int)
    logs = ''
    for tag in tqdm(
        making_soup(session, PEPS_MAIN_URL).select('#numerical-index tr')[1:]
    ):
        status = tag.select_one('abbr')['title'].split()[-1]
        pep_url = urljoin(PEPS_MAIN_URL, tag.select_one('a')['href'])
        try:
            soup = making_soup(session, pep_url)
        except ConnectionError as error:
            logs += error
            continue
        pep_status = (
            soup.find(string='Status').find_parent().find_next_sibling().text
        )
        if status != pep_status:
            logs += ERROR_STATUS.format(
                url=pep_url,
                status_card=pep_status,
                status=status
            )
        quantity_peps[pep_status] += 1
    if logs:
        logging.error(logs)
    return (
        ('Статус', 'Количество'),
        *quantity_peps.items(),
        ('Total', sum(quantity_peps.values()))
    )


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    configure_logging()
    logging.info(PARSER_START)
    try:
        arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
        args = arg_parser.parse_args()
        logging.info(ARGUMENTS.format(args=args))
        session = CachedSession()
        if args.clear_cache:
            session.cache.clear()
        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)
        if results:
            control_output(results, args)
    except Exception as error:
        logging.error(MESSAGE_ERROR.format(error=error))
    logging.info(PARSER_END)


if __name__ == '__main__':
    main()
