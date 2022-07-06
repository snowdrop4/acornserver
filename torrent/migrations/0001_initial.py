from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_countries.fields
import picklefield.fields
import torrent.models.torrent


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MusicArtist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('formed', models.DateField(blank=True, null=True)),
                ('disbanded', models.DateField(blank=True, null=True)),
                ('country', django_countries.fields.CountryField(blank=True, max_length=2, null=True)),
                ('artist_type', models.CharField(choices=[('ART', 'Artist'), ('CRC', 'Dōjin circle'), ('PER', 'Person')], default='ART', max_length=3)),
            ],
            options={
                'verbose_name': 'Artist',
                'verbose_name_plural': 'Artists',
            },
        ),
        migrations.CreateModel(
            name='MusicContribution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contribution_type', models.CharField(choices=[('MA', 'Main'), ('GU', 'Guest'), ('CP', 'Composer'), ('CD', 'Conductor'), ('DJ', 'DJ/Compiler'), ('RM', 'Remixer'), ('PR', 'Producer'), ('VO', 'Vocals')], max_length=2)),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contributions', to='torrent.MusicArtist')),
            ],
            options={
                'verbose_name': 'Contribution',
                'verbose_name_plural': 'Contributions',
            },
        ),
        migrations.CreateModel(
            name='MusicRelease',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('label', models.CharField(max_length=256)),
                ('catalog_number', models.CharField(max_length=64)),
                ('release_format', models.CharField(choices=[('WB', 'Web'), ('CD', 'CD'), ('VN', 'Vinyl')], max_length=2)),
            ],
            options={
                'verbose_name': 'Release',
                'verbose_name_plural': 'Releases',
            },
        ),
        migrations.CreateModel(
            name='MusicTorrent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('metainfo_file', models.FileField(upload_to=torrent.models.torrent.upload_to)),
                ('infohash_sha1_hexdigest', models.CharField(max_length=40, unique=True)),
                ('torrent_size', models.IntegerField()),
                ('torrent_files', picklefield.fields.PickledObjectField(editable=False)),
                ('upload_datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('encode_format', models.CharField(choices=[('FLC016', 'FLAC / 16bit'), ('FLC024', 'FLAC / 24bit'), ('MP3VB2', 'MP3 / V2'), ('MP3VB0', 'MP3 / V0'), ('MP3320', 'MP3 / 320')], max_length=6)),
            ],
            options={
                'verbose_name': 'MusicTorrent',
                'verbose_name_plural': 'MusicTorrents',
            },
        ),
        migrations.CreateModel(
            name='MusicTorrentPeer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('peer_id', models.CharField(max_length=20, unique=True)),
                ('peer_ip', models.GenericIPAddressField()),
                ('peer_port', models.IntegerField()),
                ('last_seen', models.DateTimeField(default=django.utils.timezone.now)),
                ('torrent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='peers', to='torrent.MusicTorrent')),
            ],
            options={
                'verbose_name': 'MusicTorrent Peer',
                'verbose_name_plural': 'MusicTorrent Peers',
            },
        ),
        migrations.CreateModel(
            name='MusicTorrentDownload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('download_datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('torrent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='downloads', to='torrent.MusicTorrent')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='music_downloads', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'MusicTorrent Download',
                'verbose_name_plural': 'MusicTorrent Downloads',
                'unique_together': {('user', 'torrent')},
            },
        ),
        migrations.AddField(
            model_name='musictorrent',
            name='downloaders',
            field=models.ManyToManyField(related_name='downloaded_music_torrents', through='torrent.MusicTorrentDownload', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='musictorrent',
            name='release',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='torrents', to='torrent.MusicRelease'),
        ),
        migrations.AddField(
            model_name='musictorrent',
            name='uploader',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='music_uploads', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='MusicReleaseGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('group_type', models.CharField(choices=[('LP', 'LP'), ('EP', 'EP'), ('SN', 'Single')], max_length=2)),
                ('contributors', models.ManyToManyField(related_name='release_groups', through='torrent.MusicContribution', to='torrent.MusicArtist')),
            ],
            options={
                'verbose_name': 'Release Group',
                'verbose_name_plural': 'Release Groups',
            },
        ),
        migrations.AddField(
            model_name='musicrelease',
            name='release_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='releases', to='torrent.MusicReleaseGroup'),
        ),
        migrations.AddField(
            model_name='musiccontribution',
            name='release_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contributions', to='torrent.MusicReleaseGroup'),
        ),
        migrations.AlterUniqueTogether(
            name='musiccontribution',
            unique_together={('artist', 'release_group')},
        ),
    ]
