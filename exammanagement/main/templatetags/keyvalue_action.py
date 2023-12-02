from django import template
from django.conf import settings
from django.conf.global_settings import LANGUAGES
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from main.models import Genre, Notification, Test

register = template.Library()


@register.filter
def keyvalue(dict, key):
    return dict[key]


@register.filter
def in_category(things, category):
    return things.filter(user=category)


@register.filter
def in_contain_more(things, right):
    return things.filter(total_score__gte=right).values()


@register.filter
def in_progress(things, category):
    pass_chapters = 0
    for chapter in things.chapter_set.all():
        if chapter.test_set.filter(
            user=category, total_score__gte=chapter.min_correct_ans
        ).values():
            pass_chapters += 1
    return int((pass_chapters / things.chapter_set.all().count()) * 100)


@register.filter
def in_percent(left, right):
    return 0 if right == 0 else int((left / right) * 100)


@register.filter
def replace_lang(path, lang):
    parts = path.split("/")
    for i, part in enumerate(parts):
        if part in [lang[0] for lang in LANGUAGES]:
            parts[i] = lang
            break
    return "/".join(parts)


@register.filter
def total_correct_cal(thing1, thing2):
    tests = Test.objects.filter(user=thing1.user, chapter__in=thing2.chapter_set.all())
    return sum(test.total_score for test in tests)


@register.filter
def total_times(thing1, thing2):
    tests = Test.objects.filter(user=thing1.user, chapter__in=thing2.chapter_set.all())
    return tests.count()


@register.filter
def correct_ratio(thing1, thing2):
    tests = Test.objects.filter(user=thing1.user, chapter__in=thing2.chapter_set.all())
    total_scores = 0
    total_questions = 0
    for test in tests:
        total_scores += test.total_score
        total_questions += test.chapter.num_questions

    return int((total_scores / total_questions) * 100)


@register.filter
def unread(user):
    return Notification.objects.filter(user=user, is_read=False).order_by("-created_at")


@register.filter
def unread_count(user):
    return Notification.objects.filter(user=user, is_read=False).count()


@register.simple_tag
def genre_options(selected_genre_id=None):
    genres = Genre.objects.all()
    options = []

    for genre in genres:
        selected = "selected" if genre.id == selected_genre_id else ""
        option = f'<option value="{genre.id}" {selected}>{genre.name}</option>'
        options.append(option)

    return mark_safe("\n".join(options))


@register.filter
def make_notification_time(date):
    date = date.astimezone(timezone.get_current_timezone())
    time = timezone.now() - date
    if time.seconds < 5:
        return _("Just now")

    if time.seconds < 60:
        return f"{time.seconds} " + _("seconds ago")

    if time.seconds < 3600:
        return f"{time.seconds // 60} " + _("minutes ago")

    if time.days == 0:
        return f"{time.seconds // 3600} " + _("hours ago")

    if time.days < 30:
        return f"{time.days} " + _("days ago")

    if time.days < 365:
        return f"{time.days // 30} " + _("months ago")

    return f"{time.days // 365} " + _("years ago")


# Modify the original url tag to remove FORCE_SCRIPT_NAME from the url
@register.simple_tag(takes_context=True)
def customurl(context, view_name, *args, **kwargs):
    request = context["request"] if "request" in context else None

    url = (
        request.build_absolute_uri(reverse(view_name, args=args, kwargs=kwargs))
        if request
        else reverse(view_name, args=args, kwargs=kwargs)
    )

    if settings.FORCE_SCRIPT_NAME:
        url = url.replace(settings.FORCE_SCRIPT_NAME, "/")
    return url
