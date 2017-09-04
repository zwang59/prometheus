import re
from marshmallow_jsonapi.exceptions import IncorrectTypeError
from marshmallow import ValidationError
from flask_restful import Resource, reqparse
from apps.geofencing.extensions.cache import flask_cache
from apps.geofencing.rest_api_lib.rest_util import to_json_resp, handle_local_rest_error, authentication_required,\
    query_filter, parse_json_api_data
from apps.geofencing.rest_api_lib.json_api_schemas.audience_profiles.audience_schemas import AudienceProfileSchema
# from apps.geofencing.middleware.apollo import triggered_conditions as conditions
from apps.geofencing.middleware.prometheus.prometheus import Prometheus
API_NAME = 'apollo'

class AudienceProfileCollection(Resource):

    method_decorators = [authentication_required]

    def __init__(self):
        self.profile_api = Prometheus()
        super(AudienceProfileCollection, self).__init__()

    def __repr__(self):
        # Needed to ensure an imutable object is cached via the memoize function
        return '<{0}>'.format(self.__class__.__name__)

    @flask_cache.memoize(timeout=50)
    def get_cached_profile_data_resp(self):
        profile_data = self.profile_api.get_all_profiles()
        return AudienceProfileSchema().dumps(profile_data).data

    def get(self,  permission_level=0, **kwargs):
        try:
            check_endpoint_permission_level(permission_level)
        except ValueError as error:
            return handle_local_rest_error(error, 403)
        resp = self.get_cached_profile_data_resp()
        return to_json_resp(resp, 200)

def check_endpoint_permission_level(level):
    if 0 < level < 10:
        raise ValueError('Permissions not high enough for endpoint usage!')