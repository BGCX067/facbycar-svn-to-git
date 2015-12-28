from django.contrib import admin
from facbycar.apps.models import *

class MusicAdmin(admin.ModelAdmin):
	prepopulated_fields = {"slug": ("type",)}

class UserProfileAdmin(admin.ModelAdmin):
	prepopulated_fields = {"slug": ("user",)}

class CommentAdmin(admin.ModelAdmin):
	prepopulated_fields = {"slug": ("id",)}

class MessageAdmin(admin.ModelAdmin):
	prepopulated_fields = {"slug": ("id",)}

class CarAdmin(admin.ModelAdmin):
	prepopulated_fields = {"slug": ("user", "model")}

class RouteAdmin(admin.ModelAdmin):
	prepopulated_fields = {"slug": ("city_d", "city_a", "car")}

class Round_tripAdmin(admin.ModelAdmin):
	prepopulated_fields = {"slug": ("route_going", "route_back")}

class Date_dailyAdmin(admin.ModelAdmin):
	prepopulated_fields = {"slug": ("route",)}

admin.site.register(Music, MusicAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Car, CarAdmin)
admin.site.register(Route, RouteAdmin)
admin.site.register(Round_trip, Round_tripAdmin)
admin.site.register(Date_daily, Date_dailyAdmin)
