
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
        self.serializer = AudienceProfileSchema()
        super(AudienceProfileCollection, self).__init__()

    def __repr__(self):
        return '<{0}>'.format(self.__class__.__name__)

    def get(self, audience_ref_id=None, permission_level=0, **kwargs):
        """
                Read only queries against the Prfile resource collection. The example response below is for a single profile.
                For queries returning multiple geofences a json encoded array of geofences will be returned.
                All responses will be in json API format.

                .. sourcecode:: http

                    GET /prometheus/audiences/ HTTP/1.1
                    Host: example.com
                    Accept: application/vnd.api+json, application/json, text/*

                .. sourcecode:: http

                    GET /prometheus/audiences/<audience_ref_id>' HTTP/1.1
                    Host: example.com
                    Accept: application/vnd.api+json, application/json, text/*

                **Example response**:

                .. sourcecode:: http

                    HTTP/1.1 200 OK
                    Vary: Accept
                    Content-Type: application/vnd.api+json, application/json, application/x-www-form-urlencoded

                {
                   "data":{
                      "attributes":{
                         "behaviors":[
                            {
                               "data":{
                                  "attributes":{
                                     "origin":"home",
                                     "distance":{
                                        "data":{
                                           "attributes":{
                                              "graph_max":0,
                                              "graph_min":0,
                                              "profile_min":0,
                                              "units":"test",
                                              "profile_max":0,
                                              "quantity":0.0
                                           },
                                           "type":"distance"
                                        }
                                     },
                                     "destination":"work",
                                     "label":"bus",
                                     "frequency":{
                                        "data":{
                                           "attributes":{
                                              "graph_max":0,
                                              "graph_min":0,
                                              "profile_min":0,
                                              "units":"test",
                                              "profile_max":0,
                                              "quantity":0.0
                                           },
                                           "type":"frequency"
                                        }
                                     },
                                     "duration":{
                                        "data":{
                                           "attributes":{
                                              "graph_max":0,
                                              "graph_min":0,
                                              "profile_min":0,
                                              "units":"test",
                                              "profile_max":0,
                                              "quantity":0.0
                                           },
                                           "type":"duration"
                                        }
                                     }
                                  },
                                  "type":"habit"
                               }
                            }
                         ],
                         "name":"test",
                         "appdata":[
                            {
                               "data":{
                                  "attributes":{
                                     "description":"average rating",
                                     "graph_max":0,
                                     "graph_min":0,
                                     "profile_min":0,
                                     "units":"test",
                                     "profile_max":0,
                                     "quantity":0.0
                                  },
                                  "type":"appdata_metric"
                               }
                            }
                         ],
                         "notes":"test",
                         "ref-id":2,
                         "demographics":{
                            "data":{
                               "attributes":{
                                  "agerange":"test",
                                  "familysize":"test",
                                  "incomerange":"test",
                                  "nationalorigin":"test"
                               },
                               "type":"demographics"
                            }
                         },
                         "regionshare":{
                            "data":{
                               "attributes":{
                                  "home":[
                                     {
                                        "data":{
                                           "attributes":{
                                              "units":"urban",
                                              "percentage":0.33333
                                           },
                                           "type":"regionshare_metric"
                                        }
                                     }
                                  ]
                               },
                               "type":"regionshare"
                            }
                         },
                         "appshare":{
                            "data":{
                               "attributes":{
                                  "percentage":0.0,
                                  "total":0
                               },
                               "type":"appshare"
                            }
                         },
                         "geofence-triggers":[]
                         "avatar":"http://test.png"
                      },
                      "type":"audience_profile",
                      "links":{
                         "self":"/prometheus/audiences"
                      }
                   },
                   "links":{
                      "self":"/prometheus/audiences"
                   }
                }

                :param string query: name of pre-defined query to be executed. See Query Parameters below for values.

                :query scatter_plot: returns data specific to the analytics dashboards scatterplot display
                :param string ref_id: profile to return associated data from
                :param string metric:
                :param string user_action:
                :param string time_measure:
                :param string time_window:

                :reqheader Accept: the response content type depends on
                                  :mailheader:`Accept` header
                :reqheader Authorization: OAuth token to authenticate.
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
            return handle_local_rest_error(error, 403)

        if audience_ref_id:
            try:
                return self.query_profile(audience_ref_id)
            except Exception as error:
                return handle_local_rest_error(error, API_NAME)

        parser = reqparse.RequestParser()
        parser.add_argument('query', type=str, default=None)
        args = parser.parse_args()

        if args['query']:
            try:
                return self.resource_query(args['query'])
            except Exception as error:
                return handle_local_rest_error(error, API_NAME, 400)
        else:
            return self.query_all_profile()

    def patch(self, audience_ref_id=None, permission_level=0, **kwargs):
        """
               Handles the updates to existing resources.
               Request data must be formated as a json api resource object.
               All responses will be in json API format. See http://jsonapi.org/format/#crud for more information.

               **Example request**:

               {
                   "data":{
                      "attributes":{
                         "behaviors":[
                            {
                               "data":{
                                  "attributes":{
                                     "origin":"home",
                                     "distance":{
                                        "data":{
                                           "attributes":{
                                              "graph_max":0,
                                              "graph_min":0,
                                              "profile_min":0,
                                              "units":"test",
                                              "profile_max":0,
                                              "quantity":0.0
                                           },
                                           "type":"distance"
                                        }
                                     },
                                     "destination":"work",
                                     "label":"bus",
                                     "frequency":{
                                        "data":{
                                           "attributes":{
                                              "graph_max":0,
                                              "graph_min":0,
                                              "profile_min":0,
                                              "units":"test",
                                              "profile_max":0,
                                              "quantity":0.0
                                           },
                                           "type":"frequency"
                                        }
                                     },
                                     "duration":{
                                        "data":{
                                           "attributes":{
                                              "graph_max":0,
                                              "graph_min":0,
                                              "profile_min":0,
                                              "units":"test",
                                              "profile_max":0,
                                              "quantity":0.0
                                           },
                                           "type":"duration"
                                        }
                                     }
                                  },
                                  "type":"habit"
                               }
                            }
                         ],
                         "name":"test",
                         "appdata":[
                            {
                               "data":{
                                  "attributes":{
                                     "description":"average rating",
                                     "graph_max":0,
                                     "graph_min":0,
                                     "profile_min":0,
                                     "units":"test",
                                     "profile_max":0,
                                     "quantity":0.0
                                  },
                                  "type":"appdata_metric"
                               }
                            }
                         ],
                         "notes":"test",
                         "ref-id":2,
                         "demographics":{
                            "data":{
                               "attributes":{
                                  "agerange":"test",
                                  "familysize":"test",
                                  "incomerange":"test",
                                  "nationalorigin":"test"
                               },
                               "type":"demographics"
                            }
                         },
                         "regionshare":{
                            "data":{
                               "attributes":{
                                  "home":[
                                     {
                                        "data":{
                                           "attributes":{
                                              "units":"urban",
                                              "percentage":0.33333
                                           },
                                           "type":"regionshare_metric"
                                        }
                                     }
                                  ]
                               },
                               "type":"regionshare"
                            }
                         },
                         "appshare":{
                            "data":{
                               "attributes":{
                                  "percentage":0.0,
                                  "total":0
                               },
                               "type":"appshare"
                            }
                         },
                         "geofence-triggers":[]
                         "avatar":"http://test.png"
                      },
                      "type":"audience_profile",
                      "links":{
                         "self":"/prometheus/audiences"
                      }
                   },
                   "links":{
                      "self":"/prometheus/audiences"
                   }
                }

               **Example response**:

               {
                   "data":{
                      "attributes":{
                         "behaviors":[
                            {
                               "data":{
                                  "attributes":{
                                     "origin":"home",
                                     "distance":{
                                        "data":{
                                           "attributes":{
                                              "graph_max":0,
                                              "graph_min":0,
                                              "profile_min":0,
                                              "units":"test",
                                              "profile_max":0,
                                              "quantity":0.0
                                           },
                                           "type":"distance"
                                        }
                                     },
                                     "destination":"work",
                                     "label":"bus",
                                     "frequency":{
                                        "data":{
                                           "attributes":{
                                              "graph_max":0,
                                              "graph_min":0,
                                              "profile_min":0,
                                              "units":"test",
                                              "profile_max":0,
                                              "quantity":0.0
                                           },
                                           "type":"frequency"
                                        }
                                     },
                                     "duration":{
                                        "data":{
                                           "attributes":{
                                              "graph_max":0,
                                              "graph_min":0,
                                              "profile_min":0,
                                              "units":"test",
                                              "profile_max":0,
                                              "quantity":0.0
                                           },
                                           "type":"duration"
                                        }
                                     }
                                  },
                                  "type":"habit"
                               }
                            }
                         ],
                         "name":"test",
                         "appdata":[
                            {
                               "data":{
                                  "attributes":{
                                     "description":"average rating",
                                     "graph_max":0,
                                     "graph_min":0,
                                     "profile_min":0,
                                     "units":"test",
                                     "profile_max":0,
                                     "quantity":0.0
                                  },
                                  "type":"appdata_metric"
                               }
                            }
                         ],
                         "notes":"test",
                         "ref-id":2,
                         "demographics":{
                            "data":{
                               "attributes":{
                                  "agerange":"test",
                                  "familysize":"test",
                                  "incomerange":"test",
                                  "nationalorigin":"test"
                               },
                               "type":"demographics"
                            }
                         },
                         "regionshare":{
                            "data":{
                               "attributes":{
                                  "home":[
                                     {
                                        "data":{
                                           "attributes":{
                                              "units":"urban",
                                              "percentage":0.33333
                                           },
                                           "type":"regionshare_metric"
                                        }
                                     }
                                  ]
                               },
                               "type":"regionshare"
                            }
                         },
                         "appshare":{
                            "data":{
                               "attributes":{
                                  "percentage":0.0,
                                  "total":0
                               },
                               "type":"appshare"
                            }
                         },
                         "geofence-triggers":[]
                         "avatar":"http://test.png"
                      },
                      "type":"audience_profile",
                      "links":{
                         "self":"/prometheus/audiences"
                      }
                   },
                   "links":{
                      "self":"/prometheus/audiences"
                   }
                }

               :reqheader Accept: the response content type depends on
                         :mailheader:`Accept` header
               :reqheader Authorization: required OAuth token to authenticate.
               :resheader Content-Type:
               :statuscode 200: OK
               :statuscode 400: bad request
               :statuscode 403: not authorized

        """

        try:
            check_endpoint_permission_level(permission_level, self.MIN_LEVEL)
        except ValueError as error:
            return handle_local_rest_error(error, API_NAME, 403)

        if not audience_ref_id:
            error = ValueError("Request parameter 'audience_ref_id' required")
            return handle_local_rest_error(error, API_NAME, 404)

        profile = self.prometheus_api.get_first(ref_id=audience_ref_id)

        if not profile:
            error = ValueError("No Audience Profile with audience_ref_id {0} found".format(audience_ref_id))
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

        resp = self.serializer.dumps(profile).data

        return to_json_resp(resp, 200)

    # @flask_cache.memoize(timeout=50)
    def resource_query(self, query):
        accepted_resource_queries = ('scatter_plot', 'profile')
        if query not in accepted_resource_queries:
            error = ValueError("Invalid - accepted query values ('scatter-plot')")
            return handle_local_rest_error(error, API_NAME, 400)
        else:
            return getattr(self, 'query_{0}'.format(query))()

    def query_profile(self, audience_ref_id):
        profile = self.prometheus_api.get_first(ref_id=audience_ref_id)
        if profile:
            resp_json = self.serializer.dumps(profile).data
            return to_json_resp(resp_json, 200)
        error = ValueError('Audience Ref ID {0} Not Found.'.format(audience_ref_id))
        return handle_local_rest_error(error, 400)

    def query_all_profile(self):
        profiles = self.prometheus_api.get_all_collections()
        resp_json = AudienceProfileSchema(many=True).dumps(profiles).data
        return to_json_resp(resp_json)

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

        # profile_geofence_triggers = self.prometheus_api.get_geofence_trigger(args['ref_id'])

        return 'success'

    def patch_args(self):
        try:
            return parse_json_api_data(self.serializer, reqparse.RequestParser())
        except TypeError as error:
            return handle_local_rest_error(error, 400)
