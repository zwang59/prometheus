from apps.geofencing.prometheus.rest_api.resources.audiences import AudienceProfileCollection

API_NAME = 'PROMETHEUS'


def add_resources_to_prometheus_api(api):
    """
    All Api.add_resource calls should be added to this function. Since
    we want the resources to be added only after the Api has been initialized
    with the flask app. This function is called right after the init_app call
    on the api in app.py
    :param atlas_api:
    :return:
    """
    api.add_resource(
        AudienceProfileCollection,
        '/prometheus/audiences',
        '/prometheus/audiences/<string:audience_ref_id>',
        endpoint='audiences-collection'
    )
