import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from requests_cache import CachedSession
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, MAIN_DOC_URL, PEPS_MAIN_URL
from outputs import control_output
from utils import find_tag, get_response

ARGUMENTS = 'Аргументы командной строки: {args}'
DOWNLOAD_STATUS = 'Архив был загружен и сохранён: {archive_path}'
ERROR_STATUS = (
    '\nНесовпадающий статус: {url}.\n'
    'Статус в карточке: {status_card}.\n'
    'Ожидаемый статус: {status}.\n'
)
MESSAGE_ERROR = 'Сбой в работе программы: {error}'
RESPONSE_ERROR = 'Данные со страницы {url} не получены.'
DATA_ERROR = 'Не найден список c версиями Python.'
PARSER_START = 'Парсер запущен!'
PARSER_END = 'Парсер завершил работу.'


def whats_new(session):
    '''
    Парсинг информации из статей о нововведениях в Python.
    '''
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        logging.error(RESPONSE_ERROR.format(url=whats_new_url), exc_info=True)
        raise ValueError(RESPONSE_ERROR.format(url=whats_new_url))
    soup = BeautifulSoup(response.text, features='lxml')
    div_with_ul = find_tag(
        find_tag(soup, 'section', {'id': 'what-s-new-in-python'}),
        'div', {'class': 'toctree-wrapper'}
    )
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_link = urljoin(whats_new_url, section.find('a')['href'])
        response = get_response(session, version_link)
        if response is None:
            logging.error(
                RESPONSE_ERROR.format(url=whats_new_url), exc_info=True
            )
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        results.append((version_link, h1.text, dl.text.replace('\n', ' ')))
    return results


def latest_versions(session):
    '''
    Парсинг статусов версий Python.
    '''
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        logging.error(RESPONSE_ERROR.format(url=MAIN_DOC_URL), exc_info=True)
        raise ValueError(RESPONSE_ERROR.format(url=MAIN_DOC_URL))
    soup = BeautifulSoup(response.text, 'lxml')
    ul_tags = find_tag(
        soup, 'div', {'class': 'sphinxsidebarwrapper'}
    ).find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        else:
            logging.error(DATA_ERROR, exc_info=True)
            raise ValueError(DATA_ERROR)
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
    response = get_response(session, downloads_url)
    if response is None:
        logging.error(RESPONSE_ERROR.format(url=MAIN_DOC_URL), exc_info=True)
        raise ValueError(RESPONSE_ERROR.format(url=MAIN_DOC_URL))
    soup = BeautifulSoup(response.text, 'lxml')
    pdf_a4_tag = find_tag(
        find_tag(soup, 'table', {'class': 'docutils'}),
        'a', {'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    archive_url = urljoin(downloads_url, pdf_a4_tag['href'])
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = get_response(session, archive_url)
    if response is None:
        logging.error(RESPONSE_ERROR.format(url=MAIN_DOC_URL), exc_info=True)
        raise ValueError(RESPONSE_ERROR.format(url=MAIN_DOC_URL))
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(DOWNLOAD_STATUS.format(archive_path=archive_path))


QUANTITY_PEP = {
    'Статус': 'Количество',
    'Accepted': 0,
    'Active': 0,
    'Deferred': 0,
    'Draft': 0,
    'Final': 0,
    'Provisional': 0,
    'Rejected': 0,
    'Superseded': 0,
    'Withdrawn': 0,
    'Total': 0,
}


def pep(session):
    '''
    Парсинг - подсчет общего количества РЕР и в каждом статусе.
    '''
    response = get_response(session, PEPS_MAIN_URL)
    if response is None:
        logging.error(RESPONSE_ERROR.format(url=PEPS_MAIN_URL), exc_info=True)
        raise ValueError(RESPONSE_ERROR.format(url=PEPS_MAIN_URL))
    soup = BeautifulSoup(response.text, 'lxml')
    tag_abbr = find_tag(
        soup, 'section', {'id': 'numerical-index'}
    ).find_all('abbr')
    QUANTITY_PEP['Total'] = len(tag_abbr)
    for tag in tqdm(tag_abbr):
        pep_url = urljoin(
            PEPS_MAIN_URL,
            tag.find_parent('td').find_next_sibling('td').find('a')['href']
        )
        response_pep = get_response(session, pep_url)
        if response_pep is None:
            logging.error(RESPONSE_ERROR.format(url=pep_url), exc_info=True)
            continue
        soup = BeautifulSoup(response_pep.text, 'lxml')
        pep_status = (
            soup.find(string='Status').find_parent().find_next_sibling().text
        )
        if tag['title'].split()[-1] != pep_status:
            logging.info(ERROR_STATUS.format(
                url=pep_url,
                status_card=pep_status,
                status=tag['title'].split()[-1]
            ))
        if pep_status in QUANTITY_PEP:
            QUANTITY_PEP[pep_status] += 1
    return list(zip(QUANTITY_PEP.keys(), QUANTITY_PEP.values()))


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
