# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm
from facbycar.apps.models import *
from django.contrib.auth.models import User
from facbycar.apps.models import *
from django.forms.extras.widgets import *
from django.contrib.admin import widgets 

class RegisterForm(ModelForm):
	class Meta:
		model = User		
		fields = ('username', 'first_name', 'last_name', 'email', 'password')
		
		widgets = {
			'password' : forms.PasswordInput,
		}

class AddCarForm(ModelForm):
	class Meta:
		model = Car
		fields = ('model', 'has_ac', 'nb_seats', 'url_pic')

class DeleteCarForm(forms.Form):
	def __init__(self, *args, **kwargs):
		cur_user = kwargs.pop('cur_user')
		super(DeleteCarForm, self).__init__(*args, **kwargs)
		self.fields['carList'] = forms.ModelChoiceField(label='Voiture', queryset=Car.objects.filter(user__exact=cur_user), widget=forms.Select, required=False)

	carList = forms.CharField(required=False)

class EditProfileForm(ModelForm):
	class Meta:
		model = UserProfile
		fields = ('is_email_hidden',
			'cellphone', 'is_cellphone_hidden',
			'sex', 'age',
			'is_smoker', 'is_talker',
			'type_music', 'url_pic',
			)
		widgets = {
			'type_music' : forms.Select,
		}
	#delete_picture = forms.BooleanField(required=False)

class EditUserForm(ModelForm):
	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'email',)
		
class AddRouteForm(ModelForm):
	def __init__(self, *args, **kwargs):
		cur_user = kwargs.pop('cur_user')
		is_daily = kwargs.pop('is_daily')
		is_driver = kwargs.pop('is_driver')
		super(AddRouteForm, self).__init__(*args, **kwargs)
		self.fields['car'] = forms.ModelChoiceField(label='Voiture', queryset=Car.objects.filter(user__exact=cur_user), widget=forms.Select)
		self.fields['is_daily'] = forms.BooleanField(initial=is_daily, widget=forms.HiddenInput)
		self.fields['is_driver'] = forms.BooleanField(initial=is_driver, widget=forms.HiddenInput)
	class Meta:
		model = Route
		exclude = ('slug', 'added_date', 'passengers')

class AddRoute1Form(ModelForm):
	class Meta:
		CHOICES_LABEL_DRIVER = (
			('1', 'Un conducteur'),
			('0', 'Un passager')
		)
		CHOICES_LABEL_ROUTE = (
			('1', 'Trajet quotidien'),
			('0', 'Trajet ponctuel')
		)
		
		model = Route
		exclude = ('slug', 'car', 'added_date', 'passengers', 'nb_passengers', 'price', 'time', 'has_big_boot', 'date_departure', 'hour')
		widgets = {
			'is_driver' : forms.RadioSelect(choices=CHOICES_LABEL_DRIVER),
			'is_daily' : forms.RadioSelect(choices=CHOICES_LABEL_ROUTE),
		}
		
		
class AddRoute2Form(forms.Form):
		hour = forms.TimeField(label='Heure de départ')

class AddRoute3Form(forms.Form):
	def __init__(self, *args, **kwargs):
		cur_user = kwargs.pop('cur_user')
		super(AddRoute3Form, self).__init__(*args, **kwargs)
		self.fields['car'] = forms.ModelChoiceField(label='Voiture', queryset=Car.objects.filter(user__exact=cur_user), widget=forms.Select)
	car = forms.CharField()
	nb_passengers = forms.IntegerField(label='Nombre de passagers')
	price = forms.FloatField(label='Prix par passager')
	has_big_boot = forms.BooleanField(required=False, label='J\'ai un grand coffre')

class AddRoute3bForm(forms.Form):
	price = forms.FloatField(label='Prix par passager')
	has_big_boot = forms.BooleanField(required=False, label='Il faut un grand coffre')

class BasicSearchForm(ModelForm):
	class Meta:
		model = Route
		exclude = ('slug', 'car', 'date_departure', 'hour', 'has_big_boot', 'passengers', 'nb_passengers', 'price', 'is_daily', 'is_driver', 'place_d', 'place_a', 'added_date')

class RefinedSearchForm(forms.Form):
	price_min = forms.FloatField(required=False, initial=0.0)
	price_max = forms.FloatField()
	city_a = forms.CharField()
	city_d = forms.CharField()
	is_daily = forms.BooleanField(required=False)
	has_big_boot = forms.BooleanField(required=False)
	
class DailyRouteForm(ModelForm):
	class Meta:
		model = Date_daily
		exclude = ('route', 'slug', 'start_time', 'end_time')

class SendMessageForm(ModelForm):
	class Meta:
		model = Message
		fields = ('recipient', 'subject', 'content')

class ContactForm(forms.Form):
	sender = forms.EmailField()
	subject = forms.CharField(max_length=100)
	message = forms.CharField(widget=forms.Textarea(attrs={'cols': 40, 'rows': 5}))
    
class CommForm(ModelForm):
	class Meta:
		CHOICES_LABEL = (
			('0', '0'),
			('1', '1'),
			('2', '2'),
			('3', '3'),
			('4', '4'),
			('5', '5')
		)
		model = Comment		
		fields = ('content', 'note')
		widgets = {
			'content' : forms.Textarea(attrs={'cols': 40, 'rows': 2}),
			'note' : forms.Select(choices=CHOICES_LABEL),
		}
	
