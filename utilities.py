import json
from collections import namedtuple, Counter

from datetime import datetime
from loguru import logger
from cyrtranslit import to_latin

from amo.entities import Leads


def timer_decorator(func):

    def timer(*args, **kwargs):
        start = datetime.now()
        logger.info(f'Starting timer at {start}')
        func(*args, **kwargs)
        end = datetime.now()
        logger.success(f'Ending timer at {end}, it took {end-start}.')

    return timer

def read_json(file):
    return json.loads('[' + file.read()[:-2] + ']')


def inherit_named_tuple(new_tuple, old_tuple, new_fields):
    return namedtuple(new_tuple, old_tuple._fields+(new_fields))


def has_duplicates(values):
    if len(set(values)) != values:
        return True
    return False


def comprehend_lead_custom_fields(lead):     #TODO make it for every entity
    """Function will take an entity, inherit from it to a new entity,
        adding there additional fields and return a new entity,
        with new fields and it contens.
        In case there is TypeError, and there are no custom fields,
        it will return the basic lead."""
    if lead.custom_fields_values:
        new_fields_temp = [
            ''.join(
                c for c in to_latin(i['field_name'], lang_code='ru') if c.isalpha() or c.isdigit()
               )
            for i in lead.custom_fields_values
           ]

        new_fields = set(new_fields_temp)

        New_lead = inherit_named_tuple('FrLead', Leads, tuple(new_fields))

        ddict = {}
        for i in lead.custom_fields_values:
            dkey = ''.join(c for c in to_latin(i['field_name'], lang_code='ru') if c.isalpha() or c.isdigit())
            try:
                dvalue = str(i['values'][0]['value'])

                for k in i['values'][1::]:
                    dvalue += f', {k["value"]}'
                ddict[dkey] = dvalue
            except IndexError:
                dvalue = i['field_name']
                ddict[dkey] = dvalue

        new_lead = New_lead(**lead._asdict(), **ddict)
        return new_lead
    return lead
