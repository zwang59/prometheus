
from flask import current_app
from flask_restful import Resource, reqparse
from apps.geofencing.extensions.cache import flask_cache
from apps.geofencing.rest_api_lib.rest_util import to_json_resp, handle_local_rest_error, check_endpoint_permission_level, \
    authentication_required
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

    def get(self, audience_profile_id=None, permission_level=0, **kwargs):
        try:
            check_endpoint_permission_level(permission_level, self.MIN_LEVEL)
        except ValueError as error:
            return handle_local_rest_error(error, 403)

        if audience_profile_id is None:
            resp = self.get_cached_all_profile_data_resp()
            return to_json_resp(resp, 200)

        resp = self.get_cached_profile_data_resp(audience_profile_id)
        return to_json_resp(resp, 200)

    def post(self, permission_level=0, **kwargs):
        try:
            check_endpoint_permission_level(permission_level, self.MIN_LEVEL)
        except ValueError as error:
            return handle_local_rest_error(error, API_NAME, 403)

        return 'success', 200

    def patch(self, audience_id=None, permission_level=0, **kwargs):
        try:
            check_endpoint_permission_level(permission_level, self.MIN_LEVEL)
        except ValueError as error:
            return handle_local_rest_error(error, API_NAME, 403)

        return 'success', 200

    def delete(self, audience_id=None, permission_level=0, **kwargs):
        try:
            check_endpoint_permission_level(permission_level, self.MIN_LEVEL)
        except ValueError as error:
            return handle_local_rest_error(error, API_NAME, 403)

        return 'success', 200


    # @flask_cache.memoize(timeout=50)
    def get_cached_all_profile_data_resp(self):
        profile_objs = self.profile_api.get_all_profiles()
        return AudienceProfileSchema(many=True).dumps(profile_objs).data

    # @flask_cache.memoize(timeout=50)
    def get_cached_profile_data_resp(self, audience_profile_id):
        current_app.logger.debug("Audience Profile ID received: {0}".format(audience_profile_id))
        audience_profile = self.profile_api.get_profile(id=audience_profile_id)
        current_app.logger.debug("Retrieved fence {0}".format(audience_profile))
        if audience_profile is not None:
            return AudienceProfileSchema(many=True).dumps(audience_profile).data
        err_msg = NameError('Audience Profile ID {0} Not Found.'.format(audience_profile_id))
        return handle_local_rest_error(err_msg, 400)
