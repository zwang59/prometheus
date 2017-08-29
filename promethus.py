from apps.geofencing.dbmodels.mongodb.util import load_yaml, rename_yaml_keys,create_embedded_doc_list
from apps.geofencing.dbmodels.mongodb.profiling.audience_profiles import AudienceProfile
from apps.geofencing.dbmodels.mongodb.profiling.behaviours import Individual,Family, Behaviour
from apps.geofencing.dbmodels.mongodb.profiling.demographics import App, Region, Duration, Distance, Frequency, Commute\
                                                                    ,Home, Demographic


class Prometheus(object):
    def __init__(self):
        pass

    def create_commute(self, commutedict, objtype=Commute):
        dur = rename_yaml_keys(commutedict['duration'])
        dur = Duration(description=dur.get('description'), quantity=dur.get('quantity'), units=dur.get('units'))
        freq = rename_yaml_keys(commutedict['frequency'])
        freq = Frequency(quantity=freq.get('quantity'), units=freq.get('units'), grouping=freq.get('grouping'))
        dist = rename_yaml_keys(commutedict['distance'])
        dist = Distance(quantity=dist.get('quantity'), units=dist.get('units'))
        return objtype(origin=commutedict.get('from'), destination=commutedict.get('destination') \
                       , label=commutedict.get('label'), duration=dur, \
                       frequency=freq, distance=dist)

    def create_commutes(self,listofcommutes, objtype=Commute):
        return create_embedded_doc_list(listofcommutes, self.create_commute, objtype)

    def create_behaviours(self, behaviours):
        fam = rename_yaml_keys(behaviours['family'])

        family_list = self.create_commutes(fam['data'], objtype=Family)

        individual = rename_yaml_keys(behaviours['individual'])

        individual_list = self.create_commutes(individual['data'], objtype=Individual)

        return Behaviour(individual=individual_list, family=family_list)

    def create_app_demographic(self, appdata, objtype=App):
        return objtype(description=appdata.get('description'), \
                       percentage=appdata.get('percentage'), \
                       quantity=appdata.get('quantity'), \
                       units=appdata.get('units'))

    def create_app_demographics(self,appdata):
        return create_embedded_doc_list(appdata, self.create_app_demographic, App)

    def create_home_region_demographics(self, homeregiondata):
        return create_embedded_doc_list(homeregiondata, self.create_app_demographic, Region)

    def create_home_commute_demographics(self, homecommutedata):
        return self.create_commutes(homecommutedata)

    def create_demographics(self,demographics):
        app = rename_yaml_keys(demographics['app'])
        appdata = app['data']
        app = self.create_app_demographics(appdata)

        home = rename_yaml_keys(demographics['home'])
        #
        home_region = self.create_home_region_demographics(home['region'][':data'])
        home_commute = self.create_home_commute_demographics(home['commute'][':data'])

        home = Home(region=home_region, commute=home_commute)

        return Demographic(app=app, home=home)

    def profile_from_dict(self,datadict):
        behaviours = self.create_behaviours(rename_yaml_keys(datadict['behaviors']))
        demographics = self.create_demographics(rename_yaml_keys(datadict['demographics']))

        profile = AudienceProfile(avatar=datadict.get('avatar'), \
                                  name=datadict.get('name'), \
                                  notes=datadict.get('notes'), \
                                  demographics=demographics, \
                                  behaviours=behaviours)

        profile.save()
        return profile


