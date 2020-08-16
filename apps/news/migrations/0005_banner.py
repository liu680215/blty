# Generated by Django 3.0.2 on 2020-08-02 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0004_auto_20200802_0958'),
    ]

    operations = [
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.IntegerField(default=0)),
                ('image_url', models.URLField()),
                ('link_to', models.URLField()),
                ('pub_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-priority'],
            },
        ),
    ]
