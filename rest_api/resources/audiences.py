import json, uuid

from flask import current_app
from flask_restful import Resource, reqparse
from mongoengine.errors import NotUniqueError, ValidationError

from geopy.distance import VincentyDistance, Point

from apps.geofencing.middleware.pandora import Pandora
from apps.geofencing.middleware.atlas import Atlas
# from apps.geofencing.middleware.zeus.account import AccountApi
from apps.geofencing.middleware.themis.mobile_app_api.client import Client
from apps.geofencing.middleware.zeus.group import GroupApi
from apps.geofencing.middleware.zeus.campaign import CampaignApi
from apps.geofencing.rest_api_lib.rest_util import to_json_resp, handle_local_rest_error, authentication_required, \
    query_filter, check_endpoint_permission_level, parse_json_api_data
from apps.geofencing.rest_api_lib.json_api_schemas.geo_regions.geofence_schemas import GeofenceResponseSchema
from apps.geofencing.middleware.themis.mobile_device_api.token import Token

API_NAME = 'ATLAS'


class AudienceCollection(Resource):
    """
    Geofence Resource collection

    """

    method_decorators = [authentication_required]

    MIN_LEVEL = 10

    def __init__(self):
        self.atlas = Atlas()
        super(AudienceCollection, self).__init__()

    def __repr__(self):
        return '<{0}>'.format(self.__class__.__name__)

    def get(self, fence_id=None, permission_level=0, **kwargs):
        """
        Read only queries against the Geofence resource collection. The example response below is for a single geofence.
         For queries returning multiple geofences a json encoded array of geofences will be returned.
        All responses will be in json API format.

        .. sourcecode:: http

            GET /atlas/geofences/ HTTP/1.1
            Host: example.com
            Accept: application/vnd.api+json, application/json, text/*

        .. sourcecode:: http

            GET /atlas/geofences/g123/ HTTP/1.1
            Host: example.com
            Accept: application/vnd.api+json, application/json, text/*

        **Example response**:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Vary: Accept
            Content-Type: application/vnd.api+json, application/json, application/x-www-form-urlencoded

            {
              "data": {
                "relationships": {
                  "content": {
                    "data": {
                      "type": "content-message",
                      "id": "57db107c46e6da0c82e15592"
                    },
                    "links": {
                      "related": "/pandora/content-messages/57db107c46e6da0c82e15596"
                    }
                  },
                  "content-pool": {}
                },
                "attributes": {
                  "direction": "entry",
                  "address-components": {
                    "country_abbv": "USA",
                    "street_number": "5534",
                    "locality": "Chicago",
                    "country": "United States",
                    "route": "North Kenmore",
                    "colloquial_area": "Edgewater",
                    "adminArea1": "Illinois",
                    "adminArea2": "Cook",
                    "adminArea3": "Midwest",
                    "postal_code": "60640",
                    "neighbourhood": "Edgewater",
                    "route_abbv": "N Kenmore",
                    "intersection": "Broadway and Kenmore",
                    "sublocality": ""
                  },
                  "center": {
                    "type": "Point",
                    "coordinates": [
                      -77.336733,
                      25.063592
                    ]
                  },
                  dwell: {
                        "device_id": "abc12334",
                        "start": "2016-10-12 13:29:33"
                        "end": "2016-10-12 17:29:33"
                    },
                  "extra": {},
                  "deleted": null,
                  "last-modified-dt": "2016-09-15T16:19:53.556000+00:00",
                  "labels": [],
                  "group-id": 20,
                  "radius": 100,
                  "created-dt": "2016-09-15T16:19:53.556000+00:00",
                  "expiration-dt": null,
                  "dynamic-content": false,
                  "triggers": {
                    "temp_range": [
                      {
                        "temp_end": 35,
                        "temp_start": 0
                      }
                    ],
                    "active_timewindows": [
                      {
                        "start": {
                          "sec": 0,
                          "hour": 0,
                          "min": 30
                        },
                        "end": {
                          "sec": 0,
                          "hour": 23,
                          "min": 30
                        },
                        "tzname": "America/Chicago"
                      }
                    ],
                    "precipitation": {
                      "snow": {
                        "end": 0.99,
                        "st": 0
                      },
                      "rain": {
                        "end": 0.99,
                        "st": 0
                      }
                    }
                  }
                },
                "type": "geofence",
                "id": "57db107c46e6da0c82e15595",
                "links": {
                  "self": "/atlas/geofences/57db107c46e6da0c82e15595"
                }
              }
            }

        :param filter: json encoded string of attributes to filter the collection by. See JSON Parameters below for values.
        :param string query: name of pre-defined query to be executed. See Query Parameters below for values.

        :jsonparam filter-param-float lat: positional latitude coordinate
        :jsonparam filter-param-float lon: positional longitude coordinate
        :jsonparam filter-param-json-string address: json enconded string of address components. See fence schema for more info.
        :jsonparam filter-param-float radius: radial distance in meters
        :jsonparam filter-param-int group-id: group id of geofence group
        :jsonparam filter-param-int tag: geofence tag

        :query geofences-in-radius: returns all geofences within the radial distance from a given {lon, lat}
        :query closest-geofences: returns all geofences within the radial distance from a given {lon, lat}
        :query enclosing-geofences: returns all geofences that are enclosing the position {lon, lat}
        :param double lat: latitude coordinate - used in named queries.
        :param double lon: longitude coordinate - used in named queries.
        :param int radius: distance in meters - used in named queries.

        :reqheader Accept: the response content type depends on
                          :mailheader:`Accept` header
        :reqheader Authorization: optional OAuth token to authenticate. Must be present if not included in request body.
        :resheader Content-Type: this depends on :mailheader:`Accept`
                                header of request
        :statuscode 200: no error
        :statuscode 204: no data
        :statuscode 400: bad request
        :statuscode 403: not authorized
        """
        try:
            check_endpoint_permission_level(permission_level, self.MIN_LEVEL)
        except ValueError as error:
            return handle_local_rest_error(error, API_NAME, 403)

        parser = reqparse.RequestParser()
        parser.add_argument('query', type=str, default='')
        parser.add_argument('filter', type=query_filter, default='')  # Expects a json string (not json api)
        args = parser.parse_args()
        current_app.logger.debug(args)
        if fence_id is None:
            try:
                if args['filter']:
                    return self.execute_resource_query_filter(args['filter'])
                return self.execute_resource_query(args['query'], **kwargs)
            except:
                # Todo: make clause more specific to certain errors
                raise
                # return handle_local_rest_error(api_name=API_NAME)
        try:
            current_app.logger.debug("Fence ID received: {0}".format(fence_id))
            fence = self.atlas.getGeoFence(fence_id)
            current_app.logger.debug("Retrieved fence {0}".format(fence))
            if fence is not None:
                resp_json = GeofenceResponseSchema().dumps(fence).data
                return to_json_resp(resp_json, 200)
            err_msg = NameError('Fence ID {0} Not Found.'.format(id))
            return handle_local_rest_error(err_msg, 400)
        except Exception as error:
            return handle_local_rest_error(error, API_NAME)

    def post(self, permission_level=0, **kwargs):
        """
                Handles the creation of a single geofence resource objects. Below is an example request and response.
                Request data must be formated as a json api resource object or encoded as form data.
                All responses will be in json API format. See http://jsonapi.org/format/#crud for more information.

                .. sourcecode:: http

                    POST /atlas/geofences/ HTTP/1.1
                    Host: example.com
                    Accept: application/vnd.api+json, application/json, text/*

                **Example response**:

                .. sourcecode:: http

                    HTTP/1.1 201 Created
                    Content-Type: application/vnd.api+json, application/json, application/x-www-form-urlencoded

                    {
                      "data": {
                        "relationships": {
                          "content": {
                            "data": {
                              "type": "content-message",
                              "id": "57db107c46e6da0c82e15592"
                            },
                            "links": {
                              "related": "/pandora/content-messages/57db107c46e6da0c82e15596"
                            }
                          },
                          "content-pool": {}
                        },
                        "attributes": {
                          "direction": "entry",
                          "address-components": {
                            "country_abbv": "USA",
                            "street_number": "5534",
                            "locality": "Chicago",
                            "country": "United States",
                            "route": "North Kenmore",
                            "colloquial_area": "Edgewater",
                            "adminArea1": "Illinois",
                            "adminArea2": "Cook",
                            "adminArea3": "Midwest",
                            "postal_code": "60640",
                            "neighbourhood": "Edgewater",
                            "route_abbv": "N Kenmore",
                            "intersection": "Broadway and Kenmore",
                            "sublocality": ""
                          },
                          "center": {
                            "type": "Point",
                            "coordinates": [
                              -77.336733,
                              25.063592
                            ]
                          },
                          dwell: {
                            "device_id": "abc12334",
                            "start": "2016-10-12 13:29:33"
                            "end": "2016-10-12 17:29:33"
                          },
                          "extra": {},
                          "deleted": null,
                          "last-modified-dt": "2016-09-15T16:19:53.556000+00:00",
                          "labels": [],
                          "group-id": 20,
                          "radius": 100,
                          "created-dt": "2016-09-15T16:19:53.556000+00:00",
                          "expiration-dt": null,
                          "dynamic-content": false,
                          "triggers": {
                            "temp_range": [
                              {
                                "temp_end": 35,
                                "temp_start": 0
                              }
                            ],
                            "active_timewindows": [
                              {
                                "start": {
                                  "sec": 0,
                                  "hour": 0,
                                  "min": 30
                                },
                                "end": {
                                  "sec": 0,
                                  "hour": 23,
                                  "min": 30
                                },
                                "tzname": "America/Chicago"
                              }
                            ],
                            "precipitation": {
                              "snow": {
                                "end": 0.99,
                                "st": 0
                              },
                              "rain": {
                                "end": 0.99,
                                "st": 0
                              }
                            }
                          }
                        },
                        "type": "geofence",
                        "id": "57db107c46e6da0c82e15595",
                        "links": {
                          "self": "/atlas/geofences/57db107c46e6da0c82e15595"
                        }
                      }
                    }

                :param double lat: latitude coordinate - mandatory.
                :param double lon: longitude coordinate - mandatory.
                :param int radius: distance in meters.
                :param int group-id: geofence group id.
                :param json-obj address: json encoded string consisting of key value pairs of address components.
                :param string street-number: json encoded string consisting of key value pairs of address components.
                :param string route: route or street name.
                :param string intersection: route or street name.
                :param string neighborhood route: route or street name.
                :param string postal-code: route or street name.
                :param string locality: city or township.
                :param string admin-area-1: county level name
                :param string admin-area-2: state or province
                :param string admin-area-3: region level name
                :param string country: state or province
                :param string token: OAuth token must be provided if not included in request header

                :reqheader Accept: the response content type depends on
                                  :mailheader:`Accept` header
                :reqheader Authorization: optional OAuth token to authenticate. Must be present if not included in request body.
                :resheader Content-Type: this depends on :mailheader:`Accept`
                                        header of request
                :statuscode 201: created
                :statuscode 400: bad request
                :statuscode 403: not authorized
                """
        try:
            check_endpoint_permission_level(permission_level, self.MIN_LEVEL)
        except ValueError as error:
            return handle_local_rest_error(error, API_NAME, 403)

        self.jsonformattag = True
        args = self.get_patch_post_data()  # Parse the request

        # use parameter tag to identify json api
        if self.jsonformattag:
            # handle json api format
            current_app.logger.debug("in json format")
            if 'center' not in args:
                return handle_local_rest_error(ValidationError('Location coordinates required!'), API_NAME, 400)

            if 'address_components' in args:
                loc_dict = dict(args['address_components'])
            else:
                loc_dict = dict()

            group_id = args['group_id']

            # deal with tags and labels
            if 'tags' not in args:
                args['tags'] = None
            if 'labels' not in args:
                args['labels'] = None

            current_app.logger.debug(args)
            try:
                # Determine Fence Type:
                if 'geometry' in args and args['geometry']['type'] == "Polygon":
                    current_app.logger.debug("in polygon")
                    polygon = args['geometry']
                    new_fence = self.atlas.createPolygonalFence(
                        group_id=group_id,
                        polygon=polygon,
                        address=loc_dict,
                        tags=args['tags'],
                        labels=args['labels']
                    )

                # #todo: beacons logic
                # elif 'beacons' in args:
                #     new_fence = self.atlas.createBeaconRegion(group_id, loc_dict)

                else:
                    new_fence = self.atlas.createFence(
                        center=args['center'],
                        group_id=group_id,
                        radius=args['radius'],
                        address=loc_dict,
                        labels=args['labels'],
                        tags=args['tags']
                    )
                # todo: times windows alternative
                # Easy way to set time triggers
                # if 'time_windows' in args:
                #     triggers = dict(time_windows=args['time_windows'])
                #     new_fence.triggers = triggers
                #     new_fence.save()

                resp = GeofenceResponseSchema().dumps(new_fence).data
                return to_json_resp(resp, 201)

            except NotUniqueError as err:
                return handle_local_rest_error(err, API_NAME, 406)
            except ValidationError as err:
                return handle_local_rest_error(err, API_NAME, 406)
            except Exception as err:
                return handle_local_rest_error(err, API_NAME)

        if args['lat'] is None or args['lon'] is None:
            return handle_local_rest_error(ValidationError('Location coordinates required!'), API_NAME, 400)

        loc_dict = dict(
            street_number=args['street_number'],
            route=args['route'],
            route_short=args['route_abbv'],
            intersection=args['intersection'],
            colloquial_area=args['colloquial_area'],
            postal_code=args['postal_code'],
            sublocality=args['sublocality'],
            locality=args['locality'],
            adminArea1=args['adminArea1'],
            adminArea2=args['adminArea2'],
            adminArea3=args['adminArea3'],
            country=args['country'],
            country_abbv=args['country_abbv'],
            neighbourhood=args['neighbourhood']
        )

        group_id = args['group_id']
        try:
            # Determine Fence Type:
            if args['polygon'] is not None:
                polygon = json.loads(args['polygon'])
                new_fence = self.atlas.createPolygonalFence(
                    group_id=group_id,
                    polygon=polygon,
                    address=loc_dict,
                    tags=args['tags'],
                    labels=args['labels']
                )

            elif args['beacons'] is not None:
                new_fence = self.atlas.createBeaconRegion(group_id, loc_dict)

            else:
                center = self.atlas.createGeoPoint(lat=args['lat'], lon=args['lon'])
                new_fence = self.atlas.createFence(
                    center,
                    group_id=group_id,
                    radius=args['radius'],
                    address=loc_dict,
                    labels=args['labels'],
                    tags=args['tags']
                )
            # Easy way to set time triggers
            if args['time_windows'] is not None:
                triggers = dict(time_windows=args['time_windows'])
                new_fence.triggers = triggers
                new_fence.save()

            resp = GeofenceResponseSchema().dumps(new_fence).data
            return to_json_resp(resp, 201)

        except NotUniqueError as err:
            return handle_local_rest_error(err, API_NAME, 406)
        except ValidationError as err:
            return handle_local_rest_error(err, API_NAME, 406)
        except Exception as err:
            return handle_local_rest_error(err, API_NAME)

    def patch(self, fence_id, permission_level=0, **kwargs):
        """
       Handles the updates to existing resources.
       Request data must be formated as a json api resource object or encoded as form data.
       All responses will be in json API format. See http://jsonapi.org/format/#crud for more information.

       .. sourcecode:: http

           PATCH /atlas/geofences/abc123 HTTP/1.1
           Host: example.com
           Accept: application/vnd.api+json, application/json, text/*

       **Example response**:

       .. sourcecode:: http

           HTTP/1.1 200 OK
           Content-Type: application/vnd.api+json, application/json, application/x-www-form-urlencoded

       :param double lat: latitude coordinate.
       :param double lon: longitude coordinate.
       :param int radius: distance in meters.
       :param int group-id: geofence group id.
       :param json-obj address: json encoded string consisting of key value pairs of address components.
       :param string street-number: json encoded string consisting of key value pairs of address components.
       :param string route: route or street name.
       :param string intersection: route or street name.
       :param string neighborhood route: route or street name.
       :param string postal-code: route or street name.
       :param string locality: city or township.
       :param string admin-area-1: county level name
       :param string admin-area-2: state or province
       :param string admin-area-3: region level name
       :param string country: state or province
       :param string token: OAuth token must be provided if not included in request header

       :reqheader Accept: the response content type depends on
                         :mailheader:`Accept` header
       :reqheader Authorization: optional OAuth token to authenticate. Must be present if not included in request body.
       :resheader Content-Type: this depends on :mailheader:`Accept`
                               header of request
       :statuscode 200: OK
       :statuscode 400: bad request
       :statuscode 403: not authorized
       """
        try:
            check_endpoint_permission_level(permission_level, self.MIN_LEVEL)
        except ValueError as error:
            return handle_local_rest_error(error, API_NAME, 403)

        args = self.get_patch_post_data()

        if fence_id is None:
            return {'error': 'Missing ID'}, 400

        pandora = Pandora()
        # mep = MobileRegistration()
        fence = self.atlas.getGeoFence(fence_id)

        if fence is None:
            return {'error': '{0} Not Found'.format(fence_id)}, 400

        if args['time_windows']:
            triggers = dict(time_windows=args['time_windows'], timezone=args['tzname'])
            fence.triggers = triggers
            self.atlas.updateFence(fence)

        if args['direction']:
            try:
                if args['direction'] != '':
                    self.atlas.updateFenceTriggerDirection(fence_id, args['direction'])

            except ValidationError:
                return handle_local_rest_error(ValidationError('{0} is not a valid id'.format(fence_id)), 400)

        if args['radius']:
            try:
                if args['radius'] >= 0:
                    self.atlas.updateFenceRadius(fence, args['radius'])
                    # update devices to resynchronize
            except ValidationError:
                return handle_local_rest_error(ValidationError('{0} is not a valid id'.format(fence_id)), 400)

        if args['content_id']:
            try:
                content = pandora.getContentMessages(content_id=args['content_id']).first()
                self.atlas.updateFenceContent(fence=fence, content=content)
            except Exception as error:
                return handle_local_rest_error(error)

        if args['pool_id']:
            try:
                pools = pandora.getPoolsByIDs(pool_ids=args['pool_id'])
                fence.content_pool = pools
                self.atlas.updateFence(fence)
            except Exception as error:
                return handle_local_rest_error(error)

        # mep.pingDevicesToSynchronize()

        resp = GeofenceResponseSchema().dumps(self.atlas.getGeoFence(fence_id)).data
        return to_json_resp(resp, 200)

    def delete(self, fence_id, permission_level=0, **kwargs):
        """
        Deletes an exisiting geofence.

        .. sourcecode:: http

           DELETE /atlas/geofences/abc123 HTTP/1.1
           Host: example.com
           Accept: application/vnd.api+json, application/json, text/*

        **Example response**:

        .. sourcecode:: http

           HTTP/1.1 204 OK
           Content-Type: application/vnd.api+json, application/json, application/x-www-form-urlencoded

        :param string token: OAuth token must be provided if not included in request header

        :reqheader Accept: the response content type depends on
                         :mailheader:`Accept` header
        :reqheader Authorization: optional OAuth token to authenticate. Must be present if not included in request body.
        :resheader Content-Type: this depends on :mailheader:`Accept`
                               header of request
        :statuscode 400: bad request
        :statuscode 403: not authorized

        """

        try:
            check_endpoint_permission_level(permission_level, self.MIN_LEVEL)
        except ValueError as error:
            return handle_local_rest_error(error, API_NAME, 403)

        try:
            self.atlas.deleteFence(fence_id)
            return to_json_resp('', 204)
        except Exception as error:
            return handle_local_rest_error(error, API_NAME)

    def get_patch_post_data(self):  # Can be static but is specific to the AccountCollections resource
        try:
            return parse_json_api_data(GeofenceResponseSchema(), reqparse.RequestParser())
        except TypeError:  # Content is not json api
            self.jsonformattag = False
            parser = parse_args_post_patch_form_data(reqparse.RequestParser())
            return parser.parse_args()

    def execute_resource_query(self, query, **kwargs):
        if query == '':
            err_msg = NotImplementedError('Invalid - query string is empty!')
            return handle_local_rest_error(err_msg, API_NAME, 400)
        if query == 'geofences-in-radius':
            return self.query_geofences_by_radius()
        if query == 'closest-geofences':
            return self.query_closest_geofences()
        if query == 'enclosing-geofences':
            return self.query_closest_geofences(**kwargs)

    def execute_resource_query_filter(self, filters):
        for k, v in filters.items():
            if k == 'delete_flag':  # Ensure deleted records are hidden
                filters.pop('delete_flag')
        fences = self.atlas.getGeoFences(**filters)
        resp = GeofenceResponseSchema(many=True).dumps(fences).data
        return to_json_resp(resp)

    # Define custom queries for geofences against the resource collection. Each returns a flask response object
    def query_geofences_by_radius(self):
        parser = add_required_location_args(reqparse.RequestParser())
        parser.add_argument('radius', type=float, required=True)
        parser.add_argument('groups', type=int, required=True, append=True, help='Fence GroupApi IDs')
        args = parser.parse_args()
        fences = self.atlas.getFencesWithinSphere(args['groups'], args['lat'], args['lon'], args['radius'])
        resp = GeofenceResponseSchema(many=True).dumps(fences).data
        return to_json_resp(resp, 200)

    def query_closest_geofences(self, **kwargs):
        parser = add_required_location_args(reqparse.RequestParser())
        parser.add_argument('limit', default=19)
        parser.add_argument('radius', type=int, default=1600)  # meters ~mile
        parser.add_argument('device-id', type=str)
        parser.add_argument('client-id', type=str)
        parser.add_argument('token', type=str)
        args = parser.parse_args()

        radius = args['radius']
        limit = args['limit']
        device_id = args['device-id']
        log_msg = ''.join(['Requesting closest geofences at ', str(args['lat']), ',', str(args['lon']),
                           'by', str(device_id)])
        current_app.logger.debug(log_msg)

        account = Token().get_related_account(args['token'])
        current_app.logger.debug('Get Closest Fences Account is {0}'.format(account))
        campaigns = CampaignApi().get_all_join_on_account([account]).all()
        current_app.logger.debug('Campaigns found: {}'.format(campaigns))
        groups = GroupApi().get_all_join_on_campaign(campaigns).all()
        current_app.logger.debug('Groups found: {}'.format(groups))
        group_ids = [x.id for x in groups]
        fences = self.atlas.getClosestFences(args['lat'], args['lon'], group_ids=group_ids, radius=radius, limit=limit) \
            .exclude('triggers', 'created_dt', 'address_components')
        current_app.logger.debug('Fences found: {}'.format(fences.all()))

        if not fences.all():
            # Create a dummy fence to force a reload...
            current_app.logger.debug('No fences present. Creating a reload one...')
            dist_miles = 1
            bearing = 30  # Degrees
            lat2, lon2, alt2 = VincentyDistance(miles=dist_miles).destination(Point(args['lat'], args['lon']), bearing)
            current_app.logger.debug('Calculated Vincenty Distance')
            # Create fake fence at new lat lon and return it...
            p = self.atlas.createGeoPoint(lat=lat2, lon=lon2)
            # Todo: Remove hard-coded group id or don't save
            fence = self.atlas.createFence(p, group_id=99999, save=False, reload=False)
            fence.fence_id = 'reload'
            current_app.logger.debug(fence)
            rv = GeofenceResponseSchema().dumps(fence).data
            current_app.logger.debug('Returning Geofence data ...')
            return to_json_resp(rv, 200)
        else:
            rv = GeofenceResponseSchema(many=True).dumps(fences).data
            return to_json_resp(rv, 200)

    def query_enclosing_geofences(self, lat, lon, account=None, campaign=None, group=None):
        """Checks to see if location is inside a geofence(s) and returns the set if so"""
        atlas = Atlas()
        args = self.parser.parse_args()
        fence = atlas.is_inside_fence(args['lat'], args['lon'])
        if fence:
            return to_json_resp(fence.to_json(), 200)
        return to_json_resp(json.dumps(dict(data=None)), 204)


class GeofenceContentRelationship(Resource):
    """Returns the content message for a specified Geofence"""

    def __init__(self):
        super(GeofenceContentRelationship, self).__init__()

    def get(self, id):
        pass


class GeofenceContentPoolRelationship(Resource):
    """Returns the content pool for a specified Geofence"""

    def __init__(self):
        super(GeofenceContentPoolRelationship, self).__init__()

    def get(self, id):
        pass


def add_required_location_args(parser):
    parser.add_argument('lat', type=float, required=True)
    parser.add_argument('lon', type=float, required=True)
    return parser


def add_address_args(parser):
    parser.add_argument('address', type=address)
    parser.add_argument('street-number', dest='street_number', type=unicode)
    parser.add_argument('route-abbv', dest='route_abbv', type=unicode)
    parser.add_argument('route', type=unicode)
    parser.add_argument('intersection', type=unicode)
    parser.add_argument('neighbourhood', type=unicode)
    parser.add_argument('colloquial_area', dest='colloquial_area', type=unicode)
    parser.add_argument('postal-code', dest='postal_code', type=unicode)
    parser.add_argument('sublocality', type=unicode)
    parser.add_argument('locality', type=unicode)
    parser.add_argument('country', type=unicode)
    parser.add_argument('country_abbv', type=unicode)
    parser.add_argument('admin-area-1', dest='adminArea1', type=unicode)
    parser.add_argument('admin-area-2', dest='adminArea2', type=unicode)
    parser.add_argument('admin-area-3', dest='adminArea3', type=unicode)
    return parser


def parse_args_post_patch_form_data(parser):
    """
    Parsing functions to handle request data sent as form encorded or application/json
    :param parser:
    :return:
    """
    parser.add_argument('lat', type=float, required=False)
    parser.add_argument('lon', type=float, required=False)
    parser.add_argument('direction', type=unicode, required=False)
    parser.add_argument('content-id', dest='content_id', type=str, required=False)
    parser.add_argument('pool-id', dest='pool_id', type=str, action='append', required=False)
    parser.add_argument('act-when[]', type=json.loads, action='append', dest='time_windows')
    parser.add_argument('tags', type=json.loads)
    parser.add_argument('labels', action='append')
    parser.add_argument('group-id', dest='group_id', type=int)
    parser.add_argument('radius', type=float, required=False)
    parser.add_argument('polygon', type=str)
    parser.add_argument('beacons', type=str)
    add_address_args(parser)

    return parser  # Return parser to allow for more arguments to be added


def address(data):
    parsed = query_filter(data)
    # Todo: perform validation on address components:
    return parsed
