
from flask import current_app
from flask_restful import Resource, reqparse
from flask_mongoengine import ValidationError

from apps.geofencing.extensions.cache import flask_cache
from apps.geofencing.rest_api_lib.rest_util import to_json_resp, handle_local_rest_error, check_endpoint_permission_level, \
    authentication_required, query_filter, parse_json_api_data
from apps.geofencing.rest_api_lib.json_api_schemas.audience_profiles.audience_schemas import AudienceProfileSchema
from apps.geofencing.middleware.prometheus.prometheus import Prometheus

API_NAME = 'prometheus'


class AudienceProfileCollection(Resource):

    method_decorators = [authentication_required]

    MIN_LEVEL = 10

    def __init__(self):
        self.prometheus_api = Prometheus()
        self.serializer = AudienceProfileSchema
        super(AudienceProfileCollection, self).__init__()

    def __repr__(self):
        return '<{0}>'.format(self.__class__.__name__)

    def get(self, audience_ref_id=None, permission_level=0, **kwargs):
        try:
            check_endpoint_permission_level(permission_level, self.MIN_LEVEL)
        except ValueError as error:
            return handle_local_rest_error(error, 403)

        if audience_ref_id:
            try:
                return self.resource_query('profile', audience_ref_id=audience_ref_id)
            except Exception as error:
                return handle_local_rest_error(error, API_NAME)

        parser = reqparse.RequestParser()
        parser.add_argument('query', type=str, default='')
        args = parser.parse_args()
        try:
            return self.resource_query(args['query'], **kwargs)
        except Exception as error:
            return handle_local_rest_error(error, API_NAME, 400)

    def patch(self, audience_ref_id=None, permission_level=0, **kwargs):
        try:
            check_endpoint_permission_level(permission_level, self.MIN_LEVEL)
        except ValueError as error:
            return handle_local_rest_error(error, API_NAME, 403)

        if not audience_ref_id:
            error = ValueError("Request parameter 'audience_ref_id' required")
            return handle_local_rest_error(error, API_NAME, 404)

        profile = self.prometheus_api.get_first(ref_id=audience_ref_id)
        if not profile:
            error = ValueError("No Audience Profile with audience_ref_id {0} exists".format(audience_ref_id))
            return handle_local_rest_error(error,API_NAME, 404)

        args = self.patch_args()

        if 'name' in args:
            try:
                self.prometheus_api.update_name(profile, args.get('name'))
            except ValidationError as error:
                return handle_local_rest_error(error, API_NAME, 404)

        if 'avatar' in args:
            try:
                self.prometheus_api.update_avatar(profile, args.get('avatar'))
            except ValidationError as error:
                return handle_local_rest_error(error, API_NAME, 404)

        if 'notes' in args:
            try:
                self.prometheus_api.update_notes(profile, args.get('notes'))
            except ValidationError as error:
                return handle_local_rest_error(error, API_NAME, 404)

        if 'appshare' in args:
            try:
                self.prometheus_api.update_appshare(profile, args.get('appshare'))
            except ValidationError as error:
                return handle_local_rest_error(error, API_NAME, 404)

        if 'appdata' in args:
            try:
                self.prometheus_api.update_appdata(profile, args.get('appdata'))
            except ValidationError as error:
                return handle_local_rest_error(error, API_NAME, 404)

        if 'demographics' in args:
            try:
                self.prometheus_api.update_demographics(profile, args.get('demographics'))
            except ValidationError as error:
                return handle_local_rest_error(error, API_NAME, 404)

        if 'behaviors' in args:
            try:
                self.prometheus_api.update_behaviors(profile, args.get('behaviors'))
            except ValidationError as error:
                return handle_local_rest_error(error, API_NAME, 404)

        return 'success'

    # @flask_cache.memoize(timeout=50)
    def resource_query(self, query, audience_ref_id=None):
        accepted_resource_queries = ('scatter_plot', 'profile')
        if query not in accepted_resource_queries:
            error = ValueError("Invalid - accepted query values ('scatter-plot')")
            return handle_local_rest_error(error, API_NAME, 400)
        if query == 'profile':
            return self.query_profile(audience_ref_id)
        else:
            return getattr(self, 'query_{0}'.format(query))()

    def query_profile(self, audience_ref_id):
        audience_profile = self.prometheus_api.get_first(ref_id=audience_ref_id)
        if audience_profile:
            resp_json = self.serializer().dumps(audience_profile).data
            print resp_json
            return to_json_resp(resp_json, 200)
        error = ValueError('Audience Ref ID {0} Not Found.'.format(audience_ref_id))
        return handle_local_rest_error(error, 400)

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

    def patch_args(self):
        try:
            return parse_json_api_data(self.serializer(), reqparse.RequestParser())
        except TypeError:
            parser = reqparse.RequestParser()
            parser.add_argument('avatar', type=str)
            parser.add_argument('name', type=str)
            parser.add_argument('notes', type=str)
            parser.add_argument('appshare', type=str)
            parser.add_argument('appdata', type=str)
            parser.add_argument('regionshare', type=str)
            parser.add_argument('demographics', type=str)
            parser.add_argument('behaviors', type=str)
            return parser.parse_args()
