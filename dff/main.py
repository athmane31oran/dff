import networkx as nx
from matplotlib import pyplot as plt


from os import path
from .webdrivers import init_driver
from .helpers import join_or_make, get_args, get_fb_id_from_url
from .helpers import construct_social_graph, save_photos, save_friends_data
from .helpers import get_user_friends_url, save_user_infos, save_user_infos
from .scrapper import login, get_profile_url, make_friends_data
from .scrapper import get_user_about_section_info, get_user_photos, get_friends
from .scrapper import make_mutual_friends, get_profile_name


if __name__ == '__main__':
    conf = get_args()

    print('init driver')
    # TODO: make all args accessible via dict notation
    driver = init_driver(conf['driver']['name'], conf['driver']['maximized'], 
        conf['driver']['headless'], conf['driver']['surpress_notifications'])

    print('logging to FB account')
    logged_in = login(driver, conf['base_url'], conf['auth']['fb_user'],
        conf['auth']['fb_pass'], conf['user_folder'])

    if(logged_in):
        profile_infos = {}
        profile_infos['profile_name'], profile_url = get_profile_name(driver), get_profile_url(driver)
        profile_infos['profile_url'] = profile_url

        print('Getting About user info')
        profile_infos['contact_info'], profile_infos['basic_info'] = \
            get_user_about_section_info(driver, profile_url)
        save_user_infos(profile_infos, conf['user_folder'])

        print('Getting friends blocks')
        friends_section_url = get_user_friends_url(conf['base_url'], profile_url)
        friends_blocks = get_friends(driver, friends_section_url)

        print('extracting data from friends blocks')
        friends_data = make_friends_data(friends_blocks)
        
        for i, friend_data in enumerate(friends_data):
            if conf['depth'] == 2:    
            # extrait les amis des amis
            # a optimiser en verifiant s'ils sont accessible dans la phase
            # mutual friends, car on peut la voir si les amis sont accessibles
            # Must eliminate duplicant friends in the list
                if 'profile.php' in friend_data['url']:
                    friend_all_url = friend_data['url'] + '&sk=friends_all'
                else:
                    friend_all_url = friend_data['url'] + '/friends_all'
                # check depth if conf['depth'] == 2:
                friend_friends = get_friends(driver, friend_all_url)
                if friend_friends is not None:
                    friends_data[i]['friends'] = make_friends_data(friend_friends)
            friends_data[i]['mutual_friends'] = make_mutual_friends(driver, friend_data['url'])

        print('Saving friends data')
        save_friends_data(friends_data, conf['user_folder'])

        #Mis en commentaire pour gagner du temps d'execution

        #print('Download friends photos')
        #save_photos(friends_data, join_or_make(conf['user_folder'], 'friends_photos'), 
        #    suffix='.thumb')

        #print('Getting photos available on photos section')
        #photos = get_user_photos(driver)
        #save_photos(photos, join_or_make(conf['user_folder'], 'photos'))
        
        print('constructing the social graph of the account')
        friends_graph = construct_social_graph(conf['auth']['fb_user'], friends_data)
        print(nx.info(friends_graph))
        
        plt.figure(3, figsize=(15, 10)) 
        plt.title('Graphe des amis')
        labels = {}
        labels[profile_infos['profile_id']]=profile_infos['profile_name']
        for f in friends_data:
            labels[f['id']] = f['name']
            if 'friends' in f :
                for ff in f['friends']:
                    labels[ff['id']] = ff['name']
        
        #TODO: Add attributes to the nodes, to be saved on gexf file 
        nx.write_gexf(friends_graph,\
            path.join(conf['user_folder'],profile_infos['profile_name']+".gexf"))

        nx.draw(friends_graph, labels=labels, with_labels=True, node_size=250)
        #nx.draw_circular(friends_graph, labels=labels, with_labels=True)
        # only on terminal
        plt.show()
    else:
        print "Couldn't login"
