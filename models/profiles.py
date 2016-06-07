#Create SQL table that keeps track of weights for each content object added to a pool
from ..extensions import sqldb
from ..extensions import mongodb #Flask Mongoengine API


class ProfileModel(mongodb.Document):
    meta = {
        'allow_inheritance': True
    }   

class UserProfile(ProfileModel):
    user_id=mongodb.StringField()

class DeviceProfile(UserProfile):
    device_id=mongodb.StringField()