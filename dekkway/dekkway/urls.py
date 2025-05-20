"""
URL configuration for dekkway project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from rest_framework.routers import DefaultRouter
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from Dekkway_app.views import BailleurListCreateView, BailleurDetailView, LocataireListCreateView, LocataireDetailView, AdministrateurListCreateView, AdministrateurDetailView, LogementListCreateView, LocationListCreateView, LocationDetailView, NotificationListCreateView, NotificationDetailView, ServiceListCreateView, ServiceDetailView, FavorisListCreateView, FavorisDetailView, LocataireServiceDetailView, LogementDetailsListCreateView, InscriptionLocataireView, ConnexionLocataireView, ProfilLocataireView, MediaViewSet, PasswordResetRequestView, PasswordResetConfirmView, PasswordChangeView

router = DefaultRouter()
router.register(r'medias', MediaViewSet, basename='media')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('bailleurs/', BailleurListCreateView.as_view(), name='bailleur-list-create'),
    path('bailleurs/<int:pk>/', BailleurDetailView.as_view(), name='bailleur-detail'),

    path('locataires/', LocataireListCreateView.as_view(), name='locataire-list-create'),
    path('locataires/<int:pk>/', LocataireDetailView.as_view(), name='locataire-detail'),

    path('administrateurs/', AdministrateurListCreateView.as_view(), name='administrateur-list-create'),
    path('administrateurs/<int:pk>/', AdministrateurDetailView.as_view(), name='administrateur-detail'),

    path('rech-logements/', LogementListCreateView.as_view(), name='logement-list-create'),
    
    
    path('details-logements/<int:pk>/', LogementDetailsListCreateView.as_view(), name='logement-detail'),


    path('locations/', LocationListCreateView.as_view(), name='location-list-create'),
    path('locations/<int:pk>/', LocationDetailView.as_view(), name='location-detail'),

    path('notifications/', NotificationListCreateView.as_view(), name='notification-list-create'),
    path('notifications/<int:pk>/', NotificationDetailView.as_view(), name='notification-detail'),

    path('services/', ServiceListCreateView.as_view(), name='service-list-create'),
    path('services/<int:pk>/', ServiceDetailView.as_view(), name='service-detail'),

    path('favoris/', FavorisListCreateView.as_view(), name='favoris-list-create'),
    path('favoris/<int:pk>/', FavorisDetailView.as_view(), name='favoris-detail'),
    
    
    path('locataire_services/<int:pk>/', LocataireServiceDetailView.as_view(), name='locataire-service-detail'),

    path('loca-inscription/', InscriptionLocataireView.as_view(), name='inscription locataire'),
    path('loca-connexion/', ConnexionLocataireView.as_view(), name='connexion locataire'),
    
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-change/', PasswordChangeView.as_view(), name='password_change'),
    
    path('profil-locataire/', ProfilLocataireView.as_view(), name='profil locataire'),
    
    # path('medias/', MediaViewSet.as_view(), name='media-list-create'),
    # path('medias/<int:pk>/', MediaViewSet.as_view(), name='media-detail'),
    
] + router.urls + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)