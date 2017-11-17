from .webdrivers import init_driver
from .helpers import join_or_make, get_args, get_fb_id_from_url
from .helpers import construct_social_graph, save_photos, save_friends_data
from .scrapper import login, get_friends_section_url, make_friends_data
from .scrapper import get_user_about_section_info, get_user_photos, get_friends



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
        friends_section_url = get_friends_section_url(driver, conf['base_url'])
        print('Getting friends blocks')
        friends_blocks = get_friends(driver, friends_section_url)

        print('extracting data from friends blocks')
        friends_data = make_friends_data(friends_blocks)

        print('Saving friends data')
        save_friends_data(friends_data, conf['user_folder'])

        print('Download friends photos')
        save_photos(friends_data, join_or_make(conf['user_folder'], 'friends_photos'), 
            suffix='.thumb')

        print('constructing the social graph of the account')
        print(construct_social_graph(conf['auth']['fb_user'], friends_data))

        print('Getting About user info')
        print(get_user_about_section_info(driver))

        photos = get_user_photos(driver)

        print('Getting photos available on photos section')
        save_photos(photos, join_or_make(conf['user_folder'], 'photos'))
    else:
        print "Couldn't login"
