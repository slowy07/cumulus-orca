import json
import uuid
from datetime import datetime, timezone, timedelta
from http import HTTPStatus
from typing import Dict, Any

import fastjsonschema as fastjsonschema
from cumulus_logger import CumulusLogger

INPUT_JOB_ID_KEY = 'asyncOperationId'

OUTPUT_JOB_ID_KEY = 'asyncOperationId'
OUTPUT_JOB_STATUS_TOTALS_KEY = 'job_status_totals'
OUTPUT_GRANULES_KEY = 'granules'
OUTPUT_STATUS_KEY = 'status'
OUTPUT_GRANULE_ID_KEY = 'granule_id'

LOGGER = CumulusLogger()


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    # noinspection SpellCheckingInspection
    """
    Entry point for the request_status_for_job Lambda.
    Args:
        event: A dict with the following keys:
            asyncOperationId: The unique asyncOperationId of the recovery job.
        context: An object provided by AWS Lambda. Used for context tracking.

    Environment Vars: See requests_db.py's get_dbconnect_info for further details.
        'DATABASE_PORT' (int): Defaults to 5432
        'DATABASE_NAME' (str)
        'DATABASE_USER' (str)
        'PREFIX' (str)
        '{prefix}-drdb-host' (str, secretsmanager)
        '{prefix}-drdb-user-pass' (str, secretsmanager)

    Returns: A Dict with the following keys:
        asyncOperationId (str): The unique ID of the asyncOperation.
        job_status_totals (Dict[str, int]): Sums of how many granules are in each particular restoration status.
            pending (int): The number of granules that still need to be copied.
            staged (int): Currently unimplemented.
            success (int): The number of granules that have been successfully copied.
            failed (int): The number of granules that did not copy and will not copy due to an error.
        granules (Array[Dict]): An array of Dicts representing each granule being copied as part of the job.
            granule_id (str): The unique ID of the granule.
            status (str): The status of the restoration of the file. May be 'pending', 'staged', 'success', or 'failed'.

        Or, if an error occurs, see create_http_error_dict
            400 if asyncOperationId is missing. 500 if an error occurs when querying the database.
    """
    with open("schemas/input.json", "r") as raw_schema:
        schema = json.loads(raw_schema.read())

    validate = fastjsonschema.compile(schema)
    validate(event)

    LOGGER.setMetadata(event, context)

    result = {
        OUTPUT_JOB_ID_KEY: uuid.uuid4().__str__(),
        OUTPUT_JOB_STATUS_TOTALS_KEY: {
            'pending': 2,
            'success': 1,
            'failed': 0,
            'staged': 2
        },
        OUTPUT_GRANULES_KEY: [
            {
                OUTPUT_GRANULE_ID_KEY: uuid.uuid4().__str__(),
                OUTPUT_STATUS_KEY: 'staged'
            },
            {
                OUTPUT_GRANULE_ID_KEY: uuid.uuid4().__str__(),
                OUTPUT_STATUS_KEY: 'pending'
            },
            {
                OUTPUT_GRANULE_ID_KEY: uuid.uuid4().__str__(),
                OUTPUT_STATUS_KEY: 'pending'
            },
            {
                OUTPUT_GRANULE_ID_KEY: uuid.uuid4().__str__(),
                OUTPUT_STATUS_KEY: 'success'
            },
            {
                OUTPUT_GRANULE_ID_KEY: uuid.uuid4().__str__(),
                OUTPUT_STATUS_KEY: 'staged'
            }
        ]
    }
    with open("schemas/output.json", "r") as raw_schema:
        schema = json.loads(raw_schema.read())

    validate = fastjsonschema.compile(schema)
    validate(result)
    return result
