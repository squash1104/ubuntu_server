from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("user_profiles", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                """
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_schema = 'public' AND table_name = 'chat_message'
                    ) THEN
                        DROP TABLE public.chat_message CASCADE;
                    END IF;

                    IF EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_schema = 'public' AND table_name = 'chat_profile'
                    ) THEN
                        DROP TABLE public.chat_profile CASCADE;
                    END IF;
                END$$;
                """
            ),
            reverse_sql="SELECT 1;",
        )
    ]




