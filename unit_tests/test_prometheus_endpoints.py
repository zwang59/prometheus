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

    def test_get_audience_profile(self):
        access_token = self.test_tokens[0].access_token

        # Test get all audience profiles
        resp = self.client.get(url_for('audiences-collection', token=access_token))
        self.assert200(resp)

        print self.audience_profile.to_json()

        # Test get audience profile by id
        resp = self.client.get(url_for('audiences-collection', token=access_token, audience_profile_id=self.audience_profile.id))
        self.assert200(resp)

    def _test_post_audience_profile(self):
        access_token = self.test_tokens[0].access_token

        resp = self.client.post(url_for('audiences-collection', token=access_token))
        self.assert200(resp)

    def _test_patch_audience_profile(self):
        access_token = self.test_tokens[0].access_token

        resp = self.client.patch(url_for('audiences-collection', token=access_token))
        self.assert200(resp)

    def _test_delete_audience_profile(self):
        access_token = self.test_tokens[0].access_token

        resp = self.client.delete(url_for('audiences-collection', token=access_token))
        self.assert200(resp)


if __name__ == '__main__':
    unittest.main()
