import django.contrib.postgres.operations
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = []

    operations = [
        django.contrib.postgres.operations.UnaccentExtension(),
        migrations.RunSQL("CREATE TEXT SEARCH CONFIGURATION en ( COPY = english )"),
        migrations.RunSQL("CREATE TEXT SEARCH CONFIGURATION es ( COPY = spanish )"),
        migrations.RunSQL(
            "ALTER TEXT SEARCH CONFIGURATION en ALTER MAPPING FOR hword, hword_part, word WITH unaccent, english_stem"
        ),
        migrations.RunSQL(
            "ALTER TEXT SEARCH CONFIGURATION es ALTER MAPPING FOR hword, hword_part, word WITH unaccent, spanish_stem"
        ),
    ]
