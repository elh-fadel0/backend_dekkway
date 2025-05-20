from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError


# Create your models here.

# Modèle Utilisateur personnalisé
class Utilisateur(AbstractUser):
    nom = models.CharField(max_length=150)
    prenom = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    adresse = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    date_de_naissance = models.DateField(null=True, blank=True)
    photo_profil = models.FileField(upload_to="profils/", null=True, blank=True)
    
    # Résolution du conflit
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="utilisateur_groups",  # Nouveau related_name
        blank=True
    )

    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="utilisateur_permissions",  # Nouveau related_name
        blank=True
    )

    def __str__(self):
        return self.username

# Modèle Bailleur (hérite d'Utilisateur)
class Bailleur(Utilisateur):
    def __str__(self):
        return f"Bailleur: {self.username}"

# Modèle Locataire (hérite d'Utilisateur)
class Locataire(Utilisateur):
    def __str__(self):
        return f"Locataire: {self.username}"

# Modèle Administrateur (hérite d'Utilisateur)
class Administrateur(Utilisateur):
    def __str__(self):
        return f"Administrateur: {self.username}"

# Modèle Logement
class Logement(models.Model):
    DUREE_CHOICES = [
        ('longue durée', 'Longue durée'),
        ('courte durée', 'Courte durée'),
    ]
    
    bailleur = models.ForeignKey(Bailleur, on_delete=models.CASCADE, related_name="logements")
    quartier = models.CharField(max_length=255)
    titre = models.CharField(max_length=255, verbose_name="Titre du logement")
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    type = models.CharField(max_length=50)
    nombre_de_chambres = models.IntegerField()
    disponibilite = models.BooleanField(default=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    region = models.CharField(max_length=255, null=True, blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    equipements = models.JSONField(default=dict, blank=True)
    duree = models.CharField(max_length=20, choices=DUREE_CHOICES, default='longue durée', verbose_name="Durée de location")
    
    # Nouveaux champs pour les équipements
    salons = models.IntegerField(null=True, blank=True, verbose_name="Nombre de salons")
    cuisines = models.IntegerField(null=True, blank=True, verbose_name="Nombre de cuisines")
    salles_de_bain = models.IntegerField(null=True, blank=True, verbose_name="Nombre de salles de bain")
    garage = models.BooleanField(default=False, verbose_name="Présence d'un garage")

    def __str__(self):
        return f"{self.type} - {self.region} - {self.quartier} ({self.prix} CFA)"


# pour le stockages des mediaes
class Media(models.Model):
    IMAGE = "image"
    VIDEO = "video"

    TYPE_CHOICES = [
        (IMAGE, "Image"),
        (VIDEO, "Vidéo"),
    ]

    logement = models.ForeignKey("Logement", on_delete=models.CASCADE, related_name="medias")
    fichier = models.FileField(upload_to="logements/")
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.fichier.name}"

    def clean(self):
        if self.type == self.VIDEO:
            existing_video = Media.objects.filter(
                logement=self.logement, 
                type=self.VIDEO
            ).exclude(id=self.id)
            
            if existing_video.exists():
                raise ValidationError("Un seul vidéo autorisée par logement")

    def save(self, *args, **kwargs):
        self.full_clean()  # Force la validation avant sauvegarde
        super().save(*args, **kwargs)



# Modèle Location (Louer un logement)
class Location(models.Model):
    logement = models.ForeignKey(Logement, on_delete=models.CASCADE)
    locataire = models.ForeignKey(Locataire, on_delete=models.CASCADE)
    date_debut = models.DateField()
    date_fin = models.DateField()
    statut = models.CharField(max_length=50, choices=[("Confirmé", "Confirmé"), ("Annulé", "Annulé"), ("En attente", "En attente")])
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    methode_paiement = models.CharField(max_length=50)
    date_location = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Location {self.logement} par {self.locataire} ({self.statut})"

# Modèle Notification
class Notification(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    message = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)

    def __str__(self):
        return f"Notif {self.utilisateur.username} - {self.message[:30]}..."

# Modèle Service (Services proposés aux locataires)
class Service(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    disponibilite = models.BooleanField(default=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom


class LocataireService(models.Model):
    locataire = models.ForeignKey(Locataire, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    date_pris = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('locataire', 'service')

class Favoris(models.Model):
    locataire = models.ForeignKey(Locataire, on_delete=models.CASCADE)
    logement = models.ForeignKey(Logement, on_delete=models.CASCADE)
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("locataire", "logement")

    def __str__(self):
        return f"{self.locataire} - {self.logement}"
