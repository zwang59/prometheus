from flask_restful import Resource, reqparse
from apps.geofencing.extensions.cache import flask_cache
from apps.geofencing.rest_api_lib.rest_util import to_json_resp, handle_local_rest_error, authentication_required
from apps.geofencing.rest_api_lib.json_api_schemas.audience_profiles.audience_schemas import AudienceProfileSchema
from apps.geofencing.middleware.prometheus.prometheus import Prometheus

API_NAME = 'prometheus'


class AudienceProfileCollection(Resource):

    method_decorators = [authentication_required]

    MIN_LEVEL = 10

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

    def patch(self, audience_id, permission_level=0, **kwargs):
        """
       Handles the updates to existing resources.
       Request data must be formated as a json api resource object or encoded as form data.
       All responses will be in json API format. See http://jsonapi.org/format/#crud for more information.

       .. sourcecode:: http

           PATCH /prometheus/audiences/<string:audience_id> HTTP/1.1
           Host: example.com
           Accept: application/vnd.api+json, application/json, text/*

       **Example response**:

       .. sourcecode:: http

           HTTP/1.1 200 OK
           Content-Type: application/vnd.api+json, application/json, application/x-www-form-urlencoded

       :reqheader Accept: the response content type depends on
       :reqheader Authorization: optional OAuth token to authenticate. Must be present if not included in request body.

       :statuscode 200: OK
       :statuscode 400: bad request
       :statuscode 403: not authorized
       """
        try:
            check_endpoint_permission_level(permission_level, self.MIN_LEVEL)
        except ValueError as error:
            return handle_local_rest_error(error, API_NAME, 403)

        return 'success', 200



def check_endpoint_permission_level(level):
    if 0 < level < 10:
        raise ValueError('Permissions not high enough for endpoint usage!')