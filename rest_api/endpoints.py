from resources import audiences

API_NAME = 'ATLAS'


def add_resources_to_prometheus_api(atlas_api):
    """
    All Api.add_resource calls should be added to this function. Since
    we want the resources to be added only after the Api has been initialized
    with the flask app. This function is called right after the init_app call
    on the api in app.py
    :param atlas_api:
    :return:
    """
    atlas_api.add_resource(
        audiences.AudienceCollection,
        '/prometheus/audiences',
        '/prometheus/audiences/<string:audience_id>',
        endpoint='geofences-collection'
    )