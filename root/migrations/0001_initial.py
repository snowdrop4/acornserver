from django.db import models, migrations

import markupfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NewsArticle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('content', markupfield.fields.MarkupField(default='', rendered_field=True)),
                ('content_markup_type', models.CharField(choices=[('', '--'), ('html', 'HTML'), ('plain', 'Plain'), ('markdown', 'Markdown')], default='markdown', editable=False, max_length=30)),
                ('mod_date', models.DateTimeField(auto_now=True)),
                ('_content_rendered', models.TextField(default='', editable=False)),
                ('pub_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
