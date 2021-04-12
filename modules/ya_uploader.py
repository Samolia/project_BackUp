import requests

from logger import get_logger


logger = get_logger('ya_uploader')

# with open('yd_token.txt') as yd_token:
#     YA_TOKEN = yd_token.read().strip()


class YaUploader:
    def __init__(self, token: str):
        """
        Инициализирую класс YaUploader
        :param token: ключ доступа
        """
        self.token = token

    def upload(self, file_path: str, image_url: str):
        """
        Загружает файлы на яндекс диск
        """
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = {'Authorization': self.token}
        file_name = file_path.split('/')[-1]
        upload_params = {'url': image_url, 'path': file_path}
        check = requests.get('https://cloud-api.yandex.net/v1/disk/resources',
                             params=upload_params, headers=headers)
        if check.status_code == 404:
            requests.post(url, params=upload_params, headers=headers)
            logger.info(f'"{file_name}" успешно загружен на яндекс диск')
            # проверка выполнения загрузки
        else:
            # если фото уже есть в папке, не грузить повторно
            logger.info(f'"{file_name}" уже есть на яндекс диске')

    def create_dir(self, dir_name: str):
        """
        Создает папку на яндекс диске
        """
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {'path': dir_name}
        headers = {'Authorization': self.token}
        response = requests.put(url, params=params, headers=headers)
        # проверка выполнения создания папки
        if response.status_code == 201:
            logger.info(f'Папка "{dir_name}" создана на яндекс диске!')
        else:
            error_message = response.json()['message']
            logger.info(f'Что-то пошло не так! Код - {response.status_code}: {error_message}')
