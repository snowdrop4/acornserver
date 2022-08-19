import django.db.models.deletion
from django.db import models, migrations
from django.conf import settings

import mptt.fields
import markupfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ForumCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('folder', models.BooleanField()),
                ('thread_count', models.IntegerField(default=0)),
                ('post_count', models.IntegerField(default=0)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='ForumThread',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', markupfield.fields.MarkupField(rendered_field=True)),
                ('body_markup_type', models.CharField(choices=[('', '--'), ('html', 'HTML'), ('plain', 'Plain'), ('markdown', 'Markdown')], default='markdown', editable=False, max_length=30)),
                ('datetime', models.DateTimeField()),
                ('_body_rendered', models.TextField(editable=False)),
                ('post_number', models.IntegerField()),
                ('title', models.CharField(max_length=256)),
                ('post_count', models.IntegerField(default=1)),
                ('latest_post_datetime', models.DateTimeField(blank=True, null=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='forum_threads', to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='threads', to='forum.ForumCategory')),
                ('latest_post_author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Thread',
                'verbose_name_plural': 'Threads',
            },
        ),
        migrations.CreateModel(
            name='ForumPost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', markupfield.fields.MarkupField(rendered_field=True)),
                ('body_markup_type', models.CharField(choices=[('', '--'), ('html', 'HTML'), ('plain', 'Plain'), ('markdown', 'Markdown')], default='markdown', editable=False, max_length=30)),
                ('datetime', models.DateTimeField()),
                ('_body_rendered', models.TextField(editable=False)),
                ('post_number', models.IntegerField()),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='forum_posts', to=settings.AUTH_USER_MODEL)),
                ('thread', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='forum.ForumThread')),
            ],
            options={
                'verbose_name': 'Post',
                'verbose_name_plural': 'Posts',
            },
        ),
        migrations.AddField(
            model_name='forumcategory',
            name='latest_post_thread',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='forum.ForumThread'),
        ),
        migrations.AddField(
            model_name='forumcategory',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='forum.ForumCategory'),
        ),
    ]
