#!/bin/bash

# Establecer PATH para cron
export PATH="/home/dbadmin/jupyter_venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Cargar .env de forma segura
set -a
source /home/dbadmin/.env
set +a

# Definir rutas
SCRIPT="/home/dbadmin/FINAL_actualizacion_predicciones.py"
LOG="/home/dbadmin/run_script_auto.log"

# Marcar ejecución (sin mostrar variables sensibles)
echo "=== $(date) ===" >> "$LOG"

# Ejecutar script con entorno cargado
/home/dbadmin/jupyter_venv/bin/python3 "$SCRIPT" >> "$LOG" 2>&1
