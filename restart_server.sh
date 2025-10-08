#!/bin/bash
echo "Parando servidor Daphne..."
pkill -f daphne
sleep 2
echo "Iniciando servidor Daphne..."
nohup /srv/sisvot/.venv/bin/daphne -b 0.0.0.0 -p 8000 sistema_fidelizacao.asgi:application > /srv/sisvot/daphne.log 2>&1 &
echo "Servidor reiniciado!"


