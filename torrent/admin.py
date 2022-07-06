from django.contrib import admin

from .models.music import MusicArtist, MusicReleaseGroup, MusicContribution, MusicRelease, MusicTorrent


admin.site.register(MusicArtist)
admin.site.register(MusicReleaseGroup)
admin.site.register(MusicContribution)
admin.site.register(MusicRelease)
admin.site.register(MusicTorrent)
