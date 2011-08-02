import types
from service import ROLE_GML, ROLE_CONTENT, ROLE_QA, ROLE_PROGRAMMER

class XmlWriter:
    __guid__ = 'xmlwriter.XmlWriter'
    __defaultaction__ = 'DefaultAction'

    def __init__(self):
        from base import GetServiceSession
        self.session = GetServiceSession('HtmlWriter')
        from base import GetServiceSession
        self.session = GetServiceSession('SPHtmlWriter')
        for each in self.__dependencies__:
            setattr(self, each, self.session.ConnectToAnyService(each))




    def DefaultAction(self):
        pass



    def SetEncoding(self, response, encoding = 'UTF-8'):
        self.response = response
        response.encoding = encoding
        response.contentType = 'text/xml'
        response.Write('<?xml version="1.0" encoding="%s"?>' % encoding)



    def Write(self, str):
        self.response.Write(str)



    def HandleAction(self, action, request, response):
        self.request = request
        self.response = response
        if action is None:
            action = self.__defaultaction__
        if action in self.__exportedactions__:
            if len(self.__exportedactions__[action]) and type(self.__exportedactions__[action][0]) in (types.IntType, types.LongType):
                if self.__exportedactions__[action][0] & session.role == 0:
                    roles = self.session.ConnectToAnyService('cache').Rowset(const.cacheUserRoles)
                    requiredRoles = ''
                    for role in roles:
                        if self.__exportedactions__[action][0] & role.roleID == role.roleID:
                            requiredRoles = requiredRoles + role.roleName + ', '

                    session.LogSessionError("Called %s::%s, which requires of the following roles: %s, which the user doesn't have" % (request.path, action, requiredRoles))
                    raise RoleNotAssignedError(self.__exportedactions__[action][0])
                preargs = self.__exportedactions__[action][1:]
            else:
                preargs = self.__exportedactions__[action]
            params = {}
            for each in preargs:
                if request.QueryString(each) is not None:
                    params[each] = request.QueryString(each)
                elif request.Form(each) is not None:
                    params[each] = request.Form(each)

            try:
                apply(getattr(self, action), (), params)
            except TypeError as e:
                sm.services['http'].LogError('Bad params (', params, ') sent to ', action, ', resulting in exception: ', e)
                raise 
        else:
            self.Write('Action not listed ' + str(action) + '<br>')




