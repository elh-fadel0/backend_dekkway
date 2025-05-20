from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.validators import FileExtensionValidator
from .models import Bailleur, Locataire, Administrateur, Logement, Location, Notification, Service, Favoris, LocataireService, Media

#recup mot de passe
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model




class BailleurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bailleur
        fields = '__all__'

class BailleurInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bailleur
        fields = ['nom', 'prenom', 'email', 'adresse', 'telephone', 'photo_profil']

class LocataireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Locataire
        fields = ['username', 'email', 'nom', 'prenom', 'adresse', 'telephone', 'date_de_naissance', 'photo_profil', 'date_creation', 'date_modification']

class AdministrateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Administrateur
        fields = '__all__'


class LogementsRechercheSerializer(serializers.ModelSerializer):
    banniere = serializers.SerializerMethodField()

    class Meta:
        model = Logement
        fields = ['id', 'type', 'titre', 'region', 'quartier', 'prix', 'banniere', 'equipements', 'duree']

    def get_banniere(self, obj):
        # Recherche le premier média image dont le nom contient "baniere"
        media = obj.medias.filter(
            type=Media.IMAGE,
            fichier__icontains='baniere'  # Recherche insensible à la casse
        ).first()
        
        if media:
            return media.fichier.url
        # Fallback: première image si pas de bannière trouvée
        fallback_media = obj.medias.filter(type=Media.IMAGE).first()
        return fallback_media.fichier.url if fallback_media else None
      
# class MediaSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Media
#         fields = "__all__"
#         extra_kwargs = {
#             'logement': {'required': False}  # Auto-rempli par la vue
#         }  



class MediaSerializer(serializers.ModelSerializer):
    fichier = serializers.FileField(required=True)  # Champ explicite
    
    class Meta:
        model = Media
        fields = "__all__"
        extra_kwargs = {
            'fichier': {
                'validators': [
                    FileExtensionValidator(
                        allowed_extensions=['jpg', 'jpeg', 'png', 'mp4', 'mov'],
                        message="Format de fichier non supporté. Formats autorisés: jpg, jpeg, png, mp4, mov"
                    )
                ]
            }
        }

class NestedMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        # Liste uniquement les champs que tu veux retourner
        fields = ['fichier', 'type', 'date_ajout']


# class MediaSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Media
#         fields = "__all__"
#         read_only_fields = ('date_ajout',)

# class LogementSerializer(serializers.ModelSerializer):
#     medias = MediaSerializer(many=True, read_only=True)
#     class Meta:
#         model = Logement
#         fields = ['type', 'description', 'region', 'quartier', 'prix', 'nombre_de_chambres', 'medias', 'equipements']


class LogementSerializer(serializers.ModelSerializer):
    medias = NestedMediaSerializer(many=True)  # Retire read_only=True
    agent = BailleurInfoSerializer(source='bailleur', read_only=True)  # Ajout du champ agent

    class Meta:
        model = Logement
        fields = [
            'type', 'description', 'region', 
            'quartier', 'prix', 'nombre_de_chambres', 'equipements', 'latitude', 'longitude', 
            'medias', 'salons', 'cuisines', 'salles_de_bain', 'garage', 'agent', 'duree'
        ]
    
    def validate_medias(self, value):
        """Valide le nombre de vidéos dans les médias"""
        video_count = sum(1 for m in value if m.get('type') == Media.VIDEO)
        
        if video_count > 1:
            raise serializers.ValidationError("Un seul vidéo autorisé par logement")
        
        return value
    
    def create(self, validated_data):
        medias_data = validated_data.pop('medias', [])
        logement = Logement.objects.create(**validated_data)
        
        # Création des médias associés
        for media_data in medias_data:
            Media.objects.create(logement=logement, **media_data)
            
        return logement

    def update(self, instance, validated_data):
        medias_data = validated_data.pop('medias', [])
        
        # Mise à jour du logement
        instance = super().update(instance, validated_data)
        
        # Mise à jour des médias
        instance.medias.all().delete()  # Supprime les anciens médias
        for media_data in medias_data:
            Media.objects.create(logement=instance, **media_data)
        
        return instance


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class FavorisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favoris
        fields = '__all__'


class LocataireServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocataireService
        fields = '__all__'
        

# class InscriptionLocataireSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)

#     class Meta:
#         model = Locataire
#         fields = ['username', 'email', 'password', 'nom', 'prenom', 'telephone', 'date_de_naissance']

#     def create(self, validated_data):
#         user = Locataire.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             password=validated_data['password'],
#             nom=validated_data.get('nom', ''),
#             prenom=validated_data.get('prenom', ''),
#             telephone=validated_data.get('telephone', ''),
#             date_de_naissance=validated_data.get('date_de_naissance', ''),
#         )
#         return user



class InscriptionLocataireSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    photo_profil = serializers.FileField(required=False)

    class Meta:
        model = Locataire
        # On retire le champ 'adresse' de la liste
        fields = ['username', 'email', 'password', 'nom', 'prenom', 'telephone', 'date_de_naissance', 'photo_profil']

    def create(self, validated_data):
        user = Locataire.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            nom=validated_data.get('nom', ''),
            prenom=validated_data.get('prenom', ''),
            # On ne gère plus 'adresse'
            telephone=validated_data.get('telephone', ''),
            date_de_naissance=validated_data.get('date_de_naissance', ''),
            photo_profil=validated_data.get('photo_profil', None),
        )
        return user



# Serializer pour la connexion
class ConnexionLocataireSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            user = Locataire.objects.get(email=email)
        except Locataire.DoesNotExist:
            raise serializers.ValidationError("Adresse e-mail ou mot de passe incorrect")

        user = authenticate(username=user.username, password=password)
        if not user:
            raise serializers.ValidationError("Adresse e-mail ou mot de passe incorrect")

        data['user'] = user
        return data
    
    
    
    


# Serializer pour la réinitialisation du mot de passe

UserModel = get_user_model()

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            return UserModel.objects.get(email=value)
        except UserModel.DoesNotExist:
            raise serializers.ValidationError("Aucun utilisateur avec cet email.")

class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data['uid']))
            user = UserModel.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            raise serializers.ValidationError("Lien invalide")

        if not PasswordResetTokenGenerator().check_token(user, data['token']):
            raise serializers.ValidationError("Token invalide ou expiré")

        data['user'] = user
        return data


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Le mot de passe actuel est incorrect.")
        return value
    
    def validate(self, data):
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError("Le nouveau mot de passe doit être différent de l'ancien.")
        return data
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user