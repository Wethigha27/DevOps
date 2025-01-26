# Utilise une image de base Python
FROM python:3.11-slim

# Définit le répertoire de travail dans le conteneur
WORKDIR /app

# Copie le fichier requirements.txt
COPY requirements.txt requirements.txt

# Installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le contenu du projet dans le conteneur
COPY . .

# Définit la variable d'environnement pour Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expose le port utilisé par Flask
EXPOSE 5000

# Commande pour démarrer l'application
CMD ["flask", "run"]
