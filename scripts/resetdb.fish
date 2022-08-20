#!/usr/bin/env fish

set root (dirname (status --current-filename))/..

rm $root/db.sqlite3
rm -rf $root/account/migrations
rm -rf $root/api/migrations
rm -rf $root/debug/migrations
rm -rf $root/forum/migrations
rm -rf $root/inbox/migrations
rm -rf $root/root/migrations
rm -rf $root/search/migrations
rm -rf $root/torrent/migrations
rm -rf $root/tracker/migrations

poetry run python3 $root/manage.py makemigrations --no-header account
poetry run python3 $root/manage.py makemigrations --no-header api
poetry run python3 $root/manage.py makemigrations --no-header debug
poetry run python3 $root/manage.py makemigrations --no-header forum
poetry run python3 $root/manage.py makemigrations --no-header inbox
poetry run python3 $root/manage.py makemigrations --no-header root
poetry run python3 $root/manage.py makemigrations --no-header search
poetry run python3 $root/manage.py makemigrations --no-header torrent
poetry run python3 $root/manage.py makemigrations --no-header tracker

poetry run python3 $root/manage.py makemigrations --no-header
poetry run python3 $root/manage.py migrate

poetry run python3 $root/manage.py createsuperuser
