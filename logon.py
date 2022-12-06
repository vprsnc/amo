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


def read_token(amo, token_type):
    try:
        access_token = Path(f"./tokens/{amo}/{token_type}_token.txt").read_text()
        return access_token
    except FileNotFoundError:
        return None


def token_is_fresh(header, logon_data, amo):
    s = requests.Session()
    s.headers.update(header)
    if s.get(
        f'https://{logon_data.subdomain}.amocrm.ru/api/v4/account',
        headers=header
    ).status_code == 200:
        return s

    s.close()
    sleep(5)
    if refresh_token(logon_data, amo):
        return token_is_fresh(header, logon_data, amo)

    logger.critical("Refreshing token failed!")
    return False


def refresh_token(logon_data, amo):
    new_url = f'https://{logon_data.subdomain}.amocrm.ru/oauth2/access_token'
    read_token(amo, 'refresh')
    logger.info(
        'Refresh token found, using it to get access token...'
    )

    data = namedtuple(
        'data',
        logon_data._fields + ('grant_type', 'refresh_token')
    )

    login_data = data(
        *logon_data,
        grant_type='refresh_token',
        refresh_token=read_token(amo, 'refresh')
    )

    request = requests.post(new_url, data=login_data._asdict())
    request_dict = json.loads(request.text)
    try:
        with open(f'tokens/{amo}/access_token.txt', 'w') as file:
            file.write(request_dict[f"access_token"])
        logger.info('New access token stored.')

        return True

    except KeyError:
        logger.critical(request_dict['hint'])

        return False


def get_token(logon_data, amo, code=None):
    new_url = f'https://{logon_data.subdomain}.amocrm.ru/oauth2/access_token'

    if code:
        logger.info(
            'Authorization code has been passed as an argument, using it to get access token...'
        )

        data = namedtuple('data', logon_data._fields + ('grant_type', 'code'))
        login_data = data(*logon_data, grant_type='authorization_code', code=code)

        request = requests.post(new_url, data=login_data._asdict())
        request_dict = json.loads(request.text)

        if request.status_code == 200:

            for token in ['refresh', 'access']:
                with open(
                        f'tokens/{amo}/{token}_token.txt', 'w',
                        encoding='utf-8') as file:
                    file.write(request_dict[f"{token}_token"])

            return True
        logger.critical(request_dict['hint'])

    logger.critical("You need to provide code/token!")
    return False


def build_session(logon_data, amo, code=None):
    """If auth code is provided, token pair will be fetched,
        otherwise function create a session to Amo API,
        and will try sending request to get account details.
        If request is succesfull, session will be returend;
        Else refresh token will be used to generate acess token."""

    if code:
        get_token(logon_data, amo, code)
        return build_session(logon_data, amo)

    if read_token(amo, 'access') is not None:
        logger.info('Token discoverd, checking if it is fresh...')
        header = {'Authorization': 'Bearer ' + read_token(amo, 'access')}
        session = token_is_fresh(header, logon_data, amo)

        if session is not False:
            logger.success('Token is fresh, building the session.')
            # header = {'Authorization': 'Bearer ' + read_token(amo, 'access')}
            session.mount('https://', HTTPAdapter(max_retries=5))
            return session

        if get_token(logon_data, amo):
            return build_session(logon_data, amo)

        logger.critical("Something went wrong!")

    logger.critical("Tokens weren't found")
