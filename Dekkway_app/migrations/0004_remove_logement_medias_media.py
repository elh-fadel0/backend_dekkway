# Generated by Django 5.1.7 on 2025-03-14 16:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Dekkway_app', '0003_utilisateur_date_de_naissance'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='logement',
            name='medias',
        ),
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fichier', models.FileField(upload_to='logements/')),
                ('type', models.CharField(choices=[('image', 'Image'), ('video', 'Vidéo')], max_length=10)),
                ('date_ajout', models.DateTimeField(auto_now_add=True)),
                ('logement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medias', to='Dekkway_app.logement')),
            ],
        ),
    ]
