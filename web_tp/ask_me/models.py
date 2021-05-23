# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models import F
from django.contrib.auth.models import User
from random import sample


class ProfileMan(models.Manager):
    def random_profiles(self, cnt):
        profile_ids = list(
            Profile.objects.values_list(
                'id', flat=True
            )
        )
        return self.filter(id__in=sample(profile_ids, k=cnt))


class Profile(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    avatar = models.ImageField(default='img/no_ava.jpg', upload_to='avatar/%y/%m/%d')
    objects = ProfileMan()

    def __str__(self):
        try:
            return self.user_id.get_username()
        except:
            return 'noname'

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class MyMan1(models.Manager):
    def on_creation(self, tags):
        tags = self.filter(tag_name__in=tags)
        for t in tags:
            t.tag_rating += 1
            t.save()
        return tags

    def popular_sort(self):
        return self.all().order_by('-tag_rating')[:10]


class Tag(models.Model):
    tag_name = models.CharField(unique=True, max_length=64)
    tag_rating = models.IntegerField(default=0)
    objects = MyMan1()

    def __str__(self):
        return self.tag_name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class MyMan2(models.Manager):
    def by_date(self):
        return self.order_by('-created_on')

    def by_tag(self, tag):
        questions = self.filter(tags__tag_name=tag).order_by('-created_on')
        return questions

    def hot(self):
        return self.order_by('-rating', '-created_on')


class Question(models.Model):
    author = models.ForeignKey('Profile', on_delete=models.CASCADE)
    title = models.CharField(max_length=1024)
    tags = models.ManyToManyField(Tag)
    question_text = models.TextField()
    rating = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    number_of_responses = models.IntegerField(default=0)
    objects = MyMan2()


    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'


class MyMan3(models.Manager):
    def for_question(self, pk):
        return self.filter(question__id=pk).order_by('-rating', 'created_on')


class Answer(models.Model):
    author = models.ForeignKey('Profile', on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    answer_text = models.TextField(default='')
    created_on = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)
    is_correct = models.BooleanField(default=False)
    objects = MyMan3()

    def __str__(self):
        return self.question.title

    def save(self, *args, **kwargs):
        if not self.pk:
            self.question.number_of_responses += 1
            self.question.save()
        super(Answer, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.question.number_of_responses -= 1
        self.question.save()
        super(Answer, self).delete(*args, **kwargs)


class RateQuestion(models.Model):
    author = models.ForeignKey('Profile', on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    rating = models.BooleanField(default=True)

    def __str__(self):
        action = 'dislike'
        if self.rating:
            action = 'like'
        return self.author.user_id.get_username() + ' ' + action + ' \"' + self.question.title + '\"'

    def save(self, *args, **kwargs):
        if not self.pk:
            question = Question.objects.filter(pk=self.question.pk)
            if self.rating:
                question.update(rating=F('rating')+1)
            else:
                question.update(rating=F('rating')-1)
            self.question = Question.objects.filter(pk=question.get().pk).get()
        super(RateQuestion, self).save(*args, **kwargs)
        return self.question.rating

    def delete(self, *args, **kwargs):
        question = Question.objects.filter(pk=self.question.pk)
        if self.rating:
            question.update(rating=F('rating') - 1)
        else:
            question.update(rating=F('rating') + 1)
        self.question = Question.objects.filter(pk=question.get().pk).get()
        super(RateQuestion, self).delete(*args, **kwargs)
        return self.question.rating

    def change(self, *args, **kwargs):
        question = Question.objects.filter(pk=self.question.pk)
        if self.rating:
            self.rating = False
            question.update(rating=F('rating') - 2)
        else:
            self.rating = True
            question.update(rating=F('rating') + 2)
        self.question = Question.objects.filter(pk=question.get().pk).get()
        super(RateQuestion, self).save(*args, **kwargs)
        return self.question.rating

    class Meta:
        unique_together = ('question', 'author')


class RateAnswer(models.Model):
    author = models.ForeignKey('Profile', on_delete=models.CASCADE)
    answer = models.ForeignKey('Answer', on_delete=models.CASCADE)
    rating = models.BooleanField(default=True)

    def __str__(self):
        action = 'dislike'
        if self.rating:
            action = 'like'
        return self.author.user_id.get_username() + ' ' + action + ' answer \"' + str(self.answer.id) + '\"'

    def save(self, *args, **kwargs):
        if not self.pk:
            answer = Answer.objects.filter(pk=self.answer.pk)
            if self.rating:
                answer.update(rating=F('rating')+1)
            else:
                answer.update(rating=F('rating')-1)
            self.answer = Answer.objects.filter(pk=answer.get().pk).get()
        super(RateAnswer, self).save(*args, **kwargs)
        return self.answer.rating

    def delete(self, *args, **kwargs):
        answer = Answer.objects.filter(pk=self.answer.pk)
        if self.rating:
            answer.update(rating=F('rating') - 1)
        else:
            answer.update(rating=F('rating') + 1)
        self.answer = Answer.objects.filter(pk=answer.get().pk).get()
        super(RateAnswer, self).delete(*args, **kwargs)
        return self.answer.rating

    def change(self, *args, **kwargs):
        answer = Answer.objects.filter(pk=self.answer.pk)
        if self.rating:
            self.rating = False
            answer.update(rating=F('rating') - 2)
        else:
            self.rating = True
            answer.update(rating=F('rating') + 2)
        self.answer = Answer.objects.filter(pk=answer.get().pk).get()
        super(RateAnswer, self).save(*args, **kwargs)
        return self.answer.rating

    class Meta:
        unique_together = ('answer', 'author')

# Create your models here.
