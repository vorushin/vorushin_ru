from fabric.api import *

env.hosts = ['root@linodeserver.com']

PROJECT_NAME = 'vorushin_ru'
PROJECT_DIR = '/srv/code/' + PROJECT_NAME


def run_in_virtualenv(command):
    run('source /srv/.virtualenvs/%s/bin/activate && %s' %
        (PROJECT_NAME, command))


def deploy():
    with cd(PROJECT_DIR):
        run('hg update')
        run_in_virtualenv('pip install -r requirements.txt')
        run_in_virtualenv('./manage.py syncdb')
        run_in_virtualenv('./manage.py migrate')
        run_in_virtualenv('./manage.py clear_cache')
        run('restart ' + PROJECT_NAME)


def fetch_data():
    with cd(PROJECT_DIR):
        run_in_virtualenv('./manage.py dumpdata --indent 4 '
                          '--exclude contenttypes > data.json')
    get(PROJECT_DIR + '/data.json', 'data.json')
    local('./manage.py flush --noinput')
    local('./manage.py loaddata data.json --noinput')
