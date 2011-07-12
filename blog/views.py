# -*- coding: utf-8 -*-
import datetime

from akismet import Akismet
from django.conf import settings
from django.contrib.comments.models import Comment
from django.contrib.comments.signals import comment_was_posted
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.utils.encoding import smart_str, force_unicode
from django.utils.text import truncate_words
import pingdjack

from blog.forms import CommentForm
from blog.models import Entry, Link, Tag, absolute_uri


def index(request):
    if request.user.is_superuser:
        entries = Entry.objects.all()
    else:
        entries = Entry.live.all()
    links = Link.objects.all()
    return render(request,
                  'blog/index.html',
                  {'entries': entries[:10], 'links': links[:10]})


def archive_entries(request):
    if request.user.is_superuser:
        entries = Entry.objects.all()
    else:
        entries = Entry.live.all()
    return render(request,
                  'blog/archive_entries.html',
                  {'entries': entries,
                   'subtitle': 'Архив статей',
                   'subtitle_url': reverse(archive_entries)})


def archive_links(request):
    return render(request,
                  'blog/archive_links.html',
                  {'links': Link.objects.all(),
                   'subtitle': 'Архив ссылок',
                   'subtitle_url': reverse(archive_links)})


def tag(request, tag):
    tag = get_object_or_404(Tag, slug=tag)
    entries = Entry.objects if request.user.is_superuser else Entry.live
    entries = entries.filter(tags__in=[tag])
    links = Link.objects.filter(tags__in=[tag])
    return render(request,
                  'blog/index.html',
                  {'entries': entries,
                   'links': links,
                   'tag': tag,
                   'subtitle': tag.title,
                   'subtitle_url': reverse('blog.views.tag', args=[tag.slug])})


def _comment_url(request, comment):
    return request.path + '#comment_%s' % comment.id


def entry(request, id, slug):
    entries = Entry.objects if request.user.is_superuser else Entry.live
    try:
        entry = entries.get(id=id)
    except Entry.DoesNotExist:
        return Http404
    form = CommentForm(request)
    if request.method == 'POST':
        form = CommentForm(request, request.POST)
        if form.is_valid():
            comment = form.save_comment_for(entry)
            return HttpResponseRedirect(_comment_url(request, comment))
    return render(request,
                  'blog/entry.html',
                  {'item': entry,
                   'popular_entries': Entry.popular_entries(),
                   'form': form})


def link(request, id):
    link = get_object_or_404(Link, id=id)
    form = CommentForm(request)
    if request.method == 'POST':
        form = CommentForm(request, request.POST)
        if form.is_valid():
            comment = form.save_comment_for(link)
            return HttpResponseRedirect(_comment_url(request, comment))
    return render(request,
                  'blog/link.html',
                  {'item': link,
                   'popular_entries': Entry.popular_entries(),
                   'form': form})


def delete_spam_comment_view(request, comment_id):
    if not request.user.is_superuser:
        raise Http404
    comment = get_object_or_404(Comment, id=comment_id)
    comment_excerpt = truncate_words(comment.comment, 10)

    if request.method == 'POST':
        report_spam_and_delete(comment)
        return HttpResponse(u'Комментарий "%s" удален' % comment_excerpt)

    return render(request,
                  'blog/delete_spam_comment.html',
                  {'comment_excerpt': comment_excerpt})


def comment_posted_callback(sender, **kwargs):
    comment, request = kwargs['comment'], kwargs['request']
    if comment.is_public:
        delete_spam_url = absolute_uri(
            reverse('blog.views.delete_spam_comment_view', args=[comment.id]))
        send_mail(
            u'[vorushin.ru] Комментарий к "%s"' % comment.content_object.title,
            render_to_string('blog/comment_posted.txt',
                             {'comment': comment,
                              'delete_spam_url': delete_spam_url}),
            'roman.vorushin@gmail.com',
            ['roman.vorushin@gmail.com'],
            fail_silently=True)
    request.session['commenter_name'] = comment.user_name
    request.session['commenter_email'] = comment.user_email
    request.session['commenter_url'] = comment.user_url

comment_was_posted.connect(comment_posted_callback)


def _akismet_api():
    api = Akismet(agent='AkismetModerator@vorushin.ru')
    if not api.key:
        api.setAPIKey(settings.AKISMET_KEY, 'http://vorushin2.wordpress.com')
    if not api.verify_key():
        return None
    else:
        return api


def report_spam_and_delete(comment):
    api = _akismet_api()
    if not api:
        return
    api.submit_spam(smart_str(comment.comment),
                    {'user_ip': comment.ip_address, 'user_agent': 'unknown'})
    comment.delete()


def handle_pingback(sender, source_url, view, args, author, excerpt, **kwargs):
    if view == entry:
        item = Entry.objects.get(id=args[0])
    elif view == link:
        item = Link.objects.get(id=args[0])
    else:
        return
    comment = Comment(
            content_type = ContentType.objects.get_for_model(item),
            object_pk    = force_unicode(item.id),
            user_name    = author,
            user_url     = source_url,
            comment      = excerpt,
            submit_date  = datetime.datetime.now(),
            site_id      = settings.SITE_ID,
            is_public    = True,
            is_removed   = False)
    comment.save()

pingdjack.received.connect(handle_pingback)
