import requests
import json
from time import sleep

from collections import namedtuple
from pathlib import Path
from requests.adapters import HTTPAdapter

from loguru import logger

from setup import franchize


# logger.add(
#     'out.log', backtrace=True, diagnose=True, level='DEBUG'
# )


def read_token(tokens_folder, token_type):
    try:
        access_token = Path(f"./{tokens_folder}/{token_type}_token.txt").read_text()
        return access_token
    except FileNotFoundError:
        return None


def token_is_fresh(header, logon_data):
    s = requests.Session()
    s.headers.update(header)
    if s.get(
        f'https://{logon_data.subdomain}.amocrm.ru/api/v4/account',
        headers=header
    ).status_code == 200:
        sleep(5)
        return s
    else:
        return False


def get_token(logon_data, tokens_folder, code=None):
    new_url = f'https://{logon_data.subdomain}.amocrm.ru/oauth2/access_token'

    if read_token(tokens_folder, 'refresh'):
        logger.info(
            'Refresh token found, using it to get access token...'
        )
        data = namedtuple('data', logon_data._fields + ('grant_type', 'refresh_token'))
        login_data = data(*logon_data, grant_type='refresh_token', refresh_token=read_token(tokens_folder, 'refresh'))

        request = requests.post(new_url, data=login_data._asdict())
        request_dict = json.loads(request.text)

        try:
            with open(f'{tokens_folder}/access_token.txt', 'w') as file:
                file.write(request_dict[f"access_token"])
            logger.info('New access token stored.')
        except KeyError:
            logger.critical(request_dict['hint'])

    elif code:
        logger.info(
            'Authorization code has been passed as an argument, using it to get access token...'
        )
        data = namedtuple('data', logon_data._fields + ('grant_type', 'code'))
        login_data = data(*logon_data, grant_type='authorization_code', code=code)

        request = requests.post(new_url, data=login_data._asdict())
        request_dict = json.loads(request.text)

        for token in ['refresh', 'access']:
            with open(f'{tokens_folder}/{token}_token.txt', 'w') as file:
                file.write(request_dict[f"{token}_token"])

    else:
        logger.critical("You need to provide code/token!")


def build_session(logon_data, tokens_folder, code=None):

    if read_token(tokens_folder, 'access') is not None:
        logger.info('Token discoverd, checking if it is fresh...')
        header = {'Authorization': 'Bearer ' + read_token(tokens_folder, 'access')}
        session = token_is_fresh(header, logon_data)
        if session is not False:
            logger.success('Token is fresh, building the session.')
            # header = {'Authorization': 'Bearer ' + read_token(tokens_folder, 'access')}
            session.mount('https://', HTTPAdapter(max_retries=5))
            return session
        else:
            logger.info('Token is not fresh, refreshing...')
            get_token(logon_data, tokens_folder)
            return build_session(logon_data, tokens_folder)

    else:
        get_token(logon_data, tokens_folder, code)
        return build_session(logon_data, tokens_folder)
