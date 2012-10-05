from pyramid.security import authenticated_userid

class DefaultAuth(object):

    def get_user_id(self, request):
        return authenticated_userid(request)


