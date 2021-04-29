import json
import uuid
from datetime import datetime, timezone, timedelta
from http import HTTPStatus
from typing import Dict, Any

import fastjsonschema as fastjsonschema
from cumulus_logger import CumulusLogger

INPUT_GRANULE_ID_KEY = 'granule_id'
INPUT_JOB_ID_KEY = 'asyncOperationId'

OUTPUT_GRANULE_ID_KEY = 'granule_id'
OUTPUT_JOB_ID_KEY = 'asyncOperationId'
OUTPUT_FILES_KEY = 'files'
OUTPUT_FILENAME_KEY = 'file_name'
OUTPUT_RESTORE_DESTINATION_KEY = 'restore_destination'
OUTPUT_STATUS_KEY = 'status'
OUTPUT_ERROR_MESSAGE_KEY = 'error_message'
OUTPUT_REQUEST_TIME_KEY = 'request_time'
OUTPUT_COMPLETION_TIME_KEY = 'completion_time'

LOGGER = CumulusLogger()


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    # noinspection SpellCheckingInspection
    """
    Entry point for the request_status_for_granule Lambda.
    Args:
        event: A dict with the following keys:
            granule_id: The unique ID of the granule to retrieve status for.
            asyncOperationId (Optional): The unique ID of the asyncOperation.
                May apply to a request that covers multiple granules.
        context: An object provided by AWS Lambda. Used for context tracking.

    Returns: A Dict with the following keys:
        'granule_id' (str): The unique ID of the granule to retrieve status for.
        'asyncOperationId' (str): The unique ID of the asyncOperation.
        'files' (List): Description and status of the files within the given granule. List of Dicts with keys:
            'file_name' (str): The name and extension of the file.
            'restore_destination' (str): The name of the glacier bucket the file is being copied to.
            'status' (str): The status of the restoration of the file. May be 'pending', 'staged', 'success', or 'failed'.
            'error_message' (str, Optional): If the restoration of the file errored, the error will be stored here.
        'request_time' (DateTime): The time, in UTC isoformat, when the request to restore the granule was initiated.
        'completion_time' (DateTime, Optional):
            The time, in UTC isoformat, when all granule_files were no longer 'pending'/'staged'.
            
        Or, if an error occurs, see create_http_error_dict
            400 if granule_id is missing. 500 if an error occurs when querying the database, 404 if not found.
    """
    with open("schemas/input.json", "r") as raw_schema:
        schema = json.loads(raw_schema.read())

    validate = fastjsonschema.compile(schema)
    validate(event)

    LOGGER.setMetadata(event, context)

    result = {
        OUTPUT_GRANULE_ID_KEY: uuid.uuid4().__str__(),
        OUTPUT_JOB_ID_KEY: uuid.uuid4().__str__(),
        OUTPUT_FILES_KEY: [
            {
                OUTPUT_FILENAME_KEY: 'some_filename.ext',
                OUTPUT_RESTORE_DESTINATION_KEY: 'some_destination_bucket',
                OUTPUT_STATUS_KEY: 'success'
            },
            {
                OUTPUT_FILENAME_KEY: 'another_filename.ext',
                OUTPUT_RESTORE_DESTINATION_KEY: 'another_destination_bucket',
                OUTPUT_STATUS_KEY: 'failed',
                OUTPUT_ERROR_MESSAGE_KEY: 'Awesome description of what went wrong.'
            }
        ],
        OUTPUT_REQUEST_TIME_KEY: (datetime.now(timezone.utc) - timedelta(hours=10)).isoformat(),
        OUTPUT_COMPLETION_TIME_KEY: datetime.now(timezone.utc).isoformat()
    }
    with open("schemas/output.json", "r") as raw_schema:
        schema = json.loads(raw_schema.read())

    validate = fastjsonschema.compile(schema)
    validate(result)
    return result
