from pathlib import Path

MAIN_DOC_URL = 'https://docs.python.org/3/'
PEPS_MAIN_URL = 'https://peps.python.org/'

BASE_DIR = Path(__file__).parent

DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

EXPECTED_STATUS = {}


OUTPUT_FILE = 'file'
OUTPUT_PRETTY = 'pretty'
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'parser.log'
DOWNLOADS = 'downloads'
RESULTS = 'results'
