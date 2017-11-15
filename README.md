# DFF
Scraping Facebook pour extraire les donnees dun compte
Le code a été testé sous ubuntu 16


# Dépendances

Python: 2.7+

Executer la commande suivante pour installer les dependances
```
pip install -r requirements.txt
```
Telecharger [chromeDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads)
et le copier dans le dossier `/usr/bin`

# Configuration

Créer une copie du fichier de config founi en exemple
```
cp config.example.yml config.yml
```

Ajouter les informations de conenxion au compte facebook

```yaml
auth:
    fb_user: 'foulan.foulani'
    fb_pass: 'password'
```