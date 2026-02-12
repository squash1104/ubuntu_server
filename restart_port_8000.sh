#!/bin/bash
echo "Parando serviço na porta 8000..."
pkill -f "manage.py runserver" 2>/dev/null
sleep 1
echo "Iniciando servidor..."
nohup /srv/sisvot/.venv/bin/python /srv/sisvot/manage.py runserver 0.0.0.0:8000 > /srv/sisvot/runserver.log 2>&1 &
sleep 2
echo "Servidor iniciado!"
tail -5 /srv/sisvot/runserver.log
