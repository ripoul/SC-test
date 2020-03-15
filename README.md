<h1 align="center">Welcome to SC-test 👋</h1>

![Python application](https://github.com/ripoul/SC-test/workflows/Python%20application/badge.svg)
[![codecov](https://codecov.io/gh/ripoul/SC-test/branch/master/graph/badge.svg)](https://codecov.io/gh/ripoul/SC-test)

Le principe du test est de faire un sous-ensemble d'une plateforme de réservation de ressources, ce qui fait partie de notre quotidien.
Une ressource est composée d'un libellé, d'un type de ressource, d'une localisation et d'une capacité (nombre de personnes).
Une réservation est composée d'un titre, d'une date de début et d'une date de fin. 

Le test est composé de plusieurs niveaux: le premier est obligatoire et déjà bien complet, les suivants sont optionnels et (beaucoup?) plus complexes, pour ceux qui aiment les gros défis.
Chaque niveau inclut les règles de base et les demandes des niveaux précédents. 

Côté technique, ce projet est à faire en Python 3.6 (https://www.python.org/) à l'aide du framework Django (https://www.djangoproject.com/) dans sa dernière version (2.2.9).
La partie front niveau 2 doit se faire si possible via la bibliothèque React (https://reactjs.org/).
Le projet doit contenir un fichier requirements.txt qui liste les dépendances Python, et doit être utilisable via un virtualenv (https://python-guide-pt-br.readthedocs.io/fr/latest/dev/virtualenvs.html).
Enfin, le projet doit être versionné avec Git, et hébergé sur un dépôt comme GitHub, Gitlab, ou encore Bitbucket. 

# Configurations

## Installation de l'application

```
pip install -r requirements.txt
python manage.py migrate
python manage.py data
python manage.py compilemessages
python manage.py createcachetable
python manage.py collectstatic
python tornado_main.py
```

Pour tester l'application vous pouvez lancer les tests unitaire `python manage.py test` ou lancer l'application et se 
connecter en tant que `admin:admin` ou `user:user` ou avec votre compte github si vous avez set `SOCIAL_AUTH_GITHUB_KEY` et `SOCIAL_AUTH_GITHUB_SECRET` dans vos variable d'environnement ou dans un fichier `.env` à la racine du projet. L'url de connection est `/booking/login/`.

## Docker

```
docker build -t sc-test .
docker run -p 8888:8888 sc-test
```

## requierements par niveau
Voici le contenu des fichiers requirements.txt par niveau, en récapitulatif.

Niveau 1: 

- Django<3

Niveau 2: 

- Django<3
- social-auth-app-django 
- djangorestframework 

Niveau 3: 

- Django<3
- social-auth-app-django 
- djangorestframework 
- tornado

# Règles
## Règles de base 

- Il ne faut pas perdre trop de temps avec la partie CSS. Un style minimaliste mais élégant suffit. 
- Il n'est pas nécessaire d'utiliser d'autres bibliothèques que celles mentionnées. 
- Commenter le code, préciser si des améliorations sont possibles, respecter les best practices Python (PEP8). 
- Garantir la sécurité de la plateforme (ne pas laisser de grosses failles), comme utiliser les formulaires Django. 
- Garantir la performance du service: utiliser du cache. 
- Les tests unitaires sont optionnels mais bienvenus. 

### Niveau 1 – MVP

1. Fonctionnalités 
- Permettre à un administrateur de déclarer des ressources, associées à un type de ressource. 
- Permettre à un utilisateur de réserver une ressource sur un créneau. 
- Voir la liste des réservations passés, en cours et à venir. 
- Permettre à un utilisateur d'annuler une réservation en cours ou à venir. 
- Permettre à un utilisateur de modifier une réservation à venir  

2. Technique 

- Mise en place d'une authentification simple. 
- Les interactions côté JS avec le serveur doivent se faire en asynchrone, via appels AJAX. 
- Gérer les timezones: les dates doivent être affichées en fonction de la timezone de l'utilisateur (stockée dans le profil de l'utilisateur). 
- Gérer la traduction: Français/Anglais. 
- Simple gestion des droits: un utilisateur ne voit et n'interagit qu'avec ses réservations, un administrateur peut tout voir et tout faire. 

### Niveau 2 – Filtre, calendrier, OAuth et API REST (hard)

1. Fonctionnalités 

- Filtrer les ressources par type et par localisation sur le formulaire de réservation. 
- Tous les utilisateurs voient les réservations de la plateforme sur un calendrier. 

2. Technique 

- Ajout d'une authentification par OAuth, via Python Social Auth (https://github.com/python-social-auth/social-app-django) 
- L'accès au service doit se faire via une API REST, en utilisant Django REST Framework (http://www.django-rest-framework.org/). 
- Le composant React de calendrier peut être react-big-calendar (http://intljusticemission.github.io/react-big-calendar/examples/index.html) 

### Niveau 3 – Temps réel et Docker (encore plus hard)

1. Fonctionnalités 

- Les réservations sont rechargées en temps réel quand une réservation est ajoutée. 

2. Technique 

- Les interactions en temps réel doivent se faire via le protocole WebSocket en utilisant le framework Tornado (http://www.tornadoweb.org/en/stable/). Il faut trouver le moyen de faire communiquer Django et Tornado. 
- Intégration Docker (https://www.docker.com/): proposer un fichier docker-compose.yml pour démarrer l'application. 
