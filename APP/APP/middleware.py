from django.http import HttpResponseRedirect
from django.urls import reverse, resolve
from django.shortcuts import redirect

class LoginMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):
        """
        Make sure user is authenticated for create/update app vies.
        """
        if resolve(request.path).url_name in ('register-app', 'update-app', 'user-apps', ) and not request.user.is_authenticated:
            return redirect('/admin/')

        response = self.get_response(request)
        response.set_cookie('login', 'required')

        return response


