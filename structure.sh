#!/bin/bash

# Create principal directories
mkdir -p config
mkdir -p app/{templates,static}
mkdir -p nlp
mkdir -p database
mkdir -p tests
mkdir -p docs

# Crear archivos para mantener la estructura de los directorios
touch config/.gitkeep
touch app/templates/.gitkeep app/static/.gitkeep
touch nlp/.gitkeep
touch database/.gitkeep
touch tests/.gitkeep
touch docs/.gitkeep
touch .gitignore
touch README.md
touch requirements.txt
touch Dockerfile
touch docker-compose.yml

# Archivo README.md
echo "# Asistente PYMES" >> README.md
echo "Proyecto de asistente virtual para PYMES." >> README.md

# Archivo .gitignore
echo "__pycache__" >> .gitignore

# Mensaje de finalización
echo "Estructura del proyecto creada con éxito."