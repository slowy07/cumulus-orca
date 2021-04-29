"""
Name: test_request_status_for_granule_unit.py

Description:  Unit tests for request_status_for_granule.py.
"""
import json
import unittest
import uuid
from unittest.mock import Mock

import fastjsonschema

import request_status_for_job_dummy


class TestRequestStatusForJobUnit(
    unittest.TestCase
):  # pylint: disable-msg=too-many-instance-attributes
    """
    TestRequestStatusForGranuleDummy.
    """
    def test_task_output_json_schema(self):
        """
        Checks a realistic output against the output.json.
        """
        result = request_status_for_job_dummy.handler(
            {
                request_status_for_job_dummy.INPUT_JOB_ID_KEY: uuid.uuid4().__str__()
            }, Mock()
        )

        with open("schemas/output.json", "r") as raw_schema:
            schema = json.loads(raw_schema.read())

        validate = fastjsonschema.compile(schema)
        validate(result)
