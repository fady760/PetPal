# Rapport de Déploiement - PetPal

## 1. Architecture
L'application PetPal est une application web FastAPI (Python) connectée à une base de données MySQL. 
L'ensemble est orchestré via Docker Compose :
- **Service Web** : Construit à partir du Dockerfile (image python:3.11-slim), tourne avec un utilisateur non-root et expose le port 8000. Il inclut un `HEALTHCHECK` sur la route `/health`.
- **Service Base de données** : MySQL 8.0. Le port 3306 n'est pas publié à l'extérieur (sécurité). Les données sont persistées via un volume Docker (`mysql_data`). Le démarrage de l'application est conditionné à la santé de la base (`service_healthy`).

## 2. Version mise en service
- **Version déployée** : `v1.0.0`
- **Image Docker** : L'image a été construite une seule fois, taguée `petpal:v1.0.0`, et publiée. Lors du déploiement, l'image n'est jamais reconstruite, elle est simplement instanciée.

## 3. Déroulé du retour arrière (Rollback)
En cas de problème avec une nouvelle version (par exemple `v1.0.1`), voici la procédure de retour arrière :
1. Arrêt des conteneurs actuels : `docker compose down`
2. Modification du tag de l'image vers la version stable précédente : `docker tag petpal:v1.0.0 fady760/petpal:current`
3. Redémarrage des conteneurs : `docker compose up -d`
4. Vérification de la santé de l'application : `curl http://localhost:8000/health` (doit retourner "healthy").