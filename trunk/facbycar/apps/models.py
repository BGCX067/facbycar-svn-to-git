# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

import datetime
import random
import re
import sha
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site

class Music(models.Model):
	slug = models.SlugField(max_length=200)
	type = models.CharField(max_length=200)

	def __unicode__(self):
		return u'%s' % (self.type)
		
class ContactsList(models.Model):
	user = models.ForeignKey(User, unique =True, related_name='Utilisateur', null=False)
	contact = models.ForeignKey(User, related_name='User contact', null=False)
	username = models.CharField(max_length=200, null=False)
	
	def __unicode__(self):
		return u'%s %s %s' % (self.user, self. contact, self.username)
		
class UserProfile(models.Model):
	GENDER_CHOICES = (
		('M', 'Male'),
		('F', 'Female'),
	)
	# Django 
	user = models.ForeignKey(User, unique =True)
	slug = models.SlugField(max_length=200)
	sex = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, verbose_name='Sexe')
	
	# We do not need this informations to create an user
	age = models.IntegerField(null=True, blank=True)
	cellphone = models.CharField(max_length=20, null=True, blank=True, verbose_name='Téléphone')
	is_cellphone_hidden = models.BooleanField(verbose_name='Cacher le numéro de téléphone aux autres utilisateurs', default=True)
	is_email_hidden = models.BooleanField(verbose_name='Cacher l\'email aux autres utilisateurs',default=True)
	is_smoker = models.NullBooleanField(null=True, blank=True, verbose_name='Je fume')
	is_talker = models.NullBooleanField(null=True, blank=True, verbose_name='J\'aime parler en voiture')
	url_pic = models.ImageField(upload_to='picts/', null=True, blank=True, verbose_name='Photo', default='picts/default_user.jpg')
	
	type_music = models.ForeignKey(Music, null=True, blank=True, verbose_name='Types de musique écoutés')

	# Internal use only : get rating for user
	note = models.FloatField(editable=False, null=True, blank=True, default=0)
	nb_rating = models.IntegerField(editable=False, null=True, blank=True, default=0)
	
	def __unicode__(self):
		user =  User.objects.get(pk=self.user_id)
		profile = user.get_full_name()
		return profile	

class Comment(models.Model):
	slug = models.SlugField(max_length=200)
	writer = models.ForeignKey(User,related_name='comment_writer')
	recipient = models.ForeignKey(User,related_name='comment_recipient')
	content = models.TextField(verbose_name='Commentaire')
	date = models.DateField()
	note = models.IntegerField()

	def __unicode__(self):
		return u'%s' % (self.id_comment)

class Message(models.Model):
	slug = models.SlugField(max_length=200)
	writer = models.ForeignKey(User,related_name='message_writer', verbose_name='Expéditeur')
	recipient = models.ForeignKey(User,related_name='message_recipient', verbose_name='Destinataire')
	subject = models.CharField(max_length=200, verbose_name='Objet')
	content = models.TextField(verbose_name='Message')
	date = models.DateTimeField()
	is_read = models.BooleanField()
	id_owner = models.IntegerField()

	def __unicode__(self):
		return u'%s' % (self.subject)
		
class Car(models.Model):
	slug = models.SlugField(max_length=200)
	user = models.ForeignKey(User,related_name='car_user')
	model = models.CharField(max_length=200, verbose_name='Modèle')
	url_pic = models.ImageField(upload_to='picts/', null=True, blank=True, verbose_name='URL de l\'image', default='picts/default_car.jpg')
	has_ac = models.BooleanField(verbose_name='Climatisation installée')
	nb_seats = models.IntegerField(verbose_name='Nombre de places')

	def __unicode__(self):
		return self.model

class Route(models.Model):
	slug = models.SlugField(max_length=200)
	user_route = models.ForeignKey(User, related_name='user_owner')
	#user_route_id = models.IntegerField(verbose_name='id user')
	city_d = models.CharField(max_length=255, verbose_name='Ville de départ')
	city_a = models.CharField(max_length=255, verbose_name='Ville d\'arrivée')
	car = models.ForeignKey(Car, verbose_name='Voiture', null=True, blank=True)
	passengers = models.ManyToManyField(User, related_name='user_passenger')
	nb_passengers = models.IntegerField(verbose_name='Nombre de passagers')
	price = models.FloatField(verbose_name='Prix par passager')
	date_departure = models.DateField(verbose_name='Date de départ', blank=True, null=True)
	hour = models.TimeField(verbose_name='Heure de départ', blank=True, null=True)
	is_daily = models.BooleanField(verbose_name='Fréquence')
	is_driver = models.BooleanField(verbose_name='Je suis ')
	place_d = models.CharField(max_length=200, verbose_name='Lieu de départ')
	place_a = models.CharField(max_length=200, verbose_name='Lieu d\'arrivée')
	has_big_boot = models.BooleanField(verbose_name='J\'ai un grand coffre')
	added_date = models.DateField()

	def __unicode__(self):
		return u'%s %s' % (self.city_d, self.city_a)
	
class Round_trip(models.Model):
	slug = models.SlugField(max_length=200)
	route_going = models.OneToOneField(Route,related_name='route_going')
	route_back = models.OneToOneField(Route,related_name='route_back')

	def __unicode__(self):
		return u'%s %s' % (self.id_route_going, self.id_route_back)
		
class Date_daily(models.Model):
	slug = models.SlugField(max_length=200)
	date_mo = models.CharField(max_length=200, verbose_name='Lundi', null=True, blank=True)
	date_tu = models.CharField(max_length=200, verbose_name='Mardi', null=True, blank=True)
	date_we = models.CharField(max_length=200, verbose_name='Mercredi', null=True, blank=True)
	date_th = models.CharField(max_length=200, verbose_name='Jeudi', null=True, blank=True)
	date_fr = models.CharField(max_length=200, verbose_name='Vendredi', null=True, blank=True)
	date_sa = models.CharField(max_length=200, verbose_name='samedi', null=True, blank=True)
	date_su = models.CharField(max_length=200, verbose_name='Dimanche', null=True, blank=True)
	start_time = models.DateField(verbose_name='Date de début de validité')
	end_time = models.DateField(verbose_name='Date de fin de validité')
	route = models.OneToOneField(Route)

	def __unicode__(self):
		return u'%s %s' % (self.start_time, self.end_time)
		



