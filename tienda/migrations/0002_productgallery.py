# Generated by Django 3.2.3 on 2021-07-18 16:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tienda', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductGallery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(max_length=255, upload_to='photos/products')),
                ('producto', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='tienda.producto')),
            ],
        ),
    ]
