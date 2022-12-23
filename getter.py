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
    """It just checks if the requests get the right status code"""
    request = session.get(url)
    if request.status_code == 200:
        return request
    logger.critical(f'Something is wrong here!: {request.status_code}: {request.text}')
    return False


def build_contents(r, entity):
    """Function basically returns the contents of the request dict,
        with the keys specific for AMO, if they change the keys,
        it should be rebuilt."""
    return json.loads(r.text)['_embedded'][f'{entity}']


def build_next(r):
    """This function checks if there's something in the request body
        from which next url can be taken, if not it just returns False"""
    try:
        return json.loads(r.text)['_links']['next']['href']
    except KeyError:
        return False


def write_contents(entity, contents, amo):
    """"It just writes the specified json file with indent 4."""
    for c in contents:
        with open(
                f'temp_data/{amo}_{entity}_tmp.json', 'a',
                encoding='utf-8'
        ) as file:
            json.dump(c, file, indent=4)
            file.write(',\n')


@timer_decorator
def get_entity(
        entity, logon_data, amo,
        entity_subtype=None, filters=None, code=None
               ):
    """Function creates session with Logon data specified,
        and downloads all the data from the Amo instance,
        writing it to json file {entity}_tmp.json

        It will first try to build the session, check if the token
        is fresh, and refresh it in case it's not.
        If the code was passed as an argument, it will generate new
        token pair.

        It takes following arguments:

        entity -> str; which entity type will be downloaded

        logon_data -> named tuple; For generating logon_data
            use amo.entities.Logon_data

        entity_subtype -> str; it's crucial for such entities as events, where
            a lot of things are lying together, e.g. lead statuses and calls.
            So, it will check first if this argumanet was passed, and then use
            it to make all the further actions.

        tokens_folder  -> str; where are tokens, or where should be stored

        filters: None  -> str; so far it should be a just a string specified
            in Amo API documentanion"""

    # First, check if entity subtype was passed:
    entity_true_name = entity_subtype if entity_subtype else entity
    logger.info(f"Building session for {entity_true_name}...")

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

        write_contents(
            entity_true_name,
            build_contents(r, entity),
            amo
        )
        next_url = build_next(r)

        while True:

            if next_url:
                r = request_entities(next_url, session)
                write_contents(
                    entity_true_name,
                    build_contents(r, entity),
                    amo
                )
                next_url = build_next(r)
                logger.info(next_url)
                count += 50

            else:
                record_last_time(entity_true_name, amo)
                logger.success(f'Approx. {count} records downloaded')
                session.close()
                return True

    logger.critical('Was not able to build session!')
    return False
