#!/bin/bash

NAME="sistema_eleicoes"                              # Nome da sua aplicação
DJANGODIR=/home/ubuntu/sistema_eleicoes              # O caminho absoluto para a raiz do seu projeto Django
SOCKFILE=/home/ubuntu/sistema_eleicoes/run/gunicorn.sock  # Onde o socket do Gunicorn será criado
USER=ubuntu                                   # O usuário que vai rodar o Gunicorn (geralmente 'ubuntu' na AMI Ubuntu)
GROUP=ubuntu                                  # O grupo do usuário
NUM_WORKERS=3                                 # Número de workers do Gunicorn (ajuste conforme a CPU)
DJANGO_SETTINGS_MODULE=sistema_fidelizacao.settings     # Caminho para seu settings.py (ex: meuapp.settings)
DJANGO_WSGI_MODULE=sistema_fidelizacao.wsgi             # Caminho para seu wsgi.py (ex: meuapp.wsgi)

echo "Iniciando $NAME como `whoami`"

# Ativa o ambiente virtual
cd $DJANGODIR
source .venv/bin/activate

# Cria o diretório de runtime se não existir
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Inicia o Gunicorn
exec .venv/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --bind=unix:$SOCKFILE \
  --log-level=debug \
  --log-file=/var/log/gunicorn/gunicorn_sistema_eleicoes.log # Envia logs para stdout/stderr para systemd capturar
