# -*- coding: utf-8 -*-
from facbycar.apps.models import *
from facbycar.apps.forms import *
from facbycar import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.core.mail import send_mail
from string import atof
from copy import deepcopy
from django.db.models import Q
from operator import itemgetter
from operator import attrgetter
#from myapp.models import Entry
from django.utils import simplejson
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings
#from registration.forms import RegistrationForm
from registration.models import RegistrationProfile


def home(request):
	last_routes = Route.objects.order_by('-added_date')[:5]
	
	last_routes2_daily = Route.objects.filter(date_daily__start_time__lt=datetime.now(), date_daily__end_time__gte=datetime.now())[:5]
	nb = last_routes2_daily.count()
	last_routes2 = Route.objects.filter(date_departure__gte=datetime.now()).order_by('date_departure')[:(5-nb)]
	
	
	if request.user.is_authenticated():
		user = User.objects.get(username=request.user)
		profile = user.get_profile()
		return render_to_response('apps/home.html', {'user': user, 'profile': profile, 'last_routes' : last_routes, 'last_routes2' : last_routes2, 'last_routes2_daily' : last_routes2_daily}, context_instance=RequestContext(request))
	else:
		return render_to_response('apps/home.html', {'user': "none", 'last_routes' : last_routes, 'last_routes2' : last_routes2, 'last_routes2_daily' : last_routes2_daily}, context_instance=RequestContext(request))

# def register(request):
	# if request.method == 'POST': # If the form has been submitted...
		# form = RegisterForm(request.POST) # A form bound to the POST data
		# if form.is_valid(): # All validation rules pass
			# u = form.save()
			# u.set_password(form.cleaned_data['password'])
			# u.save()
			# u.profile = UserProfile(user=u)
			# u.profile.save()
			# user = auth.authenticate(username=u.username, password=form.cleaned_data['password'])
			# auth.login(request, user)
			# return HttpResponseRedirect("/edit_profile/")
	# else:
		# form = RegisterForm()

   	# return render_to_response('apps/register.html', {'form': form,}, context_instance=RequestContext(request))

def register(request, success_url=None,form_class=RegistrationForm, profile_callback=None, template_name='registration/registration_form.html', extra_context=None):

	if request.method == 'POST':
		form = form_class(data=request.POST, files=request.FILES)
		if form.is_valid():
			#if user email doesnt exist
			new_user = form.save(profile_callback=profile_callback)
			# if User.objects.filter(email__iexact=request.POST['email']):
				# raise forms.ValidationError(_(u'This email address is already in use. Please supply a different email address.'))
			# else:
				
			# last_name = request.POST['id_last_name']
			# first_name = request.POST['id_first_name']
			# new_user.last_name = last_name
			# new_user.first_name = first_name
			# new_user.save()
			# u = UserProfile()
			# u.user = new_user
			# u.save()
			# success_url needs to be dynamically generated here; setting a
			# a default value using reverse() will cause circular-import
			# problems with the default URLConf for this application, which
			# imports this file.
			return HttpResponseRedirect(success_url or reverse('registration_complete'))
	else:
		form = form_class()

	if extra_context is None:
		extra_context = {}
	context = RequestContext(request)
	for key, value in extra_context.items():
		context[key] = callable(value) and value() or value
	return render_to_response(template_name,{ 'form': form },context_instance=context)
	
def activate(request, activation_key,template_name='registration/activate.html',extra_context=None):
	"""
	Activate a ``User``'s account from an activation key, if their key
	is valid and hasn't expired.

	By default, use the template ``registration/activate.html``; to
	change this, pass the name of a template as the keyword argument
	``template_name``.

	**Required arguments**

	``activation_key``
	The activation key to validate and use for activating the
	``User``.

	**Optional arguments**

	``extra_context``
	A dictionary of variables to add to the template context. Any
	callable object in this dictionary will be called to produce
	the end result which appears in the context.

	``template_name``
	A custom template to use.

	**Context:**

	``account``
	The ``User`` object corresponding to the account, if the
	activation was successful. ``False`` if the activation was not
	successful.

	``expiration_days``
	The number of days for which activation keys stay valid after
	registration.

	Any extra variables supplied in the ``extra_context`` argument
	(see above).

	**Template:**

	registration/activate.html or ``template_name`` keyword argument.

	"""
	activation_key = activation_key.lower() # Normalize before trying anything with it.
	account = RegistrationProfile.objects.activate_user(activation_key)
	
	
	#new profile PROBLEME NON ENREGISTREMENT DU PROFILE
	#recuperer l user id de l'account user.id
	profile = UserProfile();
	profile.user = account
	profile.save()
	
	
	if extra_context is None:
		extra_context = {}
	context = RequestContext(request)
	for key, value in extra_context.items():
		context[key] = callable(value) and value() or value
	return render_to_response(template_name,{ 'account': account,'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS }, context_instance=context)
	
def login(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = auth.authenticate(username=username, password=password)
		if user is not None and user.is_active:
			auth.login(request, user)
			return HttpResponseRedirect("/profile/")
			
	return HttpResponseRedirect("/")

@login_required
def edit_profile(request):
	user = User.objects.get(username=request.user)
	profile = user.get_profile()
	if request.method == 'POST':
		# Populate form with POST datas
		user_form = EditUserForm(request.POST, instance=user)
		profile_form = EditProfileForm(request.POST, request.FILES,  instance=profile)
		if user_form.is_valid() and profile_form.is_valid():
			user_form.save()
			profile_form.save()
			return HttpResponseRedirect("/profile/")
	else:
		user_form = EditUserForm(instance=user)
		profile_form = EditProfileForm(instance=profile)
		return render_to_response('apps/edit_profile.html', {
			'user_form': user_form,
			'profile_form': profile_form,
			'form_action' : "/edit_profile/",
			},
			context_instance=RequestContext(request)
			)
	return HttpResponseRedirect("/profile")
	
@login_required
def profile(request):
	if request.user.is_authenticated():
		user = User.objects.get(username=request.user)
		profile = user.get_profile()
		cars = Car.objects.filter(user=user)
		comments = Comment.objects.filter(recipient__id=user.id)
		messages = Message.objects.filter(recipient__id=user.id, is_read=0, id_owner=user.id)
		
		routes_drivers = Route.objects.filter(is_driver=1, user_route=user.id).order_by('date_departure')[:3]
		routes_passengers = Route.objects.filter(is_driver=0, user_route=user.id).order_by('date_departure')[:3]
		
		return render_to_response('apps/profile.html', {
			'profile' : profile, 
			'user': user, 
			'cars':cars, 
			'messages':messages, 
			'comments':comments, 
			'routes_drivers':routes_drivers, 
			'routes_passengers':routes_passengers
			},context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect("/register/")
	
def user_profile(request):
	if request.method == 'POST':
		user = User.objects.get(id=request.POST['id_user'])
		profile = user.get_profile()
		
		form = CommForm(request.POST) # A form bound to the POST data

		user_user = User.objects.get(id=request.POST['id_user_profil'])
		profile_user = user_user.get_profile()
		cars_user = Car.objects.filter(user=user_user)
		comments_user = Comment.objects.filter(recipient__id=request.POST['id_user_profil'])
		
		routes_drivers = Route.objects.filter(is_driver=1, user_route=user_user.id).order_by('date_departure')[:3]
		routes_passengers = Route.objects.filter(is_driver=0, user_route=user_user.id).order_by('date_departure')[:3]
		

		
		if form.is_valid(): # All validation rules pass
			comm = form.save(commit=False)
			
			comm.writer_id = request.POST['id_user']
			comm.recipient_id = request.POST['id_user_profil']
			comm.content = request.POST['content']
			comm.note = request.POST['note']
			comm.date = datetime.now()#date("Y-m-d") # A CHANGER DANS LA BDD pour avoir l'heure
			comm.save()
			
			date = datetime.now().strftime('%d-%m-%Y')
			
			#Mise à jour de la note dans le profil de l'utilisateur
			profile_user.note = ((atof(profile_user.note) * profile_user.nb_rating) + atof(comm.note)) / (profile_user.nb_rating + 1)
			profile_user.nb_rating += 1
			profile_user.save()
				
			data = { 'content':comm.content , 'note':comm.note, 'username':user.username, 'id_user':user.id, 'date':date, 'new_note':profile_user.note, 'nb_rating':profile_user.nb_rating }
			return HttpResponse(simplejson.dumps(data),mimetype='application/json')
		else:
			form = CommForm()
			
			return render_to_response('apps/user_profile.html', { 
				'profile_user' :profile_user, 
				'user_user': user_user, 
				'cars_user':cars_user, 
				'comments_user':comments_user, 
				'form':form, 
				'routes_drivers':routes_drivers, 
				'routes_passengers':routes_passengers
				},context_instance=RequestContext(request))

	else:
		if request.user.is_authenticated():
			id_u = request.GET.get('u')
		
			user_user = User.objects.get(id=id_u)
			profile_user = user_user.get_profile()
			cars_user = Car.objects.filter(user=user_user)
			comments_user = Comment.objects.filter(recipient__id=user_user.id)
			comments_user.order_by('-id')
			
			routes_drivers = Route.objects.filter(car__in=cars_user, user_route=user_user.id).order_by('date_departure')[:3]
			routes_passengers = Route.objects.exclude(car__in=cars_user).filter(user_route=user_user.id).order_by('date_departure')[:3]
			
			#dans la liste de l'utilisateur courant ou pas ?
			user = User.objects.get(username=request.user)
			contact = ContactsList.objects.filter(user = user, contact = user_user)
			if contact:
				already_contact = 1;
			else:
				already_contact = 0;
		
			form = CommForm()
			
			return render_to_response('apps/user_profile.html', { 
				'profile_user' :profile_user, 
				'user_user': user_user, 
				'cars_user':cars_user, 
				'comments_user':comments_user, 
				'form':form,
				'routes_drivers':routes_drivers, 
				'routes_passengers':routes_passengers,
				'already_contact':already_contact
				},context_instance=RequestContext(request))

		else:
			return HttpResponseRedirect("/login/")

	
@login_required		
def add_car(request):
	user = User.objects.get(username=request.user)
	if request.method == 'POST':
		form = AddCarForm(request.POST, request.FILES)
		if form.is_valid():
			car = form.save(commit=False)
			car.user = user
			if car.url_pic == '':
				car.url_pic = 'picts/default_car.jpg'
			car.save()
			return HttpResponseRedirect('/car/')
	else:
		form = AddCarForm()
		
	return render_to_response('apps/add_car.html', {'form': form,	'form_action': "/add_car/", 'mess': 1}, context_instance=RequestContext(request))

@login_required
def edit_car(request):
	user = User.objects.get(username=request.user)
	if request.method == 'POST':
		form = DeleteCarForm(request.POST, request.FILES, cur_user = user)
		if form.is_valid():
			request.session['temp_data'] = form.cleaned_data['carList']
			return HttpResponseRedirect('/edit_car2/')
	else:
		form = DeleteCarForm(cur_user = user)	

	return render_to_response('apps/form.html', {'form': form, 'form_action': "/edit_car/"}, context_instance=RequestContext(request))

@login_required
def edit_car2(request):
	car = request.session['temp_data']
	if request.method == 'POST':
		form = AddCarForm(request.POST, request.FILES, instance = car)
		if form.is_valid():
			form.save()
			request.session['temp_data'] = ''
			lacar = Car.objects.get(id=car.id)
			if lacar.url_pic == '':
				lacar.url_pic = 'picts/default_car.jpg'
				lacar.save()
			return HttpResponseRedirect("/car/")
	else:
		form = AddCarForm(instance = car)	

	return render_to_response('apps/form.html', {'form': form, 'form_action': "/edit_car2/"}, context_instance=RequestContext(request))

@login_required		
def del_car(request):
	user = User.objects.get(username=request.user)
	if request.method == 'POST':
		form = DeleteCarForm(request.POST, cur_user = user)
		if form.is_valid():
			car = form.cleaned_data['carList']
			Car.objects.filter(id__exact=car.id).delete()
			return HttpResponseRedirect("/profile")
	else:
		form = DeleteCarForm(cur_user = user)
		
	return render_to_response('apps/form.html', {'form': form, 'form_action': "/del_car/"}, context_instance=RequestContext(request))

@login_required	
def car(request):
	user = User.objects.get(username=request.user)
	cars = Car.objects.filter(user=user)
	return render_to_response('apps/cars.html', {'cars': cars,}, context_instance=RequestContext(request))

@login_required
def edit_route(request):
	idm = request.GET.get('id')
	url = "/edit_route/?id="+idm
	route = Route.objects.get(id=idm)
	user = User.objects.get(username=request.user)
	
	if request.method == 'POST':
		# Populate form with POST datas
		route_form = EditRouteForm(request.POST,request.FILES, instance = route)
		if route_form.is_valid():
			route_form.save()
			request.session['temp_data'] = ''
			return HttpResponseRedirect("")
	else:
		route_form = EditRouteForm(instance = route)
		
	return render_to_response('apps/edit_route.html', {
		'route_form': route_form,
		'form_action' : url,
		'date_departure' : route.date_departure,
		'city_d' : route.city_d,
		'city_a' : route.city_a }, context_instance=RequestContext(request))
	#return HttpResponseRedirect("/profile")
	
@login_required
def edit_route1(request):
	if request.user.is_authenticated():
		idm = request.GET.get('id')
		route = Route.objects.get(id=idm)
		#route = request.session['temp_data']
		user = User.objects.get(username=request.user)
		url = "/edit_route1/?id="+idm
		# if route appartient à user
		if request.method == 'POST':
			form = AddRoute1Form(request.POST, request.FILES, instance = route)
			if form.is_valid():
				form.save()
				request.session['temp_data'] = ''
				return HttpResponseRedirect("")
		else:

			#request.session['temp_data'] = route
			form = AddRoute1Form(instance = route)
			
	#return render_to_response('apps/form.html', {'form': form, 'form_action': url}, context_instance=RequestContext(request))
	return render_to_response('apps/add_route1.html', {'form': form, 'form_action': url}, context_instance=RequestContext(request))
	
@login_required
def edit_route2(request):
	form_daily = '0'
	daily = '0'
	if request.user.is_authenticated():
		idm = request.GET.get('id')
		route = Route.objects.get(id=idm)
		#route = request.session['temp_data']
		user = User.objects.get(username=request.user)
		url = "/edit_route2/?id="+idm
		# if route appartient à user
		
		
		if request.method == 'POST':
			form = AddRoute2Form(request.POST)
			route = request.session['temp_data']
			if route.is_daily is True:
				form_daily = DailyRouteForm(request.POST)
				if form_daily.is_valid():
					rd = Date_daily()
					rd.start_time = request.POST['start_time']
					rd.end_time = request.POST['end_time']				
					hour_mo = request.POST['hour_mo']
					hour_tu = request.POST['hour_tu']
					hour_we = request.POST['hour_we']
					hour_th = request.POST['hour_th']
					hour_fr = request.POST['hour_fr']
					hour_sa = request.POST['hour_sa']
					hour_su = request.POST['hour_su']
					
					minutes_mo = request.POST['minutes_mo']
					minutes_tu = request.POST['minutes_tu']
					minutes_we = request.POST['minutes_we']
					minutes_th = request.POST['minutes_th']
					minutes_fr = request.POST['minutes_fr']
					minutes_sa = request.POST['minutes_sa']
					minutes_su = request.POST['minutes_su']
					
					if hour_mo == '00' :
						rd.date_mo = ''
					else :
						rd.date_mo = hour_mo + ":" + minutes_mo
					if hour_tu == '00' :
						rd.date_tu = ''
					else :
						rd.date_tu = hour_tu + ":" + minutes_tu
					if hour_we == '00':
						rd.date_we = ''
					else :
						rd.date_we = hour_we + ":" + minutes_we
					if hour_th == '00':
						rd.date_th = ''
					else :
						rd.date_th = hour_th + ":" + minutes_th
					if hour_fr == '00':
						rd.date_fr = ''
					else :
						rd.date_fr = hour_fr + ":" + minutes_fr
					if hour_sa == '00':
						rd.date_sa = ''
					else :
						rd.date_sa = hour_sa + ":" + minutes_sa
					if hour_su == '00':
						rd.date_su = ''
					else :
						rd.date_su = hour_su + ":" + minutes_su
						
					request.session['temp_daily'] = rd
					
				route.date_departure = request.POST['start_time']
				route.hour = '00:00'
				request.session['temp_data'] = route
				return HttpResponseRedirect('/add_route3/')
			if form.is_valid():
				route.date_departure = request.POST['date']
				hour = form.cleaned_data['hour']
				minutes = form.cleaned_data['minutes']
				route.hour = hour + ":" + minutes
				request.session['temp_data'] = route
				return HttpResponseRedirect('/add_route3/')
		else:

			#request.session['temp_data'] = route
			form = AddRoute2Form(instance = route)
			
	#return render_to_response('apps/form.html', {'form': form, 'form_action': url}, context_instance=RequestContext(request))
	return render_to_response('apps/add_route2.html', {'form': form, 'form_action': url}, context_instance=RequestContext(request))




	
@login_required
def add_route1(request):
	if request.method == 'POST':
		form = AddRoute1Form(request.POST)
		if form.is_valid():
			route = form.save(commit=False)
			request.session['temp_data'] = route
			return HttpResponseRedirect('/add_route2/')
	else:
		form = AddRoute1Form()

	return render_to_response('apps/add_route.html', {'form': form, 'form_action': "/add_route/"}, context_instance=RequestContext(request))

	
@login_required	
def add_route2(request):
	form_daily = '0'
	daily = '0'
	if request.method == 'POST':
		form = AddRoute2Form(request.POST)
		route = request.session['temp_data']
		if route.is_daily is True:
			form_daily = DailyRouteForm(request.POST)
			if form_daily.is_valid():
				rd = Date_daily()
				rd.start_time = request.POST['start_time']
				rd.end_time = request.POST['end_time']				
				hour_mo = request.POST['hour_mo']
				hour_tu = request.POST['hour_tu']
				hour_we = request.POST['hour_we']
				hour_th = request.POST['hour_th']
				hour_fr = request.POST['hour_fr']
				hour_sa = request.POST['hour_sa']
				hour_su = request.POST['hour_su']
				
				minutes_mo = request.POST['minutes_mo']
				minutes_tu = request.POST['minutes_tu']
				minutes_we = request.POST['minutes_we']
				minutes_th = request.POST['minutes_th']
				minutes_fr = request.POST['minutes_fr']
				minutes_sa = request.POST['minutes_sa']
				minutes_su = request.POST['minutes_su']
				
				if hour_mo == '00' :
					rd.date_mo = ''
				else :
					rd.date_mo = hour_mo + ":" + minutes_mo
				if hour_tu == '00' :
					rd.date_tu = ''
				else :
					rd.date_tu = hour_tu + ":" + minutes_tu
				if hour_we == '00':
					rd.date_we = ''
				else :
					rd.date_we = hour_we + ":" + minutes_we
				if hour_th == '00':
					rd.date_th = ''
				else :
					rd.date_th = hour_th + ":" + minutes_th
				if hour_fr == '00':
					rd.date_fr = ''
				else :
					rd.date_fr = hour_fr + ":" + minutes_fr
				if hour_sa == '00':
					rd.date_sa = ''
				else :
					rd.date_sa = hour_sa + ":" + minutes_sa
				if hour_su == '00':
					rd.date_su = ''
				else :
					rd.date_su = hour_su + ":" + minutes_su
					
				request.session['temp_daily'] = rd
				
			route.date_departure = request.POST['start_time']
			route.hour = '00:00'
			request.session['temp_data'] = route
			return HttpResponseRedirect('/add_route3/')
		if form.is_valid():
			route.date_departure = request.POST['date']
			hour = form.cleaned_data['hour']
			minutes = form.cleaned_data['minutes']
			route.hour = hour + ":" + minutes
			request.session['temp_data'] = route
			return HttpResponseRedirect('/add_route3/')
	else:
		form = AddRoute2Form()
		route = request.session['temp_data']
		if route.is_daily is True:
			form_daily = DailyRouteForm()
			daily = '1'
	
	return render_to_response('apps/add_route2.html', {'form': form, 'form_daily': form_daily, 'daily': daily, 'form_action': "/add_route2/"}, context_instance=RequestContext(request))

@login_required	
def add_route3(request):
	route = request.session['temp_data']
	user = User.objects.get(username=request.user)
	cars = Car.objects.filter(user=user)
	if route.is_driver == 1:
		driver = 1
		if request.method == 'POST':
			if cars :
				voiture = 1
				form = AddRoute3Form(request.POST, cur_user=user)			
				if form.is_valid():
					route.user_route = user
					route.car = form.cleaned_data['car']
					route.nb_passengers = form.cleaned_data['nb_passengers']
					route.price = form.cleaned_data['price']
					route.has_big_boot = form.cleaned_data['has_big_boot']
					route.added_date = datetime.now()
					route.is_driver = 1
					route.save()
					#route.passengers.add(user)
					#route.save()
					#request.session['temp_data'] = ''
					if route.is_daily is True:
						daily = request.session['temp_daily']
						daily.route = route;
						daily.save()
						#request.session['temp_daily'] = ''
					else:
						daily = ''
					return render_to_response('apps/summary.html', {'route': route, 'daily':daily}, context_instance=RequestContext(request))
			else :
				form = AddRoute3cForm(request.POST, request.FILES)	
				voiture = 0
				if form.is_valid():
					#enregistrement de la voiture
					car = form.save(commit=False)
					car.model = form.cleaned_data['model']
					car.has_ac = form.cleaned_data['has_ac']
					car.nb_seats = form.cleaned_data['nb_seats']
					car.url_pic = form.cleaned_data['url_pic']
					print car.url_pic 
					car.user = user
					if car.url_pic == '':
						car.url_pic = 'picts/default_car.png'
					car.save()
			
					#enregistrement du reste
					route.user_route = user
					route.car = car
					route.nb_passengers = form.cleaned_data['nb_passengers']
					route.price = form.cleaned_data['price']
					route.has_big_boot = form.cleaned_data['has_big_boot']
					route.added_date = datetime.now()
					route.is_driver = 1
					route.save()
					#route.passengers.add(user)
					#route.save()
					#request.session['temp_data'] = ''
					if route.is_daily is True:
						daily = request.session['temp_daily']
						daily.route = route;
						daily.save()
						#request.session['temp_daily'] = ''
					else:
						daily = ''
					return render_to_response('apps/summary.html', {'route': route, 'daily':daily}, context_instance=RequestContext(request))
		else:
			if cars :
				voiture = 1
				form = AddRoute3Form(cur_user=user)	
			else:
				voiture = 0
				form = AddRoute3cForm()	
	else:
		driver = 0
		voiture = 0
		if request.method == 'POST':
			form = AddRoute3bForm(request.POST)	
			if form.is_valid():
				route.user_route = user
				route.nb_passengers = 1
				route.price = form.cleaned_data['price']
				route.has_big_boot = form.cleaned_data['has_big_boot']
				route.added_date = datetime.now()
				route.is_driver = 0
				route.save()
				#route.passengers.add(user)
				#route.save()
				#request.session['temp_data'] = ''
				if route.is_daily is True:
					daily = request.session['temp_daily']
					daily.route = route;
					daily.save()
					#request.session['temp_daily'] = ''
				else:
					daily = ''
				return render_to_response('apps/summary.html', {'route': route, 'daily':daily}, context_instance=RequestContext(request))
		else:
			form = AddRoute3bForm()	

	return render_to_response('apps/add_route3.html', {'form': form, 'form_action': "/add_route3/", 'driver':driver, 'voiture':voiture}, context_instance=RequestContext(request))


def summary(request):
	return render_to_response('apps/summary.html', context_instance=RequestContext(request))

@login_required	
def my_routes(request):
	cars = Car.objects.filter(user=request.user)
	routes_driver = Route.objects.filter(car__in=cars, user_route=request.user.id).order_by('date_departure')
	routes_passengers = Route.objects.exclude(car__in=cars).filter(user_route=request.user.id).order_by('date_departure')
	#routes_passengers = Route.objects.filter(passengers=request.user, car__isnull=False).order_by('date_departure') #pour le moment pas de gestion des demandes
	return render_to_response('apps/my_routes.html', { 'routes_driver' : routes_driver, 'routes_passengers' : routes_passengers},context_instance=RequestContext(request))
		
@csrf_exempt
def route(request):
	if request.method == 'POST':
		proute = request.POST['id_route']
		puser = request.POST['id_user']

		route = Route.objects.get(id=proute)
		user = User.objects.get(id=puser)
		
		route.passengers.add(user)
		route.save()
		
		data = { 'username':user.username, 'id_route':proute, 'p':1 }
		return HttpResponse(simplejson.dumps(data),mimetype='application/json')
	
	else :
		id_route = request.GET.get('id')
		route = Route.objects.get(id=id_route)
		user_route = User.objects.get(id=route.user_route.id)
		profile = user_route.get_profile()
		
		if request.user.is_authenticated():
			#variable permettant de vérifier si le user est connecté ou non
			auth = 1
			user=request.user
			#permet de savoir si le user paticipe ou non
			participate = Route.objects.filter(passengers=user, id=route.id)		
			if not participate :
				p = 0
			else :
				p = 1
		else :
			auth = 0
			p = 0
		
		if route.is_daily is True:
			daily = Date_daily.objects.get(route=route)
		else:
			daily = ''
	
		
		return render_to_response('apps/route.html', { 'route' : route, 'daily':daily, 'user_route':user_route, 'profile':profile, 'p':p, 'auth':auth},context_instance=RequestContext(request))

		
@login_required	
def my_demands(request):
	routes = Route.objects.filter(passengers=request.user, car__isnull=True).order_by('date_departure')
	return render_to_response('apps/last_routes.html', { 'routes' : routes },context_instance=RequestContext(request))

def search(request):
	return render_to_response('apps/search.html', context_instance=RequestContext(request))

def basic_search(request):
	if request.method == 'POST':
		form = BasicSearchForm(request.POST)
		if form.is_valid():
			route = form.save(commit=False)
			routes = Route.objects.filter(city_d__exact=route.city_d, city_a__exact=route.city_a)
			return render_to_response('apps/last_routes.html', {'routes': routes}, 
			context_instance=RequestContext(request)
			)
	else:
		form = BasicSearchForm()
		
	return render_to_response('apps/basic_search.html', {'form': form, 'form_action': '/basic_search/'}, context_instance=RequestContext(request))

def refined_search(request):
	if request.method == 'POST':
		form = RefinedSearchForm(request.POST)
		if form.is_valid():
			city_a = form.cleaned_data['city_a']
			city_d = form.cleaned_data['city_d']
			date_departure = request.POST['date']
			price_max = form.cleaned_data['price_max']
			price_min = form.cleaned_data['price_min']
			is_daily = form.cleaned_data['is_daily']
			has_big_boot = form.cleaned_data['has_big_boot']
			if has_big_boot:
				routes = Route.objects.filter(
					city_d__exact=city_d,
					city_a__exact=city_a,
					date_departure__exact=date_departure,
					price__lte=price_max,
					price__gte=price_min,
					is_daily__exact=is_daily,
					has_big_boot__exact=has_big_boot
					)
			else:
				routes = Route.objects.filter(
					city_d__exact=city_d,
					city_a__exact=city_a,
					date_departure__exact=date_departure,
					price__lte=price_max,
					price__gte=price_min,
					is_daily__exact=is_daily
					)
			return render_to_response('apps/last_routes.html', {'routes': routes}, 
			context_instance=RequestContext(request)
			)
	else:
		form = RefinedSearchForm()
		
	return render_to_response('apps/refined_search.html', {'form': form, 'form_action': '/refined_search/'}, context_instance=RequestContext(request))
	
def last_routes(request):
	routes_added = Route.objects.order_by('added_date')[:5]
	routes_togo = Route.objects.filter(date_departure__gte=datetime.now()).order_by('date_departure')[:5]
	return render_to_response('apps/last_routes.html', { 'routes_added' : routes_added, 'routes_togo' : routes_togo},context_instance=RequestContext(request))

def ads_time(request):
	now = datetime.now()
	routes_driver = Route.objects.filter(is_driver=False, date_departure__gte=now).order_by('date_departure')[:3]
	routes_passengers = Route.objects.filter(is_driver=True, date_departure__gte=now).order_by('date_departure')[:3]
	return render_to_response('apps/ads.html', { 'routes_driver' : routes_driver, 'routes_passengers' : routes_passengers},context_instance=RequestContext(request))

def ads_price(request):
	now = datetime.now()
	routes_driver = Route.objects.filter(is_driver=False, date_departure__gte=now).order_by('price')[:3]
	routes_passengers = Route.objects.filter(is_driver=True, date_departure__gte=now).order_by('price')[:3]
	return render_to_response('apps/ads.html', { 'routes_driver' : routes_driver, 'routes_passengers' : routes_passengers},context_instance=RequestContext(request))

@login_required
def send_message(request):
	if request.user.is_authenticated():
		if request.method == 'POST': # If the form has been submitted...
			user = User.objects.get(username=request.user)
			form = SendMessageForm(request.POST) # A form bound to the POST data
			if form.is_valid(): # All validation rules pass
				#Create 2 new messages in table message
				sended = Message()
				#recipient = User.objects.get(username=request.POST['recipient'])
				
				sended.writer_id = user.id
				sended.recipient_id = request.POST['recipient']#recipient.id
				sended.subject = request.POST['subject']
				sended.content = request.POST['content']
				sended.date = datetime.now()#date("Y-m-d") # A CHANGER DANS LA BDD pour avoir l'heure
				sended.is_read = False
				sended.id_owner = sended.writer_id

				recieped = deepcopy(sended)
				#recieped = sended
				recieped.id_owner = request.POST['recipient']#recipient.id
	
				sended.is_read = 1
				recieped.save()
				sended.save()
				
				user2 = User.objects.get(id=sended.recipient_id)
				send_mail('Nouveau message FacByCar', 'Vous avez reçu un nouveau message. Pour le consulter: http://facbycar.alwaysdata.com', 'no-reply@facbycar.com',[user2.email], fail_silently=False)

				# subject = sended.subject
				# message = "FacByCar: Vous avez reçu un nouveau message ! (http://@adresse du site)"
				# recipient = User.objects.get(id=sended.recipient_id)
				# recipient_adress = recipient.email
				# sender = User.objects.get(id=sended.writer_id)
				# sender = sender.email
				# send_mail(subject, message, sender, recipient_adress)
				
				return render_to_response('apps/confirmation.html', context_instance=RequestContext(request))
		else:
			form = SendMessageForm()# An unbound form
			user = User.objects.get(username=request.user)
			#Ne mettre que les contacts de l'utilisateur courant
			contacts = list(ContactsList.objects.filter(user =user))
			#for contact in contacts:
				#recipients += User.objects.get(id=contact.contact_id)
				#form.recipient += User.objects.get(id=contact.contact_id)
			#form.recipient = recipients

		return render_to_response('apps/send_message.html', {'form': form, 'contacts': contacts}, context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect("/login/")
		
	return HttpResponseRedirect("/")

#reply message
@login_required
def reply_message(request):
	if request.user.is_authenticated():
		idm = request.GET.get('id')
		if request.method == 'POST': # If the form has been submitted...
			user = User.objects.get(username=request.user)
			form = ReplyMessageForm(request.POST) # A form bound to the POST data
			if form.is_valid(): # All validation rules pass
				#Create 2 new messages in table message
				sended = Message()
				#recipient = User.objects.get(username=request.POST['recipient'])
				
				sended.writer_id = user.id
				sended.recipient_id = request.POST['recipient']#recipient.id
				#sended.recipient_id = idm
				sended.subject = request.POST['subject']
				sended.content = request.POST['content']
				sended.date = datetime.now()#date("Y-m-d") # A CHANGER DANS LA BDD pour avoir l'heure
				sended.is_read = False
				sended.id_owner = sended.writer_id
				
				user2 = User.objects.get(id=sended.recipient_id)
				send_mail('Nouveau message FacByCar', 'Vous avez reçu un nouveau message. Pour le consulter: http://facbycar.alwaysdata.com/messages', 'no-reply@facbycar.com',[user2.email], fail_silently=False)
			
				recieped = deepcopy(sended)
				#recieped = sended
				recieped.id_owner = request.POST['recipient']#recipient.id
				#recieped.id_owner = idm
	
				sended.is_read = 1
				recieped.save()
				sended.save()

				
				return render_to_response('apps/confirmation.html', context_instance=RequestContext(request))
		else:
			form = ReplyMessageForm()# An unbound form

		return render_to_response('apps/reply_message.html', {'form': form, 'idm': idm}, context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect("/login/")
		
	return HttpResponseRedirect("/")
#Afficher un message selectionne
	#Afficher le fil de conversation entre l'utilisateur et le destinataire.
	
def read_message(request):
	if request.user.is_authenticated():
		#message = Message.objects.get(id_message=request.POST['id_message'])
		idm = request.GET.get('id')
		user = User.objects.get(username=request.user)
		message = Message.objects.get(id=idm)

		message.is_read = 1
		message.save()
		print message.is_read
		
		r = User.objects.get(id=message.recipient_id)
		w = User.objects.get(id=message.writer_id)
		
		
		idr = r.id
		idw = w.id

		if user.id == idr:
			inter = w.username
		else:
			inter = r.username
	
		receip_messages = list(Message.objects.filter(recipient__id =idw, writer__id = idr).exclude(id_owner=idw))
		sended_messages = list(Message.objects.filter(recipient__id =idr, writer__id = idw).exclude(id_owner=idr))

		messages = receip_messages
		messages += sended_messages
	
		#messages.sort(key=itemgetter('date'), reverse=True)
		#messages = messages1 + messages2 orderedby date
		

		
		return render_to_response('apps/read_message.html', {'messages': messages, 'receip_messages': receip_messages, 'sended_messages': sended_messages,'r': r, 'w': w, 'inter': inter}, context_instance=RequestContext(request))
		
	else:
		return HttpResponseRedirect("/login/")
		
	return HttpResponseRedirect("/")
	
	
def messages(request):
	if request.user.is_authenticated():
	#afficher la liste des messages ou l'utilisateur apparait en recipient
		#user = request.user
		user = User.objects.get(username=request.user)
		#id = recipient.id
		
		#messages = Message.objects.filter(recipient__id=user.id).exclude(id_owner=user.id)
		messages = Message.objects.filter(recipient__id=user.id, id_owner=user.id)

		return render_to_response('apps/messages.html', {'messages': messages}, context_instance=RequestContext(request)) 

	else:
		return HttpResponseRedirect("/login/")
		
	return HttpResponseRedirect("/")

def sended_messages(request):#Afficher la liste des messages envoyes
	if request.user.is_authenticated():
	#afficher la liste des messages ou l'utilisateur apparait en writer
		user = request.user
		messages = Message.objects.filter(writer__id=user.id, id_owner=user.id)

		return render_to_response('apps/sended_messages.html', {'messages': messages}, context_instance=RequestContext(request)) 

	else:
		return HttpResponseRedirect("/login/")
		
	return HttpResponseRedirect("/")
		
def delete_message_confirmation(request):#Fonction suppression d'un message
	if request.user.is_authenticated():
		idm = request.GET.get('id')

		return render_to_response('apps/delete_message_confirmation.html', {'id': idm}, context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect("/login/")
		
	return HttpResponseRedirect("/")
	
def delete_message(request):#Fonction suppression d'un message
	if request.user.is_authenticated():
		idm = request.GET.get('id')
		message = Message.objects.get(id=idm)
		message.delete()

			
		return render_to_response('apps/delete_message.html', context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect("/login/")
		
	return HttpResponseRedirect("/")

	#return render_to_response('apps/search.html', context_instance=RequestContext(request))

def user_search(request):
	query = request.GET.get('q', '')
	if query:
		qset = (
			Q(username__icontains=query) |
			Q(email__icontains=query) |
			Q(first_name__icontains=query) |
			Q(last_name__icontains=query)
		)
		results = User.objects.filter(qset).distinct()
	else:
		results = []
	return render_to_response("apps/user_search.html", {"results": results,"query": query}, context_instance=RequestContext(request))

def user_contacts_list(request):
	if request.user.is_authenticated():
		user = User.objects.get(username=request.user)
		contacts = ContactsList.objects.filter(user = user)

		return render_to_response('apps/user_contacts_list.html',{'contacts': contacts}, context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect("/login/")

def add_contact_to_list(request):
	if request.user.is_authenticated():
		idu = request.GET.get('id')
		current_user = User.objects.get(username=request.user)
		new_contact = User.objects.get(id=idu)
		contact = ContactsList.objects.filter(user = current_user, contact = new_contact)
		if contact:
			contacts = ContactsList.objects.filter(user = current_user)
		else:
			form = AddContactToListForm()
			#ajout dans la liste
			contact = form.save(commit=False)	
			contact.user = current_user
			contact.contact = new_contact
			contact.username = new_contact.username
			contact.save()
			contacts = ContactsList.objects.filter(user = current_user)
		
		
		#TODO rediriger vers la page profile et non contacts
		return render_to_response('apps/user_contacts_list.html',{'contacts': contacts}, context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect("/login/")
		
def del_contact_to_list(request):
	if request.user.is_authenticated():
		idu = request.GET.get('id')
		current_user = User.objects.get(username=request.user)
		#suppression à faire
		link = ContactsList.objects.filter(user=current_user,contact=idu)
		link.delete()
		
		contacts = ContactsList.objects.filter(user = current_user)
		
		return render_to_response('apps/user_contacts_list.html',{'contacts': contacts}, context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect("/login/")
		
		
def faq(request):
	return render_to_response('apps/faq.html', context_instance=RequestContext(request))
	
def charte(request):
	return render_to_response('apps/charte.html', context_instance=RequestContext(request))
	
def plan_du_site(request):
	return render_to_response('apps/plan_du_site.html', context_instance=RequestContext(request))

def mentions_legales(request):
	return render_to_response('apps/mentions_legales.html', context_instance=RequestContext(request))
	
def contact(request):
    if request.method == 'POST': # If the form has been submitted...
        form = ContactForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
			subject = form.cleaned_data['subject']
			message = form.cleaned_data['message']
			sender = form.cleaned_data['sender']

			recipients = ['v.ralliere@gmail.com']
			
			send_mail(subject, message, sender, recipients)

			return HttpResponseRedirect('/') # Redirect after POST
    else:
        form = ContactForm() # An unbound form

    return render_to_response('apps/contact.html', {'form': form, 'form_action': "/contact/"}, context_instance=RequestContext(request))
