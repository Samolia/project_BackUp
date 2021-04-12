import requests
import json
import time
import tqdm
from termcolor import colored

from logger import get_logger
from modules.ya_uploader import YaUploader

logger = get_logger('vk_req')

# with open('token.txt') as vk_token:
#     VK_TOKEN = vk_token.read().strip()
#
# with open('yd_token.txt') as yd_token:
#     YA_TOKEN = yd_token.read().strip()

print(colored('Получив screen_name или id пользователя я сохраню фото его профиля на Яндекс диск', 'blue'))
print(colored(f'Понадобятся ваши {colored("Yandex и VK", "cyan")} {colored("токены", "blue")}', "blue"))
time.sleep(1)
YA_TOKEN = input(colored(f'Введите Ваш токен {colored("Yandex:", "cyan")} ', "blue"))
VK_TOKEN = input(colored(f'Введите Ваш токен {colored("VK:", "cyan")} ', "blue"))


class VKUser:

    def __init__(self, token: str, version: str, user_id=None):
        """
        Инициализирую класс VKUser
        :param token: ключ доступа
        :param version: версия API
        :param user_id: объект внимания
        """
        self.token = token
        self.version = version
        self.user_id = user_id
        self.params = {
            'access_token': self.token,
            'v': self.version,
        }

    def do_requests(self, api_method, my_params, request_method='get'):
        """
        Выполнить запрос к VK-API
        """
        requests_url = f'https://api.vk.com/method/{api_method}'
        params = {**self.params, **my_params}
        if request_method == 'get':
            response = requests.get(requests_url, params)
        if request_method == 'put':
            response = requests.put(requests_url, params)
        return response

    def check_user_id(self, user_id: str):
        user_params = {
            'user_ids': user_id
        }
        response = self.do_requests('users.get', user_params).json()
        if 'error' in response:
            logger.error(f'{response["error"]["error_msg"]}')
            print(colored('Такого пользователя не существует', 'red'))
            print('Такого пользователя не существует')
            exit()
        else:
            response = response['response']
            self.user_id = response[0]['id']
            self.user_info = f'{response[0]["first_name"]} {response[0]["last_name"]}'
            print(f'Найден пользователь: {self.user_info}')

    def get_info_about_albums(self):
        """
        Получает информацию об альбомах пользователя
        """
        all_albums = []
        albums_params = {
            'user_id': self.user_id,
            'need_system': 1
        }
        response = self.do_requests('photos.getAlbums', albums_params)
        if response.status_code == 200:
            logger.info(f'{response.status_code} - информация об альбомах найдена')
            response = response.json()['response']
            quantity_albums = response['count']
            counter = 1
            if quantity_albums > 0:
                for album in response['items']:
                    about_album = {str(counter): album['id'], 'album_name': album['title'], 'size': album['size']}
                    all_albums.append(about_album)
                    counter += 1
                logger.info('Информация об альбомах получена')
                self.all_albums = all_albums
                return all_albums
            else:
                logger.info(f'У пользователя {self.user_info} нет альбомов')
        else:
            status_code = f'Код ответа - {response.status_code}\n'
            error_message = response.json()['message']
            logger.error(f'{status_code}{error_message}')

    def print_info_about_albums(self):
        """
        Выводит информацию о доступных к скачиванию альбомах
        """
        all_albums = self.get_info_about_albums()
        counter = 1
        print('Доступные альбомы и количество в них фотографий')
        print('=' * 47)
        for album in all_albums:
            print(f'{counter} {album["album_name"]:=<40}{album["size"]}')
            counter += 1
        print('=' * 47)

    def choice_album(self, user_choice_album):
        """
        Принимает номер выбранного пользователем альбома для скачивания и возвращает его id
        :return: id альбома и его название
        """
        all_albums = self.all_albums
        for album in all_albums:
            if user_choice_album in album:
                selected_album_id = album[user_choice_album]
                album_name = album['album_name']
                logger.info(f'Выбран альбом - {album_name}')
                return selected_album_id, album_name
            else:
                logger.error(f'Выбран номер альбома вне диапазона')

    def get_photos(self, quantity_photo_to_upload=None, album_id=None):
        """
        Получает необходимую информацию о фото, для скачивания на яндекс диск
        :param quantity_photo_to_upload: количество скачиваемых фото
        :param album_id: из какого альбома качать
        :return: список с url и именами фотографий максимального размера
        """
        # если не ввести количество фото для скачивания, скачается 5 штук
        if quantity_photo_to_upload is None:
            quantity_photo_to_upload = 5
        # если не ввести id альбома, то скачаются фото альбома 'profile'
        if album_id is None:
            album_id = 'profile'
        photos_params = {
            'user_id': self.user_id,
            'album_id': album_id,
            'rev': 1,
            'extended': 1,
            'count': quantity_photo_to_upload,
        }
        response = self.do_requests('photos.get', photos_params)
        if response.status_code == 200:
            photos_list = response.json()['response']['items']
            # список с информацией для записи в json
            photos_to_upload = []
            # список с url и именами фотографий максимального размера, для последующего скачивания на яндекс диск
            url_and_names_to_upload = []
            for photo in photos_list:
                about_photo = {}
                quantity_likes = photo['likes']['count']
                photo_date = photo['date']
                max_size_photo = photo['sizes'][-1]
                photo_name = f'{quantity_likes}.jpg'
                for item in photos_to_upload:
                    # если количество лайков одинаково, то добавить дату загрузки
                    if item['file_name'] == photo_name:
                        photo_name = f'{quantity_likes}_{photo_date}.jpg'
                url_and_names_to_upload.append([max_size_photo['url'], photo_name])
                about_photo['file_name'] = photo_name
                about_photo['size'] = max_size_photo['type']
                photos_to_upload.append(about_photo)
            # записывает полученную информацию в json
            with open('about_photos.json', 'w') as json_file:
                json.dump(photos_to_upload, json_file)
            return url_and_names_to_upload
        else:
            status_code = f'Код ответа - {response.status_code}\n'
            error_message = response.json()['message']
            return f'Упс... Что-то пошло не так!\n{status_code} {error_message}\n'

    def ya_upload(self, url_and_names_to_upload, album_name):
        """
        Скачивает необходимое количество фото из выбранного альбома
        """
        root_dir_name = self.user_info
        uploader = YaUploader(YA_TOKEN)
        uploader.create_dir(root_dir_name)
        dir_name = f'{root_dir_name}/{album_name}'
        uploader.create_dir(dir_name)
        print(f'Выбран альбом - "{album_name}". Загружаю фотографии...')
        # прохожу циклом по списку возвращаемому методом get_photos() с url и именами фото
        for photo in tqdm.tqdm(url_and_names_to_upload, desc='Загрузка на яндекс диск', ncols=100, colour='#00ff00'):
            time.sleep(1)
            file_path = f'{dir_name}/{photo[1]}'
            image_url = photo[0]
            uploader.upload(file_path, image_url)
        logger.info('Файлы успешно добавлены на яндекс диск.')
        print('Загрузка завершена. Проверьте яндекс диск.')


def main():
    user_input = input('Введите screen_name или id: ')
    print('=' * 47)
    user1 = VKUser(VK_TOKEN, '5.130', user_input)
    user1.check_user_id(user_input)
    time.sleep(1)
    user1.print_info_about_albums()
    user_choice_album = input(colored('Выберите номер альбома: ', 'blue'))
    quantity_photo_to_upload = input(colored('Выберите количество фото для загрузки: ', 'blue'))
    user_choice_album = input('Выберите номер альбома: ')
    quantity_photo_to_upload = input('Выберите количество фото для загрузки: ')
    user1.choice_album(user_choice_album)
    selected_album_id, album_name = user1.choice_album(user_choice_album)
    user1.get_photos(quantity_photo_to_upload, selected_album_id)
    user1.ya_upload(user1.get_photos(quantity_photo_to_upload, selected_album_id), album_name)
