from fabric.api import *

env.hosts = ['root@linodeserver.com']

PROJECT_NAME = 'vorushin_ru'
PROJECT_DIR = '/srv/code/' + PROJECT_NAME


def run_in_virtualenv(command):
    run('source /srv/.virtualenvs/%s/bin/activate && %s' %
        (PROJECT_NAME, command))


def deploy():
    with cd(PROJECT_DIR):
        run('git pull')
        run_in_virtualenv('pip install -r requirements.txt')
        run_in_virtualenv('./manage.py syncdb')
        run_in_virtualenv('./manage.py migrate')
        run_in_virtualenv('./manage.py clear_cache')
        run('restart ' + PROJECT_NAME)


import settings
db_settings = settings.DATABASES['default']


def fetch_db():
    with cd(PROJECT_DIR):
        run('mysqldump %(NAME)s -u %(BACKUP_USER)s -p%(BACKUP_PASSWORD)s '
            '--skip-lock-tables > dump.sql' % db_settings)
        get('dump.sql', 'dump.sql')
    local('./manage.py flush --noinput')
    local('./manage.py dbshell < dump.sql')
