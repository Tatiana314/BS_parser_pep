from html.parser import HTMLParser
from bs4 import BeautifulSoup
from requests import RequestException

from exceptions import ParserFindTagException

ERROR_TAG = 'Не найден тег {tag} {attrs}.'
RESPONSE_ERROR = 'Данные со страницы {url} не получены: {error}.'


def get_response(session, url, encoding='utf-8'):
    '''Перехватываем ошибки RequestException.'''
    try:
        response = session.get(url)
        response.encoding = encoding
        return response
    except RequestException as error:
        raise ConnectionError(RESPONSE_ERROR.format(url=url, error=error))


def making_soup(session, url, parsing='lxml'):
    '''Преобразуем HTML-документ в дерево объектов Python.'''
    return BeautifulSoup(get_response(session, url).text, parsing)


def find_tag(soup, tag, attrs=None):
    '''Перехватываем ошибки поиска тегов.'''
    attrs_data = {} if attrs is None else attrs
    searched_tag = soup.find(tag, attrs=attrs_data)
    if searched_tag is None:
        raise ParserFindTagException(ERROR_TAG.format(tag=tag, attrs=attrs))
    return searched_tag
