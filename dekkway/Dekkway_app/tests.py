# from django.test import TestCase

# # Create your tests here.

from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from .models import Logement, Media
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile

class LogementSearchTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Création de logements tests
        self.logement1 = Logement.objects.create(
            type="Maison",
            description="Maison spacieuse",
            latitude=14.716677,  # Dakar
            longitude=-17.467686,
            prix=200000,
            quartier="Plateau",
            region="Dakar"
        )
        
        self.logement2 = Logement.objects.create(
            type="Appartement",
            description="Appartement moderne",
            latitude=14.764943,  # 10km au nord de Dakar
            longitude=-17.416587,
            prix=150000,
            quartier="Almadies",
            region="Dakar"
        )
        
        # Ajout de médias
        image = SimpleUploadedFile(
            "baniere_test.jpg", 
            b"file_content", 
            content_type="image/jpeg"
        )
        
        Media.objects.create(
            logement=self.logement1,
            fichier=image,
            type="image"
        )

    def test_search_within_radius(self):
        # Coordonnées du centre de Dakar
        url = reverse('logement-list-create') + '?lat=14.716677&lng=-17.467686&rayon=5'
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)  # Seul logement1 devrait être dans le rayon
        self.assertIn('banniere', response.data[0])
        
        # Vérification de l'URL de la bannière
        media = Media.objects.first()
        self.assertIn(media.fichier.url, response.data[0]['banniere'])

    def test_search_outside_radius(self):
        # Recherche avec un rayon trop petit
        url = reverse('logement-list-create') + '?lat=14.716677&lng=-17.467686&rayon=1'
        
        response = self.client.get(url)
        self.assertEqual(len(response.data), 0)

    def test_banniere_fallback(self):
        # Création d'un logement sans média "baniere"
        logement3 = Logement.objects.create(
            latitude=14.716677,
            longitude=-17.467686,
            type="Studio"
        )
        
        # Ajout d'une image sans "baniere" dans le nom
        image = SimpleUploadedFile(
            "test_image.jpg", 
            b"content", 
            content_type="image/jpeg"
        )
        Media.objects.create(
            logement=logement3,
            fichier=image,
            type="image"
        )
        
        url = reverse('logement-list-create') + '?lat=14.716677&lng=-17.467686'
        response = self.client.get(url)
        
        # Doit retourner la première image disponible
        self.assertIsNotNone(response.data[0]['banniere'])

    def test_query_optimization(self):
        from django.db import connection
        
        with self.assertNumQueries(2):  # 1 pour logements + 1 pour médias
            response = self.client.get(reverse('logement-list-create'))
            _ = response.data  # Force l'évaluation de la requête

    def test_haversine_calculation(self):
        # Test de distance entre Dakar et Almadies (~10km)
        from math import radians
        
        lat1 = radians(14.716677)
        lng1 = radians(-17.467686)
        lat2 = radians(14.764943)
        lng2 = radians(-17.416587)
        
        # Calcul manuel
        delta_lat = lat2 - lat1
        delta_lng = lng2 - lng1
        
        a = (pow(sin(delta_lat / 2), 2) + 
             cos(lat1) * cos(lat2) * 
             pow(sin(delta_lng / 2), 2))
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = 6371 * c
        
        # Vérification que la distance calculée est ~10km
        self.assertAlmostEqual(distance, 10, delta=1)