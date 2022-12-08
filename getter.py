import sys
import json

from datetime import datetime
from loguru import logger

sys.path.append('..')

from setup import franchize
from amo.logon import build_session
from amo.utilities import timer_decorator


def record_last_time(entity, amo):
    with open(f'last_date_{amo}_{entity}.txt', 'w') as f:
        f.write(str(datetime.now()))



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


def write_contents(entity, contents, amo):
    for c in contents:
        with open(f'temp_data/{amo}_{entity}_tmp.json', 'a', encoding='utf-8') as file:
            json.dump(c, file, indent=4)
            file.write(',\n')


@timer_decorator
def get_entity(entity, logon_data, amo, entity_subtype=None, filters=None, code=None):
    """Function creates session with Logon data specified,
        and downloads all the data from the Amo instance,
        writing it to json file {entity}_tmp.json
        It takes following arguments: \n
        entity -> str; which entity type will be downloaded
        logon_data -> named tuple; For generating logon_data
            use amo.entities.Logon_data
        tokens_folder -> str; where are tokens, or where should be stored
        filters: None -> str; so far it should be a just a string specified
            in Amo API documentanion"""

    entity_true_name = entity_subtype if entity_subtype else entity

    count = 0
    session = build_session(
        logon_data, amo,
        code if code else None
    )

    if session:
        logger.success("Successfully built session!")

        r = request_entities(
            url=build_url(logon_data, entity, filters if filters else None),
            session=session
        )
# NOTE it's all ok with r, it returns the correct dict

        contents = build_contents(r, entity)
        print(contents)
        write_contents(
            entity_true_name,
            contents,
            amo
        )
        next_url = build_next(r)

        while True:

            if next_url:
                r = request_entities(next_url, session)
                write_contents(
                    entity_true_name,
                    build_contents(r, entity_true_name),
                    amo
                )
                next_url = build_next(r)
                logger.info(next_url)
                count += 50

            else:
                record_last_time(entity, amo)
                logger.success(f'Approx. {count} records downloaded')
                session.close()
                return True

    logger.critical('Was not able to build session!')
    return False
