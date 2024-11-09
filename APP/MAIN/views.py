from django.shortcuts import render, redirect
from django.http import FileResponse
from django.views.static import serve
from django.views import View
from django.db.models import Q
from .models import *
from .forms import *
from typing import Dict, List
from .exceptions import *
from django.db import IntegrityError
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.contrib.auth import logout


# response.set_cookie(key = 'test', value = 'test123', max_age= 1200)
# request.session['test'] = 'test1'

class Home(View):

    @method_decorator(cache_page(60*60))
    def get(self, request):

        #Get filters
        filter_app = request.GET.get('app', '')
        filter_group = request.GET.get('group', '')
        filter_pm = request.GET.get('project manager', '')
        filter_developer = request.GET.get('developer', '')
        filter_hashtag = request.GET.get('hashtag', '')

        #Initial context
        context = {'page_name': 'Home',
                   'groups': Group.objects.all(),
                   'hashtags': Hashtag.objects.all(),
                   'developers': Developer.objects.all(),
                   'pms': Pm.objects.all(),
                   'filter_app': filter_app,
                   'filter_group': filter_group,
                   'filter_pm': filter_pm,
                   'filter_developer': filter_developer,
                   'filter_hashtag': filter_hashtag}

        if filter_app:
            apps = Application.objects.filter(app_name__icontains = filter_app)
            context['apps'] = apps
            return render(request, 'Home.html', context = context)


        #Get all apps
        apps = Application.objects.all()

        #Filter apps
        if filter_group:
            apps = apps.filter(group__name = filter_group)

        if filter_developer:
            apps = apps.filter(developers__email = filter_developer)

        if filter_pm:
            apps = apps.filter(pm__email = filter_pm)

        if filter_hashtag:
            apps = apps.filter(hashtags__name = filter_hashtag)

        context['apps'] = apps

        response = render(request, 'Home.html', context = context)

        return response



class App(View):

    def get(self, request, pk: str):

        app = Application.objects.get(id = pk)

        context = {'page_name': app.app_name,
                   'app': app}

        return render(request, 'app.html', context = context)



class Register_App(View):

    UPDATE_APP = False

    def init_context(self) -> Dict[str, object]:
        """
        Build initial context for view

        :return
            context: context for render
        """

        #Get groups
        groups = Group.objects.all()

        #Get types
        types = sorted([i[0] for i in Application.Status.choices])

        #Get pms
        pms = Pm.objects.all()

        #Get developers
        developers = Developer.objects.all()

        #Get hashtags
        hashtags = Hashtag.objects.all()

        context = {'page_name': 'Register',
                   'groups': groups,
                   'types': types,
                   'pms': pms,
                   'developers': developers,
                   'hashtags': hashtags,
                   'input_name': '',
                   'input_group': '',
                   'input_type': 'Desktop',
                   'input_version': '',
                   'input_pm': '',
                   'input_developers': '',
                   'input_hashtags': '',
                   'input_short_desc': '',
                   'input_detail_desc': '',
                   }

        return context



    def get(self, request):
        """
        Get request.
        """

        #Initial context
        context = self.init_context()

        return render(request, 'register_app.html', context = context)


    def post(self, request):
        """
        Post request
        """

        #Initial context
        context = self.init_context()

        #Take user input
        input_name = request.POST.get('name', '')
        input_group = request.POST.get('group', '')
        input_type = request.POST.get('type', '')
        input_version = request.POST.get('version', '')
        input_pm = request.POST.get('project manager', '')
        input_developers = request.POST.getlist('developers', [])
        input_hashtags = request.POST.getlist('hashtags', [])
        input_short_desc = request.POST.get('short_desc', '')
        input_detail_desc = request.POST.get('detail_desc', '')
        input_installer = request.FILES.get('installer', '')
        input_url = request.POST.get('url', '')
        input_user_manual = request.FILES.get('user_manual', '')
        input_presentation = request.FILES.get('presentation', '')
        input_appendix = request.FILES.get('appendix', '')

        #Update context with user inputs
        context['input_name'] = input_name
        context['input_group'] = input_group
        context['input_type'] = input_type
        context['input_version'] = input_version
        context['input_pm'] = input_pm
        context['input_developers'] = input_developers
        context['input_hashtags'] = input_hashtags
        context['input_short_desc'] = input_short_desc
        context['input_detail_desc'] = input_detail_desc

        #Create app instance:
        app = Application(app_name = input_name,
                            author = request.user,
                            group = Group.objects.get(name = input_group),
                            type = input_type,
                            version = input_version,
                            pm = Pm.objects.get(email = input_pm),
                            short_description = input_short_desc,
                            long_description = input_detail_desc,
                            installer = input_installer,
                            user_manual = input_user_manual,
                            presentation = input_presentation,
                            appendix = input_appendix,
                            url = input_url
                            )

        #Check if any error was detected
        error_detected = False

        #Check how many hashtags user has declared
        if len(input_hashtags) > 6:
            error_detected = True
            context['error_hashtags'] = 'Maximum 6 of hashtags can be assigned!'

        #Check if application references (installer/url) was privded
        if input_type == 'Web' and not input_url:
            error_detected = True
            context['error_ref'] = 'Provide web address to application!'

        if input_type == 'Desktop' and not input_installer:
            error_detected = True
            context['error_ref'] = 'Provide application file'

        if error_detected:
            return render(request, 'register_app.html', context = context)


        try:
            #Save app in database
            app.save()

            #Add developers
            for email in input_developers:
                app.developers.add(Developer.objects.get(email=email))

            #Add hashtags
            for hashtag in input_hashtags:
                app.hashtags.add(Hashtag.objects.get(name = hashtag))


            return redirect('home')

        except NotValidInstance as errors:
            for error_key, error_value in dict(errors).items():
                context[f'error_{error_key}'] = error_value[0]

        except IntegrityError:
            # Such application already exist
            context['error_app_name'] = 'Application already exist!'



        return render(request, 'register_app.html', context = context)





class User_Apps(View):
    """
    List all applications for which user is author.
    """

    def get(self, request):

        #Take all applications
        apps = Application.objects.filter(author = request.user)

        context = {'apps': apps}
        return render(request, 'user_apps.html', context = context)

    def post(self, request):
        pass



class Update_App(Register_App):
    """
    Update the application.
    """

    def get(self, request, pk: str):
        """
        Pre-fill 'register-app' page

        :parameter
            pk: the application id
        """

        #Initial context
        context = self.init_context()

        #Get app data
        app = Application.objects.get(id = pk)

        #Update context
        context['app_id'] = app.id
        context['page_name'] = app.app_name
        context['input_name'] = app.app_name
        context['input_type'] = app.type
        context['input_version'] = app.version
        context['input_pm'] = app.pm.email
        context['input_developers'] = app.developers.values_list('email', flat = True) #Take developers as a list of email, instead of list of query set -> app.developers.all()
        context['input_hashtags'] = app.hashtags.values_list('name', flat = True)
        context['input_short_desc'] = app.short_description
        context['input_detail_desc'] = app.long_description

        context['input_installer'] = app.installer.name

        return render(request, 'update_app.html', context = context)


    def post(self, request, pk: str):
        """
        Post request

        :parameter
            pk: application's id
        """

        #Initial context
        context = self.init_context()

        #Take user input
        input_name = request.POST.get('name', '')
        input_group = request.POST.get('group', '')
        input_type = request.POST.get('type', '')
        input_version = request.POST.get('version', '')
        input_pm = request.POST.get('project manager', '')
        input_developers = request.POST.getlist('developers', [])
        input_hashtags = request.POST.getlist('hashtags', [])
        input_short_desc = request.POST.get('short_desc', '')
        input_detail_desc = request.POST.get('detail_desc', '')
        input_installer = request.FILES.get('installer', '')
        input_url = request.POST.get('url', '')

        #Update context with user inputs
        context['input_name'] = input_name
        context['input_group'] = input_group
        context['input_type'] = input_type
        context['input_version'] = input_version
        context['input_pm'] = input_pm
        context['input_developers'] = input_developers
        context['input_hashtags'] = input_hashtags
        context['input_short_desc'] = input_short_desc
        context['input_detail_desc'] = input_detail_desc

        #Get app instance:
        app = Application.objects.get(id = pk)

        #Update app
        app.app_name = input_name
        app.group = Group.objects.get(name = input_group)
        app.type = input_type
        app.version = input_version
        app.pm = Pm.objects.get(email = input_pm)
        app.short_description = input_short_desc
        app.long_description = input_detail_desc


        #Check if any error was detected
        error_detected = False

        #Check how many hashtags user has declared
        if len(input_hashtags) > 6:
            error_detected = True
            context['error_hashtags'] = 'Maximum 6 of hashtags can be assigned!'

        #Check if application references (installer/url) was privded
        if input_type == 'Web' and not input_url:
            error_detected = True
            context['error_ref'] = 'Provide web address to application!'

        if input_type == 'Desktop' and not input_installer:
            error_detected = True
            context['error_ref'] = 'Provide application file'

        if error_detected:
            return render(request, 'update_app.html', context = context)


        try:
            #Save app in database
            app.save()

            #Add developers
            for email in input_developers:
                app.developers.add(Developer.objects.get(email=email))

            #Add hashtags
            for hashtag in input_hashtags:
                app.hashtags.add(Hashtag.objects.get(name=hashtag))

            return redirect('home')

        except NotValidInstance as errors:
            for error_key, error_value in dict(errors).items():
                context[f'error_{error_key}'] = error_value[0]

        except IntegrityError:
            # Such application already exist
            context['error_app_name'] = 'Application already exist!'



        return render(request, 'update_app.html', context = context)