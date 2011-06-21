# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.contrib.comments.forms import COMMENT_MAX_LENGTH
from django.contrib.comments.models import Comment
from django.contrib.comments.signals import comment_was_posted
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from recaptcha.client import captcha

from blog.models import current_site_url


class CommentForm(forms.Form):
    # 4 fields from django.contrib.comments.forms.CommentDetailsForm
    name = forms.CharField(label=_("Name"), max_length=50)
    email = forms.EmailField(label=_("Email address"))
    url = forms.URLField(label=_("URL"), required=False)
    comment = forms.CharField(label=_('Comment'), widget=forms.Textarea,
                              max_length=COMMENT_MAX_LENGTH)

    # recaptcha fields
    recaptcha_challenge_field = forms.CharField(max_length=200, required=False)
    recaptcha_response_field = forms.CharField(max_length=200, required=False)

    def __init__(self, request, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.request = request
        self.ip_address = request.META.get('REMOTE_ADDR')
        self.public_key = settings.RECAPTCHA_PUBLIC_KEY

        if request.user.is_superuser:
            name = '%s %s' % (request.user.first_name, request.user.last_name)
            email = request.user.email
            url = current_site_url()
        elif request.session:
            name = request.session.get('commenter_name', '')
            email = request.session.get('commenter_email', '')
            url = request.session.get('commenter_url', '')
        self.fields['name'].initial = name
        self.fields['email'].initial = email
        self.fields['url'].initial = url

    def clean(self):
        cleaned_data = self.cleaned_data
        captcha_response = captcha.submit(
            cleaned_data.get('recaptcha_challenge_field'),
            cleaned_data.get('recaptcha_response_field'),
            settings.RECAPTCHA_PRIVATE_KEY,
            self.ip_address)
        if not captcha_response.is_valid:
            self._errors['recaptcha_challenge_field'] = self.error_class(
                [u'Неправильная капча'])
        return cleaned_data

    def save_comment_for(self, content_object):
        cleaned_data = self.cleaned_data
        user = self.request.user
        comment = Comment.objects.create(
            user=user if user.is_authenticated() else None,
            user_name=cleaned_data['name'],
            user_email=cleaned_data['email'],
            user_url=cleaned_data['url'],
            comment=cleaned_data['comment'],
            ip_address=self.ip_address,
            content_object=content_object,
            site=Site.objects.get_current())
        comment_was_posted.send(
            sender=self.__class__,
            comment=comment,
            request=self.request)
        return comment

    def is_valid(self):
        try:
            return super(CommentForm, self).is_valid()
        # ValueError("Invalid IPv6 URL"), incorrect URLs in spam comments
        except ValueError:
            return False
