<h1 align="center" style="border-bottom: none">
    <div>
        API Regate Num Data Etat
    </div>
</h1>

<p align="center">
    Gestion des API nocode pour le projet Regate Num Data Etat<br/>
</p>

<div align="center">
 
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-green.svg)](https://conventionalcommits.org)
[![Python version](https://img.shields.io/badge/python-3.9.9-blue)](https://www.python.org/downloads/release/python-399/)
[![Flask version](https://img.shields.io/badge/Flask-2.1.3-blue)](https://flask.palletsprojects.com/en/2.1.x/)
[![Postgresql version](https://img.shields.io/badge/Postgresql-informational)](https://www.postgresql.org/)
[![Docker build](https://img.shields.io/badge/docker-automated-informational)](https://docs.docker.com/compose/)

</div>


# Description

Ce projet contient une suite d'API REST développées avec Flask-RESTx et Python 3.9. 
Ces API permettent de gérer des utilisateurs Keycloak, en les activant ou en les désactivant. 
Elles permettent également d'interroger des outils nocode tels que NocoDb et d'intégrer les fichiers 
Chorus de l'état pour recouper les données.


# Fichier de configuration

Copier le fichier [config_template.yml](./config/config_template.yml) en config.yml.
```
cp config/config_template.yml config/config.yml
```

Remplacer les variables

| Nom de la variable                                                           |                                     	Description                                      |  
|:-----------------------------------------------------------------------------|:-------------------------------------------------------------------------------------:| 
| DEBUG	                                                                       |                           Active ou désactive le mode debug                           |
| SQLALCHEMY_DATABASE_URI                                                      |                   	URL de connexion à la base de données PostgreSQL                   |
| CELERY_BROKER_URL                                                            |                           	URL du broker Redis pour Celery                            |
| result_backend	                                                              | URL de connexion à la base de données PostgreSQL pour stocker les résultats de Celery |
| api_siren |                                  	URL de l'API SIREN                                  |                                              
| UPLOAD_FOLDER	|            Dossier où sont stockés les fichiers envoyés par l'utilisateur             |
| KEYCLOAK_ADMIN_URL|                         	URL de l'administration de Keycloak                          |                      
| KEYCLOAK_ADMIN_SECRET_KEY	|                     Clé secrète pour l'administration de Keycloak                     |
| KEYCLOAK_ADMIN_REALM|                                  	Realm de Keycloak                                   |
| SECRET_KEY                                                                   |                          	Clé secrète utilisée par keycloak                           
| NOCODB_URL	|                                     URL de NocoDB                                     |                                              
| NOCODB_PROJECT|              	Liste des projets de NocoDB à utiliser  avec le token api               |               



# Installation



## Mode Api

```
python ./manage.py runserver
```

# Utilisation

## UserManagement

Pour utiliser ces API, vous pouvez utiliser un outil de test d'API comme Postman ou Insomnia. Voici les différentes routes disponibles :

* `GET /users` : Récupère la liste de tous les utilisateurs avec des informations de pagination
PATCH /users/disable/<uuid> : Désactive un utilisateur avec l'ID spécifié
* `PATCH /users/disable/<uuid>` : Désactive un utilisateur avec l'ID spécifié
* * `PATCH /users/enable/<uuid>` : Active un utilisateur avec l'ID spécifié


### Mode Api

```
python ./manage.py runserver
```

### Mode Worker

