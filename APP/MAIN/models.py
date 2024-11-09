from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.cache import cache
import re
from APP.settings import BASE_DIR
import os
from .exceptions import *
import uuid

class Developer(models.Model):
    email = models.EmailField(max_length = 100, null = False, unique = True)

    class Meta:
        ordering = ['email']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        #Clear cache
        cache.clear()

class Pm(models.Model):
    email = models.EmailField(max_length = 100, null = False, unique = True)

    class Meta:
        ordering = ['email']
    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        #Clear cache
        cache.clear()


class Hashtag(models.Model):
    name = models.TextField(max_length = 20, null = False, unique = True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        #Clear cache
        cache.clear()



class Group(models.Model):
    name = models.CharField(max_length = 30, null = False, unique = True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        #Clear cache
        cache.clear()



def take_file_extension(filename: str, lower: bool = False) -> str:
    """
    Return file extension

    :parameter
        filename: The name of file from which extension needs to be extracted

        lower: whether convert to lower cases
    :return
        extension

    """

    re_pattern = re.compile(".*[.](.*)\Z")
    match = re_pattern.match(filename)

    #Initial extension
    extension = ''

    if match:
        extension = match.group(1)

    if lower:
        return extension.lower()
    return extension




def presentation_validator(field: models.FileField) -> None:
    """
    Check if presentation has valid format.

    :parameter
        field: Model FileField

    :return
        None
    """

    acceptable_extension = ['pptx', 'pdf', 'docs']
    extension = take_file_extension(filename = field.name, lower = True)

    if extension not in acceptable_extension:
        raise ValidationError(f"Acceptable extensions: {', '.join([e for e in acceptable_extension])}")


def installer_validator(field: models.FileField) -> None:
    """
    Check if presentation has valid format.

    :parameter
        field: Model FileField

    :return
        None
    """

    acceptable_extension = ['exe', 'zip']
    extension = take_file_extension(filename = field.name, lower = True)

    if extension not in acceptable_extension:
        raise ValidationError(f"Acceptable extensions: {', '.join([e for e in acceptable_extension])}")




class UpperCharField(models.CharField):
    """Upper case field"""
    def get_prep_value(self, value):
        return value.upper()




class Application(models.Model):

    class Status(models.TextChoices):
        WEB = 'Web'
        DESKTOP = 'Desktop'

    app_name = UpperCharField(max_length = 20, unique = True)
    author = models.ForeignKey(to = User, null = True, on_delete = models.SET_NULL)
    group = models.ForeignKey(to = Group, null = True, on_delete = models.SET_NULL, blank = True)
    type = models.CharField(max_length = 7, choices = Status.choices, default = Status.DESKTOP, null = False)
    version = models.CharField(max_length = 15, null = True, default = '1.0.0')
    pm = models.ForeignKey(to = Pm, on_delete = models.SET_NULL, null = True)
    developers = models.ManyToManyField(Developer, related_name = 'developers')
    short_description = models.TextField(null = False, max_length = 200, default = '')
    long_description = models.TextField(null = False, max_length =10000, default = '')
    hashtags = models.ManyToManyField(Hashtag, related_name = 'hashtag', blank = True)
    url = models.URLField(null = True)  #For web app. Link to app
    installer = models.FileField(upload_to = 'download/', null = True, validators = [installer_validator], blank = True, unique = False) #For desktop app. Path to app installer
    presentation = models.FileField(upload_to = 'presentation/', null = True, validators = [presentation_validator], blank = True, unique = False)
    user_manual = models.FileField(upload_to = 'user_manual/', null = True, validators = [presentation_validator], blank = True, unique = False)
    appendix = models.FileField(upload_to = 'appendix/', null = True, blank = True, unique = False)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)


    class Meta:
        ordering = ['created']

    def __str__(self):
        return self.app_name

    def save(self, *args, **kwargs):

        #Initial error content
        error_message: dict = {}

        #Check app_name
        if not self.app_name:
            error_message['app_name'] = 'Application name can not be empty!'

        if len(self.app_name) > 20:
            error_message['app_name'] = 'Application name can not exceed 20 characters!'


        #Check short description
        if not self.short_description:
            error_message['short_description'] = 'Short description can not be empty!'

        if self.short_description and len(self.short_description) > 200:
            error_message['short_description'] = 'Short description can not exceed 200 characters!'


        #Check detailed description
        if not self.short_description:
            error_message['detail_description'] = 'Detailed description can not be empty!'

        if self.long_description and len(self.long_description) > 10000:
            error_message['detail_description'] = 'Detailed description can not exceed 3000 characters!'



        if any(error_message):
            raise NotValidInstance(error_message)

        # if self.installer:
        #     # Rename installer
        #     self.installer.name = f"{self.app_name}.{take_file_extension(filename=self.installer.name)}"
        #
        # if self.presentation:
        #     #Rename presentation
        #     self.presentation.name = f"{self.app_name}_PRESENTATION.{take_file_extension(filename = self.presentation.name)}"
        #
        # if self.user_manual:
        #     #Rename user manual
        #     self.user_manual.name = f"{self.app_name}_USER_MANUAL.{take_file_extension(filename = self.user_manual.name)}"
        #
        # if self.appendix:
        #     #Rename user manual
        #     self.appendix.name = f"{self.app_name}_APPENDIX.{take_file_extension(filename = self.appendix.name)}"

        super().save(*args, **kwargs)

        #Clear cache
        cache.clear()





@receiver(signal = pre_save, sender = Application)
def delete_installer(sender: Application, instance: Application, **kwargs):

    #Take pk of app
    try:
        pk = instance.pk
    except sender.DoesNotExist:
        return

    #Get current instance
    try:
        old_instance = Application.objects.get(pk = pk)
    except ObjectDoesNotExist:
        return


    #Check if presentation was changed
    if old_instance.installer.name == instance.installer.name:
        return

    try:
        OLD_INSTALLER_DIR = os.path.join(BASE_DIR, old_instance.installer.path)

        # Remove old presentation
        if os.path.exists(OLD_INSTALLER_DIR):
            os.remove(OLD_INSTALLER_DIR)

    except ValueError:
        pass



@receiver(signal = pre_save, sender = Application)
def delete_presentation(sender: Application, instance: Application, **kwargs):
    """
    Triggered before Application instance save. The method is responsible for:
    - validating new presentation
    - removing old presentation (if exists)
    """

    #Take pk of app
    try:
        pk = instance.pk
    except sender.DoesNotExist:
        return

    #Get current instance
    try:
        old_instance = Application.objects.get(pk = pk)
    except ObjectDoesNotExist:
        return

    #Check if presentation was changed
    if old_instance.presentation.name == instance.presentation.name:
        return

    try:
        OLD_PRES_DIR = os.path.join(BASE_DIR, old_instance.presentation.path)

        # Remove old presentation
        if os.path.exists(OLD_PRES_DIR):
            os.remove(OLD_PRES_DIR)

    except ValueError:
        pass


@receiver(signal = pre_save, sender = Application)
def delete_appendix(sender: Application, instance: Application, **kwargs):
    #Take pk of app
    try:
        pk = instance.pk
    except sender.DoesNotExist:
        return

    #Get current instance
    try:
        old_instance = Application.objects.get(pk = pk)
    except ObjectDoesNotExist:
        return

    #Check if presentation was changed
    if old_instance.appendix.name == instance.appendix.name:
        return

    try:
        OLD_APPENDIX_DIR = os.path.join(BASE_DIR, old_instance.appendix.path)

        # Remove old presentation
        if os.path.exists(OLD_APPENDIX_DIR):
            os.remove(OLD_APPENDIX_DIR)

    except ValueError:
        pass


@receiver(signal = pre_save, sender = Application)
def delete_user_manual(sender: Application, instance: Application, **kwargs):
    #Take pk of app
    try:
        pk = instance.pk
    except sender.DoesNotExist:
        return

    #Get current instance
    try:
        old_instance = Application.objects.get(pk = pk)
    except ObjectDoesNotExist:
        return

    #Check if presentation was changed
    if old_instance.user_manual.name == instance.user_manual.name:
        return

    try:
        OLD_MANUAL_DIR = os.path.join(BASE_DIR, old_instance.user_manual.path)

        # Remove old presentation
        if os.path.exists(OLD_MANUAL_DIR):
            os.remove(OLD_MANUAL_DIR)

    except ValueError:
        pass





class Author(models.Model):
    email = models.EmailField(max_length = 100, null = False, unique = True)

    def __str__(self):
        return self.email