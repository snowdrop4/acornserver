rm db.sqlite3
rm -rf root/migrations
rm -rf account/migrations
rm -rf torrent/migrations
rm -rf search/migrations
rm -rf tracker/migrations
rm -rf forum/migrations

python3 manage.py makemigrations --no-header root
python3 manage.py makemigrations --no-header account
python3 manage.py makemigrations --no-header torrent
python3 manage.py makemigrations --no-header search
python3 manage.py makemigrations --no-header tracker
python3 manage.py makemigrations --no-header forum
python3 manage.py makemigrations --no-header
python3 manage.py migrate

python3 manage.py createsuperuser
