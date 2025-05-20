from django.contrib import admin
from .models import Bailleur, Locataire, Administrateur, Logement, Location, Notification, Service, Favoris, LocataireService, Media  # Import your models

# Register your models here.
admin.site.register(Bailleur)
admin.site.register(Locataire)
admin.site.register(Administrateur)
admin.site.register(Logement)
admin.site.register(Location)
admin.site.register(Notification)
admin.site.register(Service)
admin.site.register(Favoris)
admin.site.register(LocataireService)
admin.site.register(Media)



