from .models import Author
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


class AuthorMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        ...
        """

        #Get user
        username = request.user

        try:
            user_email = User.objects.get(username = username).email
        except ObjectDoesNotExist:
            user_email = ''

        #Get all defined authors
        authors = Author.objects.filter(email = user_email)

        if any(authors):
            request.session['author'] = True
        else:
            request.session['author'] = False

        response = self.get_response(request)

        return response