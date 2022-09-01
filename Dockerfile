FROM python:3.11-rc-bullseye

# Stops the CMD step hanging for some reason
ENV PYTHONUNBUFFERED=1

# All other commands will be relative to this path
WORKDIR /usr/src/acornserver

# Copy everything over to our WORKDIR
COPY . .

# Install poetry from pip as a root user (keeps things simple)
RUN pip3 install poetry

# Switch to a non-root user for the rest of the setup
RUN groupadd -r acorn && useradd -m -r -g acorn acorn
USER acorn

RUN poetry install --no-interaction --no-root
RUN poetry run python3 manage.py makemigrations --noinput

EXPOSE 8000

# TODO: Run actual production webserver here
CMD poetry run python3 manage.py migrate --noinput; poetry run python3 manage.py runserver 0.0.0.0:8000
