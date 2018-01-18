rm -r migrations
rm data-dev.sqlite
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
python manage.py runserver