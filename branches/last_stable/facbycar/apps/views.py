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



def home(request):
	if request.user.is_authenticated():
		user = User.objects.get(username=request.user)
		profile = user.get_profile()
		return render_to_response('apps/home.html', {'user': user, 'profile': profile}, context_instance=RequestContext(request))
	else:
		return render_to_response('apps/home.html', {'user': "none"}, context_instance=RequestContext(request))

def register(request):
	if request.method == 'POST': # If the form has been submitted...
		form = RegisterForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			u = form.save()
			u.set_password(form.cleaned_data['password'])
			u.save()
			u.profile = UserProfile(user=u)
			u.profile.save()
			user = auth.authenticate(username=u.username, password=form.cleaned_data['password'])
			auth.login(request, user)
			return HttpResponseRedirect("/edit_profile/")
	else:
		form = RegisterForm()

   	return render_to_response('apps/register.html', {'form': form,}, context_instance=RequestContext(request))

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
		
		routes_drivers = Route.objects.filter(car__in=cars).order_by('date_departure')[:3]
		routes_passengers = Route.objects.filter(passengers=request.user).order_by('date_departure')[:3]
		
		return render_to_response('apps/profile.html', {'profile' : profile, 'user': user, 'cars':cars, 'messages':messages, 'comments':comments, 'routes_drivers':routes_drivers, 'routes_passengers':routes_passengers},context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect("/login/")
	
def user_profile(request):
	if request.method == 'POST':
		user = User.objects.get(id=request.POST['id_user'])
		profile = user.get_profile()
		form = CommForm(request.POST) # A form bound to the POST data

		user_user = User.objects.get(id=request.POST['id_user_profil'])
		profile_user = user_user.get_profile()
		cars_user = Car.objects.filter(user=user_user)
		comments_user = Comment.objects.filter(recipient__id=request.POST['id_user_profil'])
		
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
			
			return render_to_response('apps/user_profile.html', { 'profile_user' :profile_user, 'user_user': user_user, 'cars_user':cars_user, 'comments_user':comments_user, 'form':form},context_instance=RequestContext(request))

	else:
		if request.user.is_authenticated():
			id_u = request.GET.get('u')
		
			user_user = User.objects.get(id=id_u)
			profile_user = user_user.get_profile()
			cars_user = Car.objects.filter(user=user_user)
			comments_user = Comment.objects.filter(recipient__id=user_user.id)
			comments_user.order_by('-id')
			
			form = CommForm()
			
			return render_to_response('apps/user_profile.html', { 'profile_user' :profile_user, 'user_user': user_user, 'cars_user':cars_user, 'comments_user':comments_user, 'form':form},context_instance=RequestContext(request))

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
				car.url_pic = 'picts/default_car.png'
			car.save()
			return HttpResponseRedirect('/car/')
	else:
		form = AddCarForm()
		
	return render_to_response('apps/form.html', {'form': form,	'form_action': "/add_car/"}, context_instance=RequestContext(request))

@login_required
def edit_car(request):
	user = User.objects.get(username=request.user)
	if request.method == 'POST':
		form = DeleteCarForm(request.POST, request.FILES, cur_user = user)
		if form.is_valid():
			request.session['temp_data'] = form.cleaned_data['carList']
			return redirect('/edit_car2/')
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

from datetime import datetime
@login_required
def add_route1(request):
	if request.method == 'POST':
		form = AddRoute1Form(request.POST)
		if form.is_valid():
			route = form.save(commit=False)
			request.session['temp_data'] = route
			return redirect('/add_route2/')
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
			rd = form_daily.save(commit=False)
			rd.start_time = request.POST['start_time']
			rd.end_time = request.POST['end_time']
			request.session['temp_daily'] = rd
			route.date_departure = request.POST['start_time']
			route.hour = '00:00'
			request.session['temp_data'] = route
			return redirect('/add_route3/')
		if form.is_valid():
			route.date_departure = request.POST['date']
			route.hour = form.cleaned_data['hour']
			request.session['temp_data'] = route
			return redirect('/add_route3/')
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
	if route.is_driver == 1:
		driver = 1
		if request.method == 'POST':
			form = AddRoute3Form(request.POST, cur_user=user)			
			if form.is_valid():
				route.car = form.cleaned_data['car']
				route.nb_passengers = form.cleaned_data['nb_passengers']
				route.price = form.cleaned_data['price']
				route.has_big_boot = form.cleaned_data['has_big_boot']
				route.added_date = datetime.now()
				route.is_driver = 1
				route.save()
				route.passengers.add(user)
				route.save()
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
				form = AddRoute3Form(cur_user=user)	
	else:
		driver = 0
		if request.method == 'POST':
			form = AddRoute3bForm(request.POST)	
			if form.is_valid():
				route.nb_passengers = 1
				route.price = form.cleaned_data['price']
				route.has_big_boot = form.cleaned_data['has_big_boot']
				route.added_date = datetime.now()
				route.is_driver = 0
				route.save()
				route.passengers.add(user)
				route.save()
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

	return render_to_response('apps/add_route3.html', {'form': form, 'form_action': "/add_route3/", 'driver':driver}, context_instance=RequestContext(request))

def summary(request):
	return render_to_response('apps/summary.html', context_instance=RequestContext(request))

@login_required	
def my_routes(request):
	cars = Car.objects.filter(user=request.user)
	route = Route.objects.filter(car__in=cars).order_by('date_departure')[0]
	routes_driver = Route.objects.filter(car__in=cars).order_by('date_departure')
	routes_passengers = Route.objects.exclude(car__in=cars).filter(passengers=request.user).order_by('date_departure')
	#routes_passengers = Route.objects.filter(passengers=request.user, car__isnull=False).order_by('date_departure') #pour le moment pas de gestion des demandes
	return render_to_response('apps/my_routes.html', { 'routes_driver' : routes_driver, 'routes_passengers' : routes_passengers},context_instance=RequestContext(request))

def route(request):
	id_route = request.GET.get('id')
	route = Route.objects.get(id=id_route)
	if route.is_daily is True:
		daily = Date_daily.objects.get(route=route)
	else:
		daily = ''
	return render_to_response('apps/route.html', { 'route' : route, 'daily':daily},context_instance=RequestContext(request))

	
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
	
				
				recieped.save()
				sended.save()
				
				
				
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

		return render_to_response('apps/send_message.html', {'form': form}, context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect("/login/")
		
	return HttpResponseRedirect("/")


#Afficher un message selectionne
	#Afficher le fil de conversation entre l'utilisateur et le destinataire.
	
def read_message(request):
	if request.user.is_authenticated():
		#message = Message.objects.get(id_message=request.POST['id_message'])
		idm = request.GET.get('id')
		message = Message.objects.get(id=idm)
		
		r = User.objects.get(id=message.recipient_id)
		w = User.objects.get(id=message.writer_id)

		idr = r.id
		idw = w.id
		# print idr
		# print idw
		#messages = Message.objects.filter((recipient__id =idr and writer__id = idw) or (recipient__id = idw and writer__id = idr))
		
		#messages = Message.objects.filter(recipient__id=idr && writer__id = idw)
		
		
		#affiche le contenu du message
		# recipient = User.objects.get(id=message.recipient_id)
		# writer  = User.objects.get(id=message.writer_id)
		#name_w = writer.login
		#name_r = recipient.login
		
			# tout les messages ou A est writer
		#messages1 = Message.objects.filter(recipient__id =idw)
		#messages1 = messages.filter(writer__id = idw)
	
		messages1 = list(Message.objects.filter(recipient__id =idw, writer__id = idr).exclude(id_owner=idw))
		messages2 = list(Message.objects.filter(recipient__id =idr, writer__id = idw).exclude(id_owner=idr))

		messages = messages1
		messages += messages2
		
	#	messages.sort(key=itemgetter('date'), reverse=True)
		
		
		#messages = messages1 + messages2 orderedby date

			# tout les messages ou B est recipiant
		# messages2 = Message.objects.filter(recipient__id =idr)
		# messages2 = messages.filter(writer__id = idw)
			
			# Afficher tout les messages entre A et B, par chronologie
			# Afficher les messages ou le sender du message est A ou B et le recipient est B ou A
		
		# q = request.GET.get("id", "")
		# if q and len(q) >= 3:
			# clause = Q(dirtword__icontains=q)               \
				   # | Q(description__icontains=q)       \
				   # | Q(tags__name__icontains=q)       
			# site_search = Dirt.objects.filter(clause).distinct()
		# else:
			# site_search = Dirt.objects.order_by('?')[:100]
	
		if message.is_read == 0 :
			message.is_read = 1
			message.save()
			
		return render_to_response('apps/read_message.html', {'messages': messages, 'messages1': messages1, 'messages2': messages2,'r': r, 'w': w}, context_instance=RequestContext(request))
		#return render_to_response('apps/read_message.html', {'message': message}, context_instance=RequestContext(request))

	else:
		return HttpResponseRedirect("/login/")
		
	return HttpResponseRedirect("/")
	
	
def messages(request):
	if request.user.is_authenticated():
	#afficher la liste des messages ou l'utilisateur apparait en recipient
		user = request.user
		#id = recipient.id
		
		messages = Message.objects.filter(recipient__id=user.id).exclude(id_owner=user.id)

		 #Entry.objects.filter(~Q(id = 3))

			
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
