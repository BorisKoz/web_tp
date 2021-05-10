from django import forms
from django.forms import ModelForm, TextInput, PasswordInput, DateTimeInput, Textarea, FileInput
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from ask_me.models import *


class login_form(forms.Form):
    username = forms.CharField(required=True, widget=TextInput(attrs={'class': 'form-control'}), label='Login')
    password = forms.CharField(required=True,widget=PasswordInput(attrs={'class': 'form-control'}),label='Password')


class register_form(forms.Form):
    username = forms.CharField(required=True, widget=TextInput(attrs={'class': 'form-control'}), label='Login')

    email = forms.CharField(required=True, widget=TextInput(attrs={'class': 'form-control'}), label='email')

    password = forms.CharField(required=True, widget=TextInput(attrs={'class': 'form-control'}),
                               label='Password')
    password_confirm = forms.CharField(required=True, widget=TextInput(attrs={'class': 'form-control'}),
                                       label='Password confirmation')


    def clean(self):
        if self.cleaned_data['password'] != self.cleaned_data['password_confirm']:
            self.add_error('password', 'passwords dont match')
            raise forms.ValidationError('passwords dont match')
        if Profile.objects.filter(user_id__username=self.cleaned_data['username']).exists():
            self.add_error('username', 'already used')
            raise forms.ValidationError('username already used')
        if Profile.objects.filter(user_id__email=self.cleaned_data['email']).exists():
            self.add_error('email', 'already used')
            raise forms.ValidationError('email already used')


    def save(self):
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        profile = Profile.objects.create(user_id=User.objects.create_user(username, email, password))
        profile.save()
        return profile


class settings_form(forms.Form):
    username = forms.CharField(required=True, widget=TextInput(attrs={'class': 'form-control'}), label='Login')

    email = forms.CharField(required=True, widget=TextInput(attrs={'class': 'form-control'}), label='email')

    password = forms.CharField(required=True, widget=TextInput(attrs={'class': 'form-control'}),
                               label='Password')
    password_confirm = forms.CharField(required=True, widget=TextInput(attrs={'class': 'form-control'}),
                                       label='Password confirmation')

    def __init__(self, user=None, **kwargs):
        self.u = user
        super(settings_form, self).__init__(**kwargs)


    def clean(self):
        if self.cleaned_data['password'] != self.cleaned_data['password_confirm']:
            self.add_error('password', 'passwords dont match')
            raise forms.ValidationError('passwords dont match')
        if Profile.objects.filter(user_id__username=self.cleaned_data['username']).exists():
            if self.cleaned_data['username'] != self.u.username:
                self.add_error('username', 'already used')
                raise forms.ValidationError('username already used')
        if Profile.objects.filter(user_id__email=self.cleaned_data['email']).exists():
            if self.cleaned_data['email'] != self.u.email:
                self.add_error('email', 'already used')
                raise forms.ValidationError('email already used')


    def save(self):
        self.u.username = self.cleaned_data['username']
        self.u.email = self.cleaned_data['email']
        self.u.password = self.cleaned_data['password']
        self.u.save()
        return self.u


class image_form(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']

        labels = {
            'avatar': 'Upload avatar',
        }

class ask_form(forms.Form):
    title = forms.CharField(required=True, widget=TextInput(attrs={'class': 'form-control'}), label='title')
    tags = forms.CharField(required=True, widget=TextInput(attrs={'class': 'form-control'}), label='tags')
    text = forms.CharField(required=True, widget=Textarea(attrs={'class': 'form-control', 'rows': 10}), label='text')

    def __init__(self, user=None, **kwargs):
        self.u = user
        super(ask_form, self).__init__(**kwargs)

    def clean_tags(self):
        self.tags = self.cleaned_data['tags'].split()
        return self.tags

    def save(self, **kwargs):
        question = Question()
        question.author = self.u.profile
        question.title = self.cleaned_data['title']
        question.text = self.cleaned_data['text']
        question.save()

        for tag in self.tags:
            if not Tag.objects.filter(tag_name=tag).exists():
                Tag.objects.create(tag_name=tag)
        question.tags.set(Tag.objects.on_creation(self.tags))

        return question

class answer_form(forms.Form):
    text = forms.CharField(required=True, widget=Textarea(attrs={'class': 'form-control', 'rows': 5, 'cols': 30}), label='text')

    def __init__(self, user=None, answer_to=None, **kwargs):
        self.u = user
        self.a = answer_to
        super(answer_form, self).__init__(**kwargs)

    def save(self):
        answer = Answer()
        answer.author = self.u.profile
        answer.question = self.a
        answer.answer_text = self.cleaned_data['text']
        answer.save()
        return answer