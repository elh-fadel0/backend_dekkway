from math import radians, cos  # Ajouté
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.db.models import F, FloatField, ExpressionWrapper
from django.db.models.functions import Radians, Sin, Cos, ATan2, Sqrt, Power
from django.shortcuts import render
from rest_framework import generics, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from .models import Logement
from .filters import LogementFilter
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Bailleur, Locataire, Administrateur, Logement, Location, Notification, Service, Favoris, LocataireService, Media
from .serializers import BailleurSerializer, LocataireSerializer, AdministrateurSerializer, LocationSerializer, NotificationSerializer, ServiceSerializer, FavorisSerializer, LocataireServiceSerializer, LogementsRechercheSerializer, LogementsRechercheSerializer, LogementSerializer, InscriptionLocataireSerializer, ConnexionLocataireSerializer, MediaSerializer
from .serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer, PasswordChangeSerializer
#importations mot de passe
from django.core.mail import send_mail
from django.urls import reverse, reverse_lazy
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

#redirection
from django.contrib.auth.views import PasswordResetConfirmView
from django.http import JsonResponse




# Create your views here.

class BailleurListCreateView(generics.ListCreateAPIView):
    queryset = Bailleur.objects.all()
    serializer_class = BailleurSerializer

class BailleurDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bailleur.objects.all()
    serializer_class = BailleurSerializer

class LocataireListCreateView(generics.ListCreateAPIView):
    queryset = Locataire.objects.all()
    serializer_class = LocataireSerializer

class LocataireDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Locataire.objects.all()
    serializer_class = LocataireSerializer

class AdministrateurListCreateView(generics.ListCreateAPIView):
    queryset = Administrateur.objects.all()
    serializer_class = AdministrateurSerializer

class AdministrateurDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Administrateur.objects.all()
    serializer_class = AdministrateurSerializer
    

class LogementListCreateView(generics.ListCreateAPIView):
    queryset = Logement.objects.prefetch_related('medias')
    serializer_class = LogementsRechercheSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = LogementFilter
    

    def get_queryset(self):
        queryset = super().get_queryset()
        
        
        lat = self.request.GET.get('lat')
        lng = self.request.GET.get('lng')
        rayon = float(self.request.GET.get('rayon', 10))  # Par défaut : 10 km
        
        
        
        if lat and lng:
            lat = float(lat)
            lng = float(lng)
            
            # Filtre initial pour limiter la recherche à une boîte englobante
            delta_lat = rayon / 111  # 1° de latitude ≈ 111 km
            delta_lng = rayon / (111 * cos(radians(lat)))  # Ajustement selon la latitude
            
            queryset = queryset.filter(
                latitude__range=(lat - delta_lat, lat + delta_lat),
                longitude__range=(lng - delta_lng, lng + delta_lng)
            )

            # Ajout de la distance Haversine pour affiner les résultats
            queryset = queryset.annotate(
                distance=self.haversine_sql(lat, lng)
            ).filter(distance__lte=rayon).order_by('distance')

        return queryset
    
    def haversine_sql(self, lat, lng):
        """Génère une expression SQL pour calculer la distance Haversine corrigée"""
        lat_rad = Radians(F('latitude'))
        lng_rad = Radians(F('longitude'))
        input_lat_rad = radians(lat)
        input_lng_rad = radians(lng)

        delta_lat = lat_rad - input_lat_rad
        delta_lng = lng_rad - input_lng_rad

        # Utilisation de Power() au lieu de l'opérateur **
        a_expression = (
            Power(Sin(delta_lat / 2.0), 2) + 
            Cos(input_lat_rad) * 
            Cos(lat_rad) * 
            Power(Sin(delta_lng / 2.0), 2)
        )

        a = ExpressionWrapper(a_expression, output_field=FloatField())
        sqrt_a = Sqrt(a)
        sqrt_1_minus_a = Sqrt(1.0 - a)
        c = ExpressionWrapper(2.0 * ATan2(sqrt_a, sqrt_1_minus_a), output_field=FloatField())

        return ExpressionWrapper(6371.0 * c, output_field=FloatField())
    




# class LogementDetailsListCreateView(generics.ListCreateAPIView):
#     queryset = Logement.objects.all()
#     serializer_class = LogementSerializer


class LogementDetailsListCreateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Logement.objects.all()
    serializer_class = LogementSerializer
    parser_classes = [MultiPartParser, JSONParser]  # Autorise les fichiers
    # permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(bailleur=self.request.user)  # Auto-attribution du bailleur




class LocationListCreateView(generics.ListCreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

class LocationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

class NotificationListCreateView(generics.ListCreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

class ServiceListCreateView(generics.ListCreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class FavorisListCreateView(generics.ListCreateAPIView):
    queryset = Favoris.objects.all()
    serializer_class = FavorisSerializer

class FavorisDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Favoris.objects.all()
    serializer_class = FavorisSerializer


class LocataireServiceListCreateView(generics.ListCreateAPIView):
    queryset = LocataireService.objects.all()
    serializer_class = LocataireServiceSerializer

class LocataireServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LocataireService.objects.all()
    serializer_class = LocataireServiceSerializer
    
# pour la recherche
class LogementListView(generics.ListAPIView):
    queryset = Logement.objects.all()
    serializer_class = LogementsRechercheSerializer


# # Vue pour inscription
# class InscriptionLocataireView(APIView):
#     def post(self, request):
#         serializer = InscriptionLocataireSerializer(data=request.data)
#         if serializer.is_valid():
#             utilisateur = serializer.save()
#             token, _ = Token.objects.get_or_create(user=utilisateur)
#             return Response({
#                 'message': 'Compte créé avec succès',
#                 'token': token.key
#             }, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class InscriptionLocataireView(APIView):
    def post(self, request):
        serializer = InscriptionLocataireSerializer(data=request.data)
        if serializer.is_valid():
            utilisateur = serializer.save()
            token, _ = Token.objects.get_or_create(user=utilisateur)
            return Response({
                'message': 'Compte créé avec succès',
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Vue pour connexion
class ConnexionLocataireView(APIView):
    def post(self, request):
        serializer = ConnexionLocataireSerializer(data=request.data)
        if serializer.is_valid():
            utilisateur = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=utilisateur)
            return Response({
                'message': 'Connexion réussie',
                'token': token.key
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class ProfilLocataireView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]  # Pour gérer les uploads de fichiers

    def get_user_from_token(self, request):
        # Vérification de l'authentification
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        # Log pour débogage
        print(f"Auth header reçu: {auth_header}")
        
        # Si l'en-tête commence par 'Bearer' ou 'Token', on extrait le token et on l'utilise
        if auth_header.startswith('Bearer ') or auth_header.startswith('Token '):
            token_key = auth_header.split(' ')[1]
            try:
                token = Token.objects.get(key=token_key)
                return token.user
            except Token.DoesNotExist:
                print(f"Token non trouvé: {token_key}")
                return None
        # Si l'en-tête est juste le token sans préfixe
        elif auth_header and not auth_header.startswith('Bearer ') and not auth_header.startswith('Token '):
            try:
                token = Token.objects.get(key=auth_header)
                return token.user
            except Token.DoesNotExist:
                print(f"Token brut non trouvé: {auth_header}")
                return None
        return None

    def get(self, request):
        # Récupération de l'utilisateur à partir du token
        user = self.get_user_from_token(request)
        if not user:
            return Response({'error': 'Token invalide ou manquant'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Utiliser l'utilisateur récupéré du token plutôt que request.user
        serializer = LocataireSerializer(user)
        return Response(serializer.data)
        
    def put(self, request):
        # Récupération de l'utilisateur à partir du token
        user = self.get_user_from_token(request)
        if not user:
            return Response({'error': 'Token invalide ou manquant'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Vérifier si la requête contient des données de formulaire ou JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Traitement des données de formulaire (avec fichiers)
            serializer = LocataireSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                # Gestion spécifique de la photo de profil si présente dans la requête
                if 'photo_profil' in request.FILES:
                    user.photo_profil = request.FILES['photo_profil']
                    user.save()  # Sauvegarder d'abord la photo
                
                serializer.save()  # Puis sauvegarder les autres champs
                return Response({
                    'message': 'Profil mis à jour avec succès',
                    'user': serializer.data
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Traitement des données JSON
            serializer = LocataireSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': 'Profil mis à jour avec succès',
                    'user': serializer.data
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        """Permet de mettre à jour partiellement le profil"""
        # Récupération de l'utilisateur à partir du token
        user = self.get_user_from_token(request)
        if not user:
            return Response({'error': 'Token invalide ou manquant'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = LocataireSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            # Gestion spécifique de la photo de profil si présente dans la requête
            if 'photo_profil' in request.FILES:
                user.photo_profil = request.FILES['photo_profil']
                user.save()  # Sauvegarder d'abord la photo
            
            serializer.save()  # Puis sauvegarder les autres champs
            return Response({
                'message': 'Profil mis à jour avec succès',
                'user': serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class MediaViewSet(viewsets.ModelViewSet):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    parser_classes = (MultiPartParser, FormParser)  # Essentiel pour les uploads
    # permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Validation supplémentaire
        instance = serializer.save()
        instance.full_clean()


# Vue pour la réinitialisation du mot de passe

class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['email']
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            reset_url = f"{request.build_absolute_uri('/')}reset-password-confirm/{uid}/{token}/"
            
            send_mail(
                'Réinitialisation de mot de passe',
                f'Cliquez sur ce lien pour réinitialiser votre mot de passe : {reset_url}',
                'noreply@example.com',
                [user.email],
                fail_silently=False,
            )
            return Response({'message': 'Email de réinitialisation envoyé'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Mot de passe mis à jour avec succès'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    




class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy("password_reset_complete")  # URL interne Django (on la change après)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        return JsonResponse({"message": "Mot de passe réinitialisé avec succès", "redirect": "http://localhost:3000/mot-de-passe-oublie/"})


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            # Générer un nouveau token après changement de mot de passe
            Token.objects.filter(user=request.user).delete()
            token, _ = Token.objects.get_or_create(user=request.user)
            return Response({
                'message': 'Mot de passe modifié avec succès',
                'token': token.key
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
