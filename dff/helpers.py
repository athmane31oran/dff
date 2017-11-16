import argparse
from os import path, makedirs
import urllib
import re

import yaml


def get_args():
    """
        Parse les arguments passes par la ligne de commande et charge le fichier de config
        Return: object les arguments passes
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--config_file", default='config.yml', help="Fichier de config")
    args = parser.parse_args()

    with open(args.config_file) as f:
        args.config = yaml.safe_load(f)

    args.user_folder = args.config['auth']['fb_user']

    return args


def save_friends_thumb(folder, friends_data):
    """ 
    Permet d enregistrer la photo thumbnail des amis
    args:   string folder = dossier pour contenir les donnees de l'utilisqteur
            list friends_data = la liste des blocs html des amis
    """    
    if not path.exists(path.join(folder, 'friends_photos')):
        makedirs(path.join(folder, 'friends_photos'))
        
    for friend_data in friends_data:
        img_src = friend_data['img_url']
        urllib.urlretrieve(img_src, path.join(folder, 'friends_photos/', friend_data['id'] + ".thumb.jpg"))


def get_fb_id_from_url(url):
    """ 
    Permet d'extraire l'identificateur d'un utilisateur d'une url (username/id) et specifie son type
    Args: string url = url d'un utilisateur fb
    Return: string l'id ou le username
    Throws: Exception
    """
    res = re.search('facebook.com/([a-zA-Z0-9\.-]+).*', url)
    if res:
        return res.group(1), 'username'
    res = re.search('id=([0-9]+).*', url)
    if res:
        return res.group(1), 'id'
    
    raise Exception("Couldn't extract FB id from the url: ", url)
