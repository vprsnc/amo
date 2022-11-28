from datetime import datetime
from amo.entities import *


def build_lead_status_changes_tuple(entry):
    """Function returns Lead_status_changes class
        from entities.py"""
    return Lead_status_change(
            id_=entry['id'],
            type_=entry['type'],
            entity_id=entry['entity_id'],
            entity_type=entry['entity_type'],
            created_by=entry['created_by'],
            created_at=str(datetime.fromtimestamp(entry['created_at'])),
            value_after_id=entry['value_after'][0]['lead_status']['id'],
            value_after_pipeline_id=entry['value_after'][0]\
        ['lead_status']['pipeline_id'],
            value_before_id=entry['value_before'][0]['lead_status']['id'],
            value_before_pipeline_id=entry['value_before'][0]\
        ['lead_status']['pipeline_id'],
            account_id=entry['account_id']
        )
