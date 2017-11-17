import argparse
from os import path, makedirs
from urllib import urlretrieve
import re

import yaml
import pandas as pd
import networkx as nx


def join_or_make(*args):
    """
    Joins a folder and creates it if it doesn't exist
    Return: string joined folder
    """
    folder = path.join(*args)
    if not path.exists(folder):
        makedirs(folder)
    return folder


def get_args(context='terminal'):
    """
        Parse les arguments passes par la ligne de commande et charge le fichier 
            de config
        Return: object les arguments passes
    """
    if context == 'terminal':
        parser = argparse.ArgumentParser()
        parser.add_argument("--config_file", default='config.yml', help="Fichier de config")
        args = parser.parse_args()
        config_file = args.config_file
        # TODO: should be changed if we need more params from terminal
    else:
        config_file = context

    with open(config_file) as f:
        config = yaml.safe_load(f)

    config['user_folder'] = join_or_make(config['data_path'], config['auth']['fb_user'])

    return config


def get_fb_id_from_url(url):
    """ 
    Permet d'extraire l'identificateur d'un utilisateur d'une url 
        (username/id) et specifie son type
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


def get_user_link(url):
    """ Gets user url from a link """
    splits = url.split('?')
    newUrl = splits[0]
    if len(splits) == 1:
        return newUrl
    
    m = re.search('id=[0-9]+', splits[1])
    if m:
        return newUrl + '?' + m.group(0)
    return newUrl


def save_photos(data, dest_path, suffix=''):
    """ 
    Permet d enregistrer la photo thumbnail des amis
    args:  friends = la liste des blocs html des amis
    """

    for item in data:
        img_src = item['img_url']        
        urlretrieve(img_src, path.join(dest_path, item['id'] + suffix + ".jpg"))


def save_friends_data(friends_data, dest_path):
    """ 
    Construit un DataFrame et enregistre les donnees en csv
    Args:   list friends_data = liste des donnees des amis
            string dest_path = dossier destination
    Return DataFrame donnees des amis
    """
    df = pd.DataFrame(friends_data)    
    df.to_csv(path.join(dest_path, 'friends.csv'), encoding='utf-8')
    return df


def construct_social_graph(user_id, friends_data):
    # Create empty graph
    G = nx.Graph()
    # le noeud correspondant au compte traite
    G.add_node(user_id)
    for friend in friends_data:
        G.add_node(friend['id'])
        G.add_edge(user_id, friend['id'])
    
    for friend in friends_data:
        for mutual_friend in friend['mutual_friends']:
            G.add_edge(friend['id'], mutual_friend)
    return G
