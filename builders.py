from datetime import datetime
from amo.entities import *


def build_lead_status_changed_tuple(entry):
    """Function returns Lead_status_changes class
        from entities.py"""
    return Lead_status_changed(
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


def build_calls_tuple(entry):
    """Function returns Calls class
        from entities.py"""
    return Calls(
            id_=entry['id'],
            type_=entry['type'],
            entity_id=entry['entity_id'],
            entity_type=entry['entity_type'],
            created_by=entry['created_by'],
            created_at=str(datetime.fromtimestamp(entry['created_at'])),
        )

def build_leads_tuple(entry):
    """Function returns Leads class
        from entities.py"""
    return Leads(
            id_=entry['id'],
            name=entry['name'],
            price=entry['price'],
            responsible_user_id=entry['responsible_user_id'],
            group_id=entry['group_id'],
            status_id=entry['status_id'],
            pipeline_id=entry['pipeline_id'],
            loss_reason_id=entry['loss_reason_id'],
            updated_by=entry['updated_by'],
            updated_at=str(datetime.fromtimestamp(entry['updated_at'])),
            created_at=str(datetime.fromtimestamp(entry['created_at'])),
            closed_at=entry['closed_at'],
            created_by=entry['created_by'],
            closest_task_at=entry['closest_task_at'],
            is_deleted=entry['is_deleted'],
            custom_fields_values=entry['custom_fields_values']
    )
