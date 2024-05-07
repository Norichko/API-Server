import json 
import pytz 
from datetime import datetime, timezone
from wsgiref.simple_server import make_server

# Определение функции application для обработки запросов
def application(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=utf-8')] 
    path = environ.get('PATH_INFO', '').lstrip('/')
    method = environ.get('REQUEST_METHOD') 

    # Обработка GET-запроса на получение текущего времени
    if method == 'GET' and path:
        return get_current_time(path, start_response)
    # Обработка POST-запроса на конвертацию времени
    elif method == 'POST' and path == 'api/v1/convert':
        return convert_time(environ, start_response)
    # Обработка POST-запроса на вычисление разницы во времени
    elif method == 'POST' and path == 'api/v1/datediff':
        return date_difference(environ, start_response)
    # Обработка запроса на несуществующий ресурс
    else:
        start_response('404 Not Found', headers)
        return [b'Page Not Found']

# GET Функция для получения текущего времени в заданной временной зоне
def get_current_time(timezone_name, start_response):
    headers = [('Content-type', 'text/html; charset=utf-8')]
    if timezone_name:
        try:
            tz = pytz.timezone(timezone_name)  # Получение объекта временной зоны
            current_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %Z')  # Форматирование текущего времени
        except pytz.UnknownTimeZoneError:
            start_response('400 Bad Request', headers) 
            return [b'Unknown Timezone']
    else:
        current_time = datetime.now(timezone.utc)

    start_response('200 OK', headers)
    return [current_time.encode()]

# POST Функция для конвертации времени из одной временной зоны в другую
def convert_time(environ, start_response):
    headers = [('Content-type', 'text/html; charset=utf-8')]
    length = int(environ.get('CONTENT_LENGTH', 0)) 
    if length > 0:
        data = json.loads(environ['wsgi.input'].read(length))  # Чтение данных запроса в формате JSON
        date_string = data.get('date')  # Извлечение даты
        target_tz_name = data.get('target_tz')  # Извлечение целевой временной зоны
        try:
            source_time = datetime.strptime(date_string, '%m.%d.%Y %H:%M:%S')  # Преобразование строки в объект datetime
            source_tz = pytz.timezone(data.get('tz'))  # Получение исходной временной зоны
            target_tz = pytz.timezone(target_tz_name)  # Получение целевой временной зоны
            # Конвертация времени и форматирование результата
            converted_time = source_tz.localize(source_time).astimezone(target_tz).strftime('%Y-%m-%d %H:%M:%S %Z')
        except (KeyError, ValueError, pytz.UnknownTimeZoneError):
            start_response('400 Bad Request', headers)
            return [b'Invalid Request']
    else:
        start_response('400 Bad Request', headers)
        return [b'Missing Data']

    start_response('200 OK', headers) 
    return [converted_time.encode()]

# POST Функция для вычисления разницы во времени между двумя датами
def date_difference(environ, start_response):
    headers = [('Content-type', 'text/html; charset=utf-8')]
    length = int(environ.get('CONTENT_LENGTH', 0)) 
    if length > 0:
        data = json.loads(environ['wsgi.input'].read(length))  # Чтение данных запроса в формате JSON
        first_date_string = data.get('first_date')  # Извлечение первой даты
        first_tz_name = data.get('first_tz')  # Извлечение временной зоны первой даты
        second_date_string = data.get('second_date')  # Извлечение второй даты
        second_tz_name = data.get('second_tz')  # Извлечение временной зоны второй даты
        try:
            first_time = datetime.strptime(first_date_string, '%m.%d.%Y %H:%M:%S')  # Преобразование строки в объект datetime
            first_tz = pytz.timezone(first_tz_name)  # Получение временной зоны первой даты
            first_time = first_tz.localize(first_time)  # Привязка временной зоны к первой дате
            second_time = datetime.strptime(second_date_string, '%I:%M%p %Y-%m-%d')  # Преобразование строки в объект datetime
            second_tz = pytz.timezone(second_tz_name)  # Получение временной зоны второй даты
            second_time = second_tz.localize(second_time)  # Привязка временной зоны ко второй дате
            # Вычисление разницы во времени и преобразование в секунды
            time_diff = abs((second_time - first_time).total_seconds())
        except (KeyError, ValueError, pytz.UnknownTimeZoneError):
            start_response('400 Bad Request', headers) 
            return [b'Invalid Request']
    else:
        start_response('400 Bad Request', headers)
        return [b'Missing Data']

    start_response('200 OK', headers)
    return [str(time_diff).encode()]

# Запуск сервера при запуске файла
if __name__ == '__main__':
    httpd = make_server('', 8000, application)  # Создание сервера
    print("Serving on port 8000...")
    httpd.serve_forever()  # Запуск сервера
