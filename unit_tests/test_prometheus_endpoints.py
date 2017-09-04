import logging
import json
import unittest

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
from apps.geofencing.middleware.prometheus.prometheus import Prometheus
# from apps.geofencing.middleware.prometheus.unit_tests.test_prometheus_middleware import mock_profile_data
from apps.geofencing.dbmodels.mongodb.util import load_yaml
from apps.geofencing.rest_api_lib.mock_rest_api_test_data import initialize_db, clear_db, mock_base_admin_data, mock_base_geofence_data, log_in_test_user
from apps.geofencing.extensions.sqldb import sqldb


class PrometheusRestAPI(TestCase):
    """
    current state,... doesn't seem to actually be running the tests
    """
    test_tokens = []
    pandora = None
    TESTING = True

    def setUp(self):
        print("running setup")
        initialize_db(self, sqldb)
        mock_base_admin_data(self)
        self.prometheus = Prometheus()
        profile = self.prometheus.mock_profile_data()

        # self.create_app()
    #
    def tearDown(self):
        print("tearing down")
        clear_db(self)


    def create_app(self):
        print("creating app ")
        app = create_app(TestingConfig)
        app.config['TESTING'] = True
        app.config['MONGODB_SETTINGS'] = {'DB': 'prometheus_test'}
        app.config['SQLALCHEMY_ECHO'] = False
        return app

    def test_audience_profile(self):
        print("running test")
        print(url_for('audiences-collection'))
        access_token = self.test_tokens[0].access_token

        resp = self.client.get(url_for('audiences-collection',token = access_token))
        self.assert200(self,resp)

        print(resp)
        # print(type(resp))
        # print(dir(resp))

        # Query by name
        # nameprofile = self.prometheus.get_profile("JENNY")
        # self.assertEqual(nameprofile.name, "JENNY")

        # Pull all profile data
        # profiles = self.prometheus.get_all_profiles()
        # self.assertTrue(len(profiles) > 0)
#
if __name__ == '__main__':
    unittest.main()


