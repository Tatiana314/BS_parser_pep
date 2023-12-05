from bs4 import BeautifulSoup
from requests import RequestException

from exceptions import ParserFindTagException

ERROR_MSG = 'Не найден тег {tag} {attrs}.'
RESPONSE_ERROR = 'Данные со страницы {url} не получены: {error}.'


def get_response(session, url, encoding='utf-8'):
    '''Перехватываем ошибки RequestException.'''
    try:
        response = session.get(url)
        response.raise_for_status()
        response.encoding = encoding
        return response
    except RequestException as error:
        raise ConnectionError(RESPONSE_ERROR.format(url=url, error=error))


def making_soup(session, url):
    '''Преобразуем HTML-документ в дерево объектов Python.'''
    return BeautifulSoup(get_response(session, url).text, features='lxml')


def find_tag(soup, tag, attrs=None):
    '''Перехватываем ошибки поиска тегов.'''
    attrs_data = {} if attrs is None else attrs
    searched_tag = soup.find(tag, attrs=attrs_data)
    if searched_tag is None:
        raise ParserFindTagException(ERROR_MSG.format(tag=tag, attrs=attrs))
    return searched_tag
