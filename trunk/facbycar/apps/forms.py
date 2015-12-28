# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm
from facbycar.apps.models import *
from django.contrib.auth.models import User
from facbycar.apps.models import *
from django.forms.extras.widgets import *
from django.contrib.admin import widgets 
from django.utils.translation import ugettext_lazy as _

from registration.models import RegistrationProfile
# I put this on all required fields, because it's easier to pick up
# on them with CSS or JavaScript if they have a class of "required"
# in the HTML. Your mileage may vary. If/when Django ticket #3515
# lands in trunk, this will no longer be necessary.
attrs_dict = { 'class': 'required' }

CHOICES_LABEL_HOUR = (
	('00', '00'),
	('01', '01'),
	('02', '02'),
	('03', '03'),
	('04', '04'),
	('05', '05'),
	('06', '06'),
	('07', '07'),
	('08', '08'),
	('09', '09'),
	('10', '10'),
	('11', '11'),
	('12', '12'),
	('13', '13'),
	('14', '14'),
	('15', '15'),
	('16', '16'),
	('17', '17'),
	('18', '18'),
	('19', '19'),
	('20', '20'),
	('21', '21'),
	('22', '22'),
	('23', '23')
)
CHOICES_LABEL_MINUTES = (
	('00', '00'),
	('05', '05'),
	('10', '10'),
	('15', '15'),
	('20', '20'),
	('25', '25'),
	('30', '30'),
	('35', '35'),
	('40', '40'),
	('45', '45'),
	('50', '50'),
	('55', '55')
)
		
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
		
class AddContactToListForm(ModelForm):
	class Meta:
		model = ContactsList
		fields = ('user', 'contact', 'username')
		
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
	
# class EditRouteForm(ModelForm):
	# class Meta:
		# model = Route
		# fields = ('nb_passengers',
			# 'price','city_d', 'hour',
			# 'city_a','place_d',
			# 'place_a',
			# )
		# hour = forms.CharField( widget=forms.Select(choices=CHOICES_LABEL_HOUR))
		# minutes = forms.CharField( widget=forms.Select(choices=CHOICES_LABEL_MINUTES))
		
		# widgets = {
			# 'has_big_boot' : forms.Select,
			# 'hour' : forms.Select(choices=CHOICES_LABEL_HOUR),
			# 'minutes' : forms.Select(choices=CHOICES_LABEL_MINUTES),
		# }

		# car = forms.CharField()
		# has_big_boot = forms.BooleanField(required=False, label='J\'ai un grand coffre')
		
class EditRouteForm(ModelForm):
	class Meta:
		# CHOICES_LABEL_DRIVER = (
			# ('1', 'Un conducteur'),
			# ('0', 'Un passager')
		# )
		# CHOICES_LABEL_ROUTE = (
			# ('1', 'Trajet quotidien'),
			# ('0', 'Trajet ponctuel')
		# )
		
		model = Route
		exclude = ('slug','is_driver','is_daily','user_route' , 'car', 'added_date', 'passengers', 'time', 'has_big_boot', 'date_departure')
		# widgets = {
			# 'is_driver' : forms.RadioSelect(choices=CHOICES_LABEL_DRIVER),
			# 'is_daily' : forms.RadioSelect(choices=CHOICES_LABEL_ROUTE),
		# }
	
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
		exclude = ('slug','user_route' , 'car', 'added_date', 'passengers', 'nb_passengers', 'price', 'time', 'has_big_boot', 'date_departure', 'hour')
		widgets = {
			'is_driver' : forms.RadioSelect(choices=CHOICES_LABEL_DRIVER),
			'is_daily' : forms.RadioSelect(choices=CHOICES_LABEL_ROUTE),
		}
		
		
class AddRoute2Form(forms.Form):	
		#hour = forms.TimeField(label='Heure de départ')		
		hour = forms.CharField( widget=forms.Select(choices=CHOICES_LABEL_HOUR))
		minutes = forms.CharField( widget=forms.Select(choices=CHOICES_LABEL_MINUTES))

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

class AddRoute3cForm(ModelForm):
	class Meta:
		model = Car
		fields = ('model', 'has_ac', 'nb_seats', 'url_pic')
		
	nb_passengers = forms.IntegerField(label='Nombre de passagers')
	price = forms.FloatField(label='Prix par passager')
	has_big_boot = forms.BooleanField(required=False, label='J\'ai un grand coffre')
	
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
	
class DailyRouteForm(forms.Form):
		
	hour_mo = forms.CharField( widget=forms.Select(choices=CHOICES_LABEL_HOUR))
	hour_tu = forms.CharField( widget=forms.Select(choices=CHOICES_LABEL_HOUR))
	hour_we = forms.CharField( widget=forms.Select(choices=CHOICES_LABEL_HOUR))
	hour_th = forms.CharField( widget=forms.Select(choices=CHOICES_LABEL_HOUR))
	hour_fr = forms.CharField( widget=forms.Select(choices=CHOICES_LABEL_HOUR))
	hour_sa = forms.CharField( widget=forms.Select(choices=CHOICES_LABEL_HOUR))
	hour_su = forms.CharField( widget=forms.Select(choices=CHOICES_LABEL_HOUR))
	
	minutes_mo = forms.CharField( widget=forms.Select(choices=CHOICES_LABEL_MINUTES))
	minutes_tu = forms.CharField( widget=forms.Select(choices=CHOICES_LABEL_MINUTES))
	minutes_we = forms.CharField( widget=forms.Select(choices=CHOICES_LABEL_MINUTES))
	minutes_th = forms.CharField( widget=forms.Select(choices=CHOICES_LABEL_MINUTES))
	minutes_fr = forms.CharField( widget=forms.Select(choices=CHOICES_LABEL_MINUTES))
	minutes_sa = forms.CharField( widget=forms.Select(choices=CHOICES_LABEL_MINUTES))
	minutes_su = forms.CharField( widget=forms.Select(choices=CHOICES_LABEL_MINUTES))
	
	start_time = forms.DateField()
	end_time = forms.DateField()
	
	
class SendMessageForm(ModelForm):
	class Meta:
		model = Message
		fields = ('recipient', 'subject', 'content')
		
class ReplyMessageForm(ModelForm):
	class Meta:
		model = Message
		fields = ('recipient','subject', 'content')
	

class ContactForm(forms.Form):
	sender = forms.EmailField()
	subject = forms.CharField(max_length=100)
	message = forms.CharField(widget=forms.Textarea(attrs={'cols': 40, 'rows': 5}))

class ContactsListForm(forms.Form):
	class Meta:
		model = ContactsList
		fields = ('user','contact', 'username')
    
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

class RegistrationForm(forms.Form):
	"""
	Form for registering a new user account.

	Validates that the requested username is not already in use, and
	requires the password to be entered twice to catch typos.

	Subclasses should feel free to add any additional validation they
	need, but should either preserve the base ``save()`` or implement
	a ``save()`` which accepts the ``profile_callback`` keyword
	argument and passes it through to
	``RegistrationProfile.objects.create_inactive_user()``.

	"""
	username = forms.RegexField(regex=r'^\w+$',max_length=30,widget=forms.TextInput(attrs=attrs_dict),label=_(u'Pseudo'))
	# last_name = forms.RegexField(regex=r'^\w+$',max_length=30,widget=forms.TextInput(attrs=attrs_dict),label=_(u'Nom de famille'))
	# first_name = forms.RegexField(regex=r'^\w+$',max_length=30,widget=forms.TextInput(attrs=attrs_dict),label=_(u'Prénom'))
	email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=75)), label=_(u'Adresse email'))
	password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False), label=_(u'mot de passe'))
	password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False), label=_(u'confirmer mot de passe'))
	
	# class Meta:
		# model = User		
		# fields = ('username', 'first_name', 'last_name', 'email', 'password')
		
		# widgets = {
			# 'password' : forms.PasswordInput,
		# }
		
	def clean_email(self):
		"""
		Validate the email
		
		"""
		try:
			user = User.objects.get(email__iexact=self.cleaned_data['email'])
		except User.DoesNotExist:
			return self.cleaned_data['email']
		raise forms.ValidationError(_(u'This email is already taken.'))
		
	def clean_username(self):
		"""
		Validate that the username is alphanumeric and is not already
		in use.
		
		"""
		try:
			user = User.objects.get(username__iexact=self.cleaned_data['username'])
		except User.DoesNotExist:
			return self.cleaned_data['username']
		raise forms.ValidationError(_(u'This username is already taken. Please choose another.'))

	def clean(self):
		"""
		Verifiy that the values entered into the two password fields
		match. Note that an error here will end up in
		``non_field_errors()`` because it doesn't apply to a single
		field.
		
		"""
		if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
			if self.cleaned_data['password1'] != self.cleaned_data['password2']:
				raise forms.ValidationError(_(u'You must type the same password each time'))
		return self.cleaned_data
    
	def save(self, profile_callback=None):
		"""
		Create the new ``User`` and ``RegistrationProfile``, and
		returns the ``User``.
		
		This is essentially a light wrapper around
		``RegistrationProfile.objects.create_inactive_user()``,
		feeding it the form data and a profile callback (see the
		documentation on ``create_inactive_user()`` for details) if
		supplied.
		
		"""

		new_user = RegistrationProfile.objects.create_inactive_user(username=self.cleaned_data['username'],password=self.cleaned_data['password1'],email=self.cleaned_data['email'], profile_callback=profile_callback)

		return new_user
		
class RegistrationFormUniqueEmail(RegistrationForm):
	"""
	Subclass of ``RegistrationForm`` which enforces uniqueness of
	email addresses.

	"""
	def clean_email(self):
		"""
		Validate that the supplied email address is unique for the
		site.
		
		"""
		if User.objects.filter(email__iexact=self.cleaned_data['email']):
			raise forms.ValidationError(_(u'This email address is already in use. Please supply a different email address.'))
		return self.cleaned_data['email']