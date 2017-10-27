import logging
import unittest

from flask import current_app
from flask_testing import TestCase
from flask_restful import url_for

import os

# Path to import locus folder
unitdir = os.path.abspath(os.path.dirname(__file__))
prometheusdir = os.path.dirname(unitdir)
geofencingdir = os.path.dirname(unitdir)
import json

# sys.path.append(os.path.abspath(os.path.join(basedir, '../../../../')))

from apps.geofencing import create_app
from apps.geofencing.config import TestingConfig
from apps.geofencing.rest_api_lib.mock_rest_api_test_data import initialize_db, clear_db, mock_base_admin_data, mock_dashboard_data
from apps.geofencing.extensions.sqldb import sqldb
from apps.geofencing.rest_api_lib.json_api_schemas.audience_profiles.audience_schemas import AudienceProfileSchema


class PrometheusRestAPI(TestCase):
    """
    current state,... doesn't seem to actually be running the tests
    """

    def create_app(self):
        app = create_app(TestingConfig)
        app.config['TESTING'] = True
        app.config['DEBUG'] = True
        app.config['MONGODB_SETTINGS'] = {'DB': 'prometheus_test'}
        app.config['SQLALCHEMY_ECHO'] = False
        return app

    def setUp(self):
        current_app.logger.info("Running setUp")
        initialize_db(self, sqldb)
        mock_base_admin_data(self)
        mock_dashboard_data(self)

    def tearDown(self):
        current_app.logger.info("Running tearDown")
        clear_db(self)

    def _test_test(self):
        self.assertTrue(True)

    def _test_get_audience_profile(self):
        token = self.test_tokens[0].access_token

        header = {
            'Authorization': token
        }

        resp = self.client.get(
            url_for(
                'audiences-collection',
                audience_ref_id=self.audience_profile.ref_id
            ),
            headers=header
        )

        self.assert200(resp)

        resp = self.client.get(
            url_for(
                'audiences-collection',
                query='scatter-plot',
                ref_id=2,
                metric='frequency',
                user_action='conversion',
                time_measure='months',
                time_window=8
            ),
            headers=header
        )
        self.assert200(resp)

    def test_patch_audience_profile(self):
        token = self.test_tokens[0].access_token
        header = {
            'Authorization': token,
            'Content-Type': 'application/vnd.api+json'
        }

        resource_obj = {
            "data": {
                "attributes": {
                    "name": "test",
                    "notes": "test",
                    "avatar": "http://test.png",
                    "appshare": {
                        "data": {
                            "attributes": {
                                "percentage": 0,
                                "total": 0
                            },
                            "type": "appshare"
                        }
                    },
                    "appdata": [
                        {
                            "data": {
                                "attributes": {
                                    "description": "opens",
                                    "graph_max": 0,
                                    "graph_min": 0,
                                    "profile_min": 0,
                                    "units": "test",
                                    "profile_max": 0,
                                    "quantity": 0
                                },
                                "type": "appdata_metric"
                            }
                        },
                        {
                            "data": {
                                "attributes": {
                                    "description": "average rating",
                                    "graph_max": 0,
                                    "graph_min": 0,
                                    "profile_min": 0,
                                    "units": "test",
                                    "profile_max": 0,
                                    "quantity": 0
                                },
                                "type": "appdata_metric"
                            }
                        }
                    ],
                    "demographics": {
                        "data": {
                            "attributes": {
                                "agerange": "test",
                                "familysize": "test",
                                "incomerange": "test",
                                "nationalorigin": "test"
                            },
                            "type": "demographics"
                        }
                    },
                    "behaviors": [
                        {
                            "data": {
                                "attributes": {
                                    "origin": "home",
                                    "distance": {
                                        "data": {
                                            "attributes": {
                                                "graph_max": 0,
                                                "graph_min": 0,
                                                "profile_min": 0,
                                                "units": "test",
                                                "profile_max": 0,
                                                "quantity": 0
                                            },
                                            "type": "distance"
                                        }
                                    },
                                    "destination": "work",
                                    "label": "bus",
                                    "frequency": {
                                        "data": {
                                            "attributes": {
                                                "graph_max": 0,
                                                "graph_min": 0,
                                                "profile_min": 0,
                                                "units": "test",
                                                "profile_max": 0,
                                                "quantity": 0
                                            },
                                            "type": "frequency"
                                        }
                                    },
                                    "duration": {
                                        "data": {
                                            "attributes": {
                                                "graph_max": 0,
                                                "graph_min": 0,
                                                "profile_min": 0,
                                                "units": "test",
                                                "profile_max": 0,
                                                "quantity": 0
                                            },
                                            "type": "duration"
                                        }
                                    }
                                },
                                "type": "habit"
                            }
                        },
                    ],
                },
                "type": "audience_profile",
                "links": {
                    "self": "/prometheus/audiences"
                }
            }
        }

        resp = self.client.patch(
            url_for(
                'audiences-collection',
                audience_ref_id=self.audience_profile.ref_id,
            ),
            headers=header,
            data=json.dumps(resource_obj)
        )
        self.assert200(resp)

if __name__ == '__main__':
    unittest.main()
