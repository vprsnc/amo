import json

from datetime import datetime
from loguru import logger

from setup import franchize
from logon import build_session
from utilities import timer_decorator


logger.add(
     'out.log', backtrace=True, diagnose=True, level='DEBUG'
)


def build_url(logon_data, entity, filters=None):
    url = f'https://{logon_data.subdomain}.amocrm.ru/api/v4/{entity}'
    return url + filters if filters else url


def request_entities(url, session):
    request = session.get(url)
    if request.status_code == 200:
        return request
    else:
        logger.critical(f'Something is wrong here!: {request.text}')
        return False


def build_contents(r, entity):
    return json.loads(r.text)['_embedded'][f'{entity}']


def build_next(r):
    try:
        return json.loads(r.text)['_links']['next']['href']
    except KeyError:
        return False


def write_contents(entity, contents):
    for c in contents:
        with open(f'{entity}_tmp.json', 'a', encoding='utf-8') as file:
            json.dump(c, file, indent=4)
            file.write(',\n')


@timer_decorator
def get_entity(entity, logon_data, tokens_folder, filters=None):

    entity2 = 'events' if entity == 'lead_status_changes' else entity

    count = 0
    session = build_session(logon_data, tokens_folder) 
    r = request_entities(
         url=build_url(logon_data, entity2, filters if filter else None),
         session=session
    )

    write_contents(entity2, build_contents(r, entity2))

    next_url = build_next(r)

    while True:
        if next_url:
            r = request_entities(next_url, session)
            write_contents(entity, build_contents(r, entity2))
            next_url = build_next(r)
            count += 50
        else:
            logger.success(f'Approx. {count} records downloaded')
            session.close()
            break


if __name__ == '__main__':
    url = f'https://{franchize.subdomain}.amocrm.ru/api/v4/events'
    filters = '?filter[type]=lead_status_changed&filter[created_at][from]=1667250000'
    entity = 'lead_status_changes'
    tokens_folder='tokens/franchize'

    get_entity(entity, franchize, tokens_folder, filters=filters)
    with open('lead_status_changes_last_date.txt', 'w') as file:
        file.write(str(datetime.now()))
