#!/bin/bash
# Script para reiniciar o Daphne

echo "Reiniciando Daphne..."
sudo systemctl reset-failed daphne
sudo systemctl start daphne
sleep 3
sudo systemctl status daphne
