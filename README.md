# Episodes

This has been forked from https://github.com/guptachetan1997/Episodes , mostly for the purposes of adding user authentication for those wanting to use this as a self-hosted TV tracker on the public Internet.

Requirements:

 * python 2/3
 * django
 * sklearn
 * requests
 * pandas

## Local Settings

Create the file `Episodes/local_settings.py` to hold project-specific settings and sensitive variables like API keys (it's kept out of version control). You should register for a TVDB API key at https://www.thetvdb.com . The `local_settings.py` file should look something like this: 

```py
from .settings import *


# If you have pwgen installed on your machine, you could do something like
# pwgen -sy -r \' 64 1
SECRET_KEY = 'SomeVerySecureSecertKey'

# See
# https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-DATABASES
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'USER': 'episodes',
        'PASSWORD': 'some_secure_db_password',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}

# Replace with your local timezone
TIME_ZONE = 'US/Central'

# Register at
# https://www.thetvdb.com
TVDB_API_KEY = ''
TVDB_USERNAME = ''

# Sometimes also called "account identifier" on TVDB
TVDB_USER_KEY = ''
```

Then, set the `DJANGO_SETTINGS_MODULE` environment variable to `Episodes.local_settings`, e.g.

```
$ export DJANGO_SETTINGS_MODULE=Episodes.local_settings
```

To use clone the production branch, install requirements, run the following terminal commands:

    $ sudo pip3 install -r requirements.txt
    $ python3 manage.py makemigrations
    $ python3 manage.py migrate
    $ python3 manage.py runserver
    
![alt tag](https://raw.githubusercontent.com/guptachetan1997/Episodes/master/1.jpeg)
![alt tag](https://raw.githubusercontent.com/guptachetan1997/Episodes/master/2.jpeg)
![alt tag](https://raw.githubusercontent.com/guptachetan1997/Episodes/master/3.jpeg)
![alt tag](https://raw.githubusercontent.com/guptachetan1997/Episodes/master/4.jpeg)

