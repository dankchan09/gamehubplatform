from django.contrib import admin
from django.contrib.auth.models import User
admin.site.site_header = 'Game Hub Administration'
admin.site.site_title = 'Game Hub'
admin.site.index_title = 'Welcome to Game Hub Admin Panel'

admin.register(User)


