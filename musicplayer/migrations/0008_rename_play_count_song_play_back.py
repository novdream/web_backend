# Generated by Django 5.0.6 on 2024-06-10 08:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('musicplayer', '0007_message_has_read_message_is_system_message_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='song',
            old_name='play_count',
            new_name='play_back',
        ),
    ]