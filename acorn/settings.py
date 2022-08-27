import sys

# Enable tests to run in parallel on macOS
if "test" in sys.argv[1:] and sys.platform == "darwin":
    import multiprocessing

    RED = "\033[0;31m"
    NO_COLOUR = "\033[0m"

    # https://bugs.python.org/issue33725
    print(
        f'{RED}WARNING: Using `multiprocessing.set_start_method("fork")` for testing.'
    )
    print(
        f"This may or may not cause issues with system libraries crashing!{NO_COLOUR}\n"
    )
    multiprocessing.set_start_method("fork")

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "+n)-eo9&gxu&_-n=r5e0eq_c4guo8wtit#5fl^n9y*w$z2wnvz"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

INTERNAL_IPS = ["127.0.0.1", "192.168.1.110"]
ALLOWED_HOSTS = ["127.0.0.1", "192.168.1.101"]

# Custom User Model
AUTH_USER_MODEL = "account.User"

# Custom login URL
LOGIN_URL = "account:signin"

# Redirect after login if no 'next' parameter
LOGIN_REDIRECT_URL = "/"

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = (
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
)

# Application definition
INSTALLED_APPS = (
    # Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    # REST
    "rest_framework",
    # Development/debugging
    "debug_toolbar",
    # SQL tree structure library
    "mptt",
    # Acorn apps
    "account.apps.AccountConfig",
    "api.apps.ApiConfig",
    "debug.apps.DebugConfig",
    "forum.apps.ForumConfig",
    "inbox.apps.InboxConfig",
    "root.apps.RootConfig",
    "search.apps.SearchConfig",
    "torrent.apps.TorrentConfig",
    "tracker.apps.TrackerConfig",
    # Must be last
    "django.forms",
)

MIDDLEWARE = (
    # Debug Toolbar Must be first
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "global_login_required.GlobalLoginRequiredMiddleware",
)

ROOT_URLCONF = "acorn.urls"

TEMPLATES = (
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
)

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

WSGI_APPLICATION = "acorn.wsgi.application"

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/
LANGUAGE_CODE = "en-gb"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = False  # Enforce logical date-time formatting
USE_TZ = True

# Date and time display
DATE_FORMAT = "Y-m-d"
SHORT_DATE_FORMAT = "Y-m-d"
TIME_FORMAT = "H:i:s"
DATETIME_FORMAT = "Y-m-d H:i:s"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/
STATIC_ROOT = ""
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static", "")]

# User-uploaded files
MEDIA_ROOT = os.path.join(BASE_DIR, "media", "")
MEDIA_URL = "/media/"

# Restframework-specific configuration
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.DjangoModelPermissions"]
}
