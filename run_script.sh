#!/bin/bash

# Establecer PATH explícitamente para que cron tenga acceso a los binarios del entorno
export PATH="/home/dbadmin/jupyter_venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Ruta al script y al log
SCRIPT="/home/dbadmin/FINAL_actualizacion_predicciones.py"
LOG="/home/dbadmin/run_script_auto.log"

# Imprimir información útil para depuración
echo "=== $(date) ===" >> "$LOG"
env >> "$LOG"
which python >> "$LOG"

# Ejecutar el script con el Python del entorno virtual
/home/dbadmin/jupyter_venv/bin/python3 "$SCRIPT" >> "$LOG" 2>&1
