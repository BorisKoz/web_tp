# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.shortcuts import render, redirect, reverse
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseRedirect

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from ask_me.forms import *
from ask_me.models import *
from django.contrib.auth.models import User


def paginate(objects_list, request, limit=2):
    paginator = Paginator(objects_list, limit)
    page_num = request.GET.get('page')
    if page_num is None:
        page_num = 1
    return paginator.page(page_num)


def index(request):
    questions = Question.objects.by_date()
    paginated = paginate(questions, request, 5)
    most_rating = Tag.objects.popular_sort()
    return render(request, 'index.html', {'content': paginated, 'most_rating': most_rating})

def hot_index(request):
    questions = Question.objects.hot()
    paginated = paginate(questions, request, 5)
    most_rating = Tag.objects.popular_sort()
    return render(request, 'index.html', {'content': paginated, 'most_rating': most_rating})



def one_question(request, pk):
    question = Question.objects.filter(id=pk)
    tags = question.get().tags.all()
    answers = Answer.objects.for_question(pk)
    paginated = paginate(answers, request, 5)
    if request.method == 'GET':
        form = answer_form()
    else:
        if not request.user.is_authenticated:
            return redirect(f"/login/?continue={request.get_full_path()}")
        form = answer_form(data=request.POST, user=request.user, answer_to=question.get())
        if form.is_valid():
            ans = form.save()
            answers = Answer.objects.for_question(pk)
            paginated = paginate(answers, request, 5)
    most_rating = Tag.objects.popular_sort()
    return render(request, 'question.html', {'content': paginated, 'tags': tags, 'question': question.get(), 'most_rating': most_rating, 'form': form})


def one_tag(request, pk):
    tag = Tag.objects.filter(id=pk)
    questions = Question.objects.by_tag(tag.get().tag_name)
    paginated = paginate(questions, request, 5)
    most_rating = Tag.objects.popular_sort()
    return render(request, 'one_tag.html', {'content': paginated, 'tag': tag.get(), 'most_rating': most_rating})

def log_in(request):
    if request.method == 'GET':
        form = login_form()
    else:
        form = login_form(data=request.POST)
        if form.is_valid():
            profile = authenticate(request, **form.cleaned_data)
            if profile is not None:
                login(request, profile)
                return redirect(request.POST.get('continue', '/'))
    most_rating = Tag.objects.popular_sort()
    return render(request, 'login.html', {
        'form': form,
        'most_rating': most_rating,
    })

def log_out(request):
    logout(request)
    previous = request.META.get('HTTP_REFERER')
    if previous is not None:
        return redirect(previous)
    return redirect('login')

def sign_up(request):
    if request.method == 'GET':
        form = register_form()
        avatar = image_form()
    else:
        form = register_form(data=request.POST,  files=request.FILES)
        avatar = image_form(data=request.POST,  files=request.FILES)
        if form.is_valid() and avatar.is_valid():
            profile = form.save()
            avatar = image_form(data=request.POST, files=request.FILES, instance=profile)
            avatar.save()
            login(request, user=profile.user_id)
            return redirect('/')
    most_rating = Tag.objects.popular_sort()
    return render(request, 'signup.html', {
        'form': form,
        'avatar': avatar,
        'most_rating': most_rating,
    })


@login_required
def edit(request):
    if request.method == 'GET':
        form = settings_form(initial={'username': request.user.username, 'email': request.user.email}, user=request.user)
        avatar = image_form()
    else:
        form = settings_form(data=request.POST, files=request.FILES, user=request.user.profile)
        avatar = image_form(data=request.POST, files=request.FILES, instance=request.user.profile)
        if form.is_valid() and avatar.is_valid():
            user = form.save()
            avatar.save()
            login(request, user)
    most_rating = Tag.objects.popular_sort()
    return render(request, 'edit.html', {
        'form': form,
        'avatar': avatar,
        'most_rating': most_rating,
    })


@login_required
def ask(request):
    if request.method == 'GET':
        form = ask_form()
    else:
        form = ask_form(data=request.POST, user=request.user)
        if form.is_valid():
            quest = form.save()
            return redirect('question', quest.pk)
    most_rating = Tag.objects.popular_sort()
    return render(request, 'ask.html', {
        'form': form,
        'most_rating': most_rating,
    })


@require_POST
@login_required
def vote(request):
    data = request.POST
    action = ()
    rating = 0
    content_id = data['id']
    is_like = (data['action'] == 'like')
    if data['type'] == 'question':
        if not RateQuestion.objects.filter(question_id=content_id, author=request.user.profile).exists():
            like = RateQuestion(question_id=content_id, author=request.user.profile, rating=is_like)
            rating = like.save()
        else:
            like = RateQuestion.objects.get(question_id=content_id, author_id=request.user.profile)
            if is_like == like.rating:
                rating = like.delete()
            else:
                rating = like.change()
    elif data['type'] == 'answer':
        if not RateAnswer.objects.filter(answer_id=content_id, author__user_id=request.user).exists():
            like = RateAnswer(answer_id=content_id, author=request.user.profile, rating=is_like)
            rating = like.save()
        else:
            like = RateAnswer.objects.get(answer_id=content_id, author__user_id=request.user)
            if is_like == like.rating:
                rating = like.delete()
            else:
                rating = like.change()
    return JsonResponse({'rating': rating})

@require_POST
@login_required
def is_correct(request):
    data = request.POST
    content_id = data['id']
    answer = Answer.objects.filter(pk=content_id)
    count = Answer.objects.filter(question_id=answer.get().question.id, is_correct=True).count()
    if count == 1 or answer.get().is_correct:
        correct = False
    else:
        correct = True
    answer.update(is_correct=correct)
    return JsonResponse({'action': correct})



