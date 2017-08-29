import json
import pytz
from flask_restful import Resource, reqparse
from apps.geofencing.rest_api_lib.rest_util import cors_header, to_json_resp


class TimeZones(Resource):
    """
    This API Resource is responsible for returning the list of timezones available to choose from to allow time of day 
    triggers for geofences and/or associated content.
    """
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('type', type=str, required=False)

    def get(self):
        args = self.reqparse.parse_args()
        
        if args['type'] == 'common':
            timezones = pytz.common_timezones
        else:
            timezones = pytz.all_timezones

        return to_json_resp(json.dumps(timezones), 200, cors_header)  # Not json api compliant!
