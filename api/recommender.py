#import scipy
#import matplotlib
from random import uniform

from apps.geofencing.dbmodels.sqldb.administration.admin import ApiError
from apps.geofencing.pandora import Pandora
from flask import current_app


class Recommender(object):
    """
    Module containing all of the logic used in recommending content given a content pool and salient input parameters.
    """
    def getRandomContent(self, pools):
        """
        Accepts a LIST of content pool ids and returns a randomly selected content document back.
        """
        if pools:
            current_app.logger.info('Object is associated with content pools')
            #get list of content documents from list of pools
            pandora = Pandora()
            
            try:
                content_list = pandora.getContentDocsByPools(pools)

                if len(content_list) > 0:
                    current_app.logger.info('Content Objects found to be returned')
            
                    #randomly select a content document to return
                    index = int(uniform(0,len(content_list)-1)) #--->right now just returns 1 all the time
                    current_app.logger.info(str(index))
                    
                    content = content_list[index]
                    return content
                else:
                    current_app.logger.warning('Pool has not Content Information')
            except Exception, e:
                #return None
                current_app.logger.info(str(index))
                print len(content_list)
                raise ApiError(self.__class__.__name__, e.message, "404")
        else:
            return None
            raise ApiError(self.__class__.__name__, 'No Content Pool', "404")