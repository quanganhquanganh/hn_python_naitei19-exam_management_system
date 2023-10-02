from django import template
from django.conf.global_settings import LANGUAGES
from main.models import Test

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
