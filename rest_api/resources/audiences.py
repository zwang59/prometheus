
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

    def get(self, audience_profile_id=None, permission_level=0, **kwargs):
        try:
            check_endpoint_permission_level(permission_level, self.MIN_LEVEL)
        except ValueError as error:
            return handle_local_rest_error(error, 403)
        parser = reqparse.RequestParser()
        parser.add_argument('query', type=str, default='')
        # parser.add_argument('filter', type=query_filter, default='')
        args = parser.parse_args()
        if audience_profile_id is None:
            try:
                return self.execute_resource_query(args['query'], **kwargs)
            except Exception as error:
                return handle_local_rest_error(error, API_NAME, 400)
        try:
            return self.get_cached_data_resp(audience_profile_id)
        except Exception as error:
            return handle_local_rest_error(error, API_NAME)

    def post(self, permission_level=0, **kwargs):
        try:
            check_endpoint_permission_level(permission_level, self.MIN_LEVEL)
        except ValueError as error:
            return handle_local_rest_error(error, API_NAME, 403)
        args = self.reqparse.parse_args()
        return 'success', 200

    def patch(self, audience_id=None, permission_level=0, **kwargs):
        try:
            check_endpoint_permission_level(permission_level, self.MIN_LEVEL)
        except ValueError as error:
            return handle_local_rest_error(error, API_NAME, 403)
        if audience_id is None or not self.prometheus_api.get(id=audience_id):
            return handle_local_rest_error(ValueError, API_NAME, 403)
        return 'success', 200

    def delete(self, audience_id=None, permission_level=0, **kwargs):
        try:
            check_endpoint_permission_level(permission_level, self.MIN_LEVEL)
        except ValueError as error:
            return handle_local_rest_error(error, API_NAME, 403)
        return 'success', 200

    # @flask_cache.memoize(timeout=50)
    def get_cached_data_resp(self, audience_profile_id):
        current_app.logger.debug("Audience Profile ID received: {0}".format(audience_profile_id))
        audience_profile = self.prometheus_api.get(id=audience_profile_id)
        current_app.logger.debug("Retrieved fence {0}".format(audience_profile))
        if audience_profile is not None:
            resp_json = AudienceProfileSchema(many=True).dumps(audience_profile).data
            return to_json_resp(resp_json, 200)
        err_msg = NameError('Audience Profile ID {0} Not Found.'.format(audience_profile_id))
        return handle_local_rest_error(err_msg, 400)

    # @flask_cache.memoize(timeout=50)
    def execute_resource_query(self, query, **kwargs):
        accepted_resource_queries = ('scatter-plot',)
        if query not in accepted_resource_queries:
            err_msg = NotImplementedError('Invalid - query string is empty!')
            return handle_local_rest_error(err_msg, API_NAME, 400)
        if query == 'scatter-plot':
            return self.query_scatter_plot()

    def query_scatter_plot(self):
        parser = reqparse.RequestParser()
        parser.add_argument('profile_id', type=int, required=True)
        parser.add_argument('metric', type=str, required=True)
        parser.add_argument('user_action', type=str, required=True)
        parser.add_argument('time_measure', type=str, required=True)
        parser.add_argument('time_window', type=int, required=True)
        args = parser.parse_args()
        return 'success'