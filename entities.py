from collections import namedtuple


Logon_data = namedtuple(
    'Logon_data',
    ['client_id', 'client_secret', 'subdomain', 'redirect_uri']
    )


Lead_status_changed = namedtuple(
    'lead_status_changed',
    [
        'id_',
        'type_',
        'entity_id',
        'entity_type',
        'created_by',
        'created_at',
        'value_after_id',
        'value_after_pipeline_id',
        'value_before_id',
        'value_before_pipeline_id',
        'account_id'
        ]
    )

Calls = namedtuple(
    'calls',
    [
        'id_',
        'type_',
        'entity_id',
        'entity_type',
        'created_by',
        'created_at',
        'updated_at',
    ]
)
