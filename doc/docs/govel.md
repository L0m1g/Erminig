# Govel

[//]: <> (TODO Parler de la création de l'utilisateur pak)

Govel est la forge d'Erminig. C'est ici que vous allez créer, mettre à jour les fichiers de build des différents paquets de la distribution.

Vous avez 4 cas de figures pris en compte :

#### Dev

Le développement d'une nouvelle distribution à partir d'une distribution hôte ;

|                          | Valeur                             |
|--------------------------|------------------------------------|
| Utilisateur              | pak                                |
| Répertoire de travail    | `/home/pak/erminig`                |
| Fichier de log           | `/home/pak/.local/share/govel.log` |
| Fichier de configuration | `/home/pak/.config/erminig.conf`   |

#### Global

Le maintien de la distribution existante ;

|                          | Valeur                             |
|--------------------------|------------------------------------|
| Utilisateur              | pak                                |
| Répertoire de travail    | `/var/lib/erminig`                 |
| Fichier de log           | `/var/log/govel.log`               |
| Fichier de configuration | `/etc/erminig.conf`                |

#### Local

La création de paquets destinés à uniquement la machine actuelle ;

|                          | Valeur                                 |
|--------------------------|----------------------------------------|
| Utilisateur              | pak                                    |
| Répertoire de travail    | `/usr/local/lib/erminig`               |
| Fichier de log           | `/usr/local/share/erminig/govel.log`   |
| Fichier de configuration | `/usr/local/share/erminig/erminig.conf`|

#### Utilisateur

La création de paquets pour seulement un utilisateur.

|                          | Valeur                                   |
|--------------------------|------------------------------------------|
| Utilisateur              | `$USER`                                  |
| Répertoire de travail    | `$HOME/.local/lib/erminig`               |
| Fichier de log           | `$HOME/.local/share/erminig/govel.log`   |
| Fichier de configuration | `$HOME/.config/erminig.conf`             |

## Utilisation

```text
Govel

Forge of Erminig

Usage:
govel init [--dev | --root | --user] [-v] [--path PATH]
govel --version

Options:
-h --help            show this help message and exit
--version            show version and exit
-v --verbose
```

### Initialisation de Govel

```
# développement d'une nouvelle distribution
govel init --dev
# Création de paquets pour la machine
govel init --root
# Création de paquets pour l'utilisateur
govel init --user
```
Il n'y a pas besoin de créer les repertoires pour le maintien de la distribution, ils existent déjà

### Choix du répertoire de travail

Bien que des répertoire soient définis par défaut, vous pouvez également décider de ne pas utiliser ces emplacements et en choiser d'autres.
Dans ce cas il suffit d'utiliser l'option `--path`

```
govel init --user --path /home/Documents/erminig
```

Ce répertoire sera défini dans le fichier de configuration. Ce changement n'affecte que l'espace de travail et aucunement les fichiers de logs et de configuration.
Ce répertoire de travail doit etre défini de façon absolue.

### Création de l'utilisateur pak

Il est créé automatiquement avec un dossier `/home/pak` dédié sauf si vous n'utiliser que pour les besoins de l'utilisateur courant. Cet utilisateur a des paramètres dédiés au niveau de son environnement qui garantissent une homogénéité au niveau des compilations.

## Création d'une nouvelle distribution

```
sudo govel init --dev
sudo govel new --name mojenn
```