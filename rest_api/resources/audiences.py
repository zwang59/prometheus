
from flask import current_app
from flask_restful import Resource, reqparse
from apps.geofencing.extensions.cache import flask_cache
from apps.geofencing.rest_api_lib.rest_util import to_json_resp, handle_local_rest_error, check_endpoint_permission_level, \
    authentication_required, query_filter
from apps.geofencing.rest_api_lib.json_api_schemas.audience_profiles.audience_schemas import AudienceProfileSchema
from apps.geofencing.middleware.prometheus.prometheus import Prometheus
import pprint
API_NAME = 'prometheus'


class AudienceProfileCollection(Resource):

    method_decorators = [authentication_required]

    MIN_LEVEL = 10

    def __init__(self):
        self.prometheus_api = Prometheus()
        super(AudienceProfileCollection, self).__init__()

    def __repr__(self):
        # Needed to ensure an imutable object is cached via the memoize function
        return '<{0}>'.format(self.__class__.__name__)

    def get(self, audience_ref_id=None, permission_level=0, **kwargs):
        try:
            check_endpoint_permission_level(permission_level, self.MIN_LEVEL)
        except ValueError as error:
            return handle_local_rest_error(error, 403)
        parser = reqparse.RequestParser()
        parser.add_argument('query', type=str, default='')
        args = parser.parse_args()
        if not audience_ref_id:
            try:
                return self.resource_query(args['query'], **kwargs)
            except Exception as error:
                return handle_local_rest_error(error, API_NAME, 400)
        try:
            return self.resource_query('profile', audience_ref_id=audience_ref_id)
        except Exception as error:
            return handle_local_rest_error(error, API_NAME)

    def patch(self, audience_ref_id=None, permission_level=0, **kwargs):
        try:
            check_endpoint_permission_level(permission_level, self.MIN_LEVEL)
        except ValueError as error:
            return handle_local_rest_error(error, API_NAME, 403)

        if not audience_ref_id:
            err_msg = ValueError("Request parameter 'audience_ref_id' required")
            return handle_local_rest_error(err_msg, API_NAME, 404)

        profile = self.prometheus_api.get(ref_id=audience_ref_id)
        if profile is None:
            err_msg = ValueError("No Audience Profile with audience_ref_id {0} returned".format(audience_ref_id))
            return handle_local_rest_error(err_msg,API_NAME, 404)


        return 'success'

    # @flask_cache.memoize(timeout=50)
    def resource_query(self, query, audience_ref_id=None):
        accepted_resource_queries = ('scatter-plot', 'profile')
        if query not in accepted_resource_queries:
            err_msg = ValueError("Invalid - accepted query values ('scatter-plot')")
            return handle_local_rest_error(err_msg, API_NAME, 400)
        if query == 'profile':
            return self.query_profile(audience_ref_id)
        if query == 'scatter-plot':
            return self.query_scatter_plot()

    def query_profile(self, audience_ref_id):
        audience_profile = self.prometheus_api.get(ref_id=audience_ref_id)
        if audience_profile is not None:
            resp_json = AudienceProfileSchema(many=True).dumps(audience_profile).data
            return to_json_resp(resp_json, 200)
        err_msg = NameError('Audience Ref ID {0} Not Found.'.format(audience_ref_id))
        return handle_local_rest_error(err_msg, 400)

    def query_scatter_plot(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ref_id', type=int, required=True)
        parser.add_argument('metric', type=str, required=True)
        parser.add_argument('user_action', type=str, required=True)
        parser.add_argument('time_measure', type=str, required=True)
        parser.add_argument('time_window', type=int, required=True)
        args = parser.parse_args()
        if not args:
            err_msg = ValueError("Request query 'scatter-plot' requires parameters ('ref_id' int, 'metric' str, 'user_action' str, \
            'time_measure' str, 'time_window' str")
            return handle_local_rest_error(err_msg, API_NAME, 400)
        profile_geofence_triggers = self.prometheus_api.get_geofence_trigger(args['ref_id'])

        return 'success'
