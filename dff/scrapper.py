from os import path
from urllib import urlretrieve
import re

from selenium.webdriver.common.keys import Keys

from .webdrivers import init_driver
from .helpers import get_fb_id_from_url, get_user_link, join_or_make


def get_friends_section_url(driver, base_url):
    """ 
    Permet de recuperer l'url vers la section amis FB
    Args: driver = l'instance du browser
    Return l'url 
    """
    
    profile_url = driver.find_element_by_css_selector('[title="Profile"]') \
        .get_attribute('href')
    user_id, id_type = get_fb_id_from_url(profile_url)    
   
    if id_type == 'username':
        user_friends_url = profile_url + '/friends'
    else:
        user_friends_url = '%sprofile.php?id=%s&sk=friends' % (base_url, user_id)
        
    return user_friends_url


def get_section_next_to_friends_section(driver):
    """
        Selectionne la premiere section qui suit la section amis
        Args: driver = l'instance du browser
        Return Block de section ou None
    """
    selectors = ['#pagelet_timeline_medley_music', '#pagelet_timeline_medley_books', 
                '#pagelet_timeline_medley_photos', '#pagelet_timeline_medley_videos']
    for selector in selectors:
        try:
            return driver.find_element_by_css_selector(selector)
        except Exception:
            return None


def login(driver, base_url, fb_user, fb_pass, dest_path):
    """ 
    Permet de se connecter au compte FB d'un utilisateur 
    Args:   driver = browser, 
            string base_url = url facebook
            string fb_user = username ou email ou telephone
            string fb_pass = password
            string dest_path = dossier de l'utilisateur
    Retourne True en cas de succes sinon False
    """

    screenshots_path = join_or_make(dest_path, 'screnshots/')
    driver.get(base_url)
    try:
        driver.find_element_by_name("email").send_keys(fb_user)
        driver.find_element_by_name("pass").send_keys(fb_pass)
        driver.find_element_by_css_selector('#loginbutton input').click()
        driver.save_screenshot(path.join(screenshots_path, 'home-screenshot.png'))
        return True
    except Exception:
        print("Un probleme de connexion")
        return False


def get_friends(driver, friends_section_url, friends_section='friends_all'):     
    """ 
    Permet d'extraire les blocs HTML contenant la liste des amis
    args:   driver = browser
            string friends_section_url = URL de la page liste d'amis
    Retourne la liste des amis
    """   
    
    # TODO: check if this is actually working
    if(driver.current_url != friends_section_url):
        driver.get(friends_section_url)
    
    body = driver.find_element_by_css_selector('body')

    selector = '[id="pagelet_timeline_medley_friends"] > div div:nth-of-type(2) a[aria-selected="true"]'
    try:
        selected_link = driver.find_element_by_css_selector(selector)
    except Exception:
        return None
    if friends_section not in selected_link.get_attribute('href'):
        return None

    next_section = None
    old_height = -1
    height = get_page_height(driver)
    try:
        # Scroll down to show all friends
        while next_section is None and old_height != height:
            body.send_keys(Keys.END)
            next_section = get_section_next_to_friends_section(driver)
            old_height = height
            height = get_page_height(driver)
        # Return all friends blocks
        return driver.find_elements_by_css_selector('[data-testid="friend_list_item"]')
    except Exception:
        print("Unhandled error")
        return None


def get_page_height(driver):
    script = """
    var body = document.body,
    html = document.documentElement;
    return Math.max( body.scrollHeight, body.offsetHeight, 
        html.clientHeight, html.scrollHeight, html.offsetHeight );
    """
    return driver.execute_script(script)



def make_friends_data(friends_blocks):
    """ 
    Permet d'extraire les donnees des amis
    args:   list friends_blocks = la liste des blocs html des amis
    Return list les donnees des amis {name, url, img_url, meta_text, id, username}
    """

    friends_data = []
    
    for friend in friends_blocks:
        friend_data = {}
        img_link = friend.find_element_by_css_selector('a')
        try:
            img = friend.find_element_by_css_selector('a > img')
            # si cette instruction ne s'execute pas, cela veut dire
            # que l'utilisateur est desactive
        except Exception:
            continue
        
        friend_data['name'] = img.get_attribute('aria-label')        
        friend_data['url'] = get_user_link(img_link.get_attribute('href'))
        friend_data['img_url'] = img.get_attribute('src')
        friend_data['meta_text'] = friend.text
        
        try:
            friend_data['id'], _ = get_fb_id_from_url(
                    img_link.get_attribute('data-hovercard'))
        except Exception:
            print('Warning: couldnt get the FB id for:', friend_data['url'])
            continue
        try:
            user_id, id_type = get_fb_id_from_url(friend_data['url'])
            if id_type == 'username':
                friend_data['username'] = user_id
        except Exception:
            pass
            
        friends_data.append(friend_data)
    
    return friends_data


def get_user_about_section_info(driver):
    """
    Permet d'extraire les blocs HTML contenant la liste des amis
    args:   driver = browser
    Retourne la liste des amis
    """

    about_url = driver.find_element_by_css_selector('[data-tab-key="about"]') \
        .get_attribute('href')        
    driver.get(about_url)

    return driver \
        .find_element_by_css_selector('[data-overviewsection="contact_basic"]') \
        .text


def get_user_photos(driver):
    """ 
    Permet de telecharger les photos d'un utilisateur
    Args:   driver = browser
            string dest_path = dossier de l'utilisateur
    Retourne True en cas de succes sinon False
    """

    photos_section = driver.find_element_by_css_selector('[data-tab-key="photos"]') \
        .get_attribute('href') 
    driver.get(photos_section)
    img_selector = 'a.uiMediaThumb._6i9.uiMediaThumbMedium'
    photos_blocks = driver.find_elements_by_css_selector(img_selector)
    photos = []
    for block in photos_blocks:  
        style = block.find_element_by_css_selector('i.uiMediaThumbImg') \
            .get_attribute('style')
        img_src = re.search('url\("(https://.+)"\);$', style).group(1)
        photos.append({'id': block.get_attribute('id'), 'img_url': img_src})
        
    return photos

def make_mutual_friends(driver, friend_url):
    """"
    Construie la liste des amis en communs
    Args:
        driver : le browser
        url : le lien du compte ami
    Retourne la liste des amis en commun
    """
    
    if('profile.php' in friend_url):
        mutual_friend_url = friend_url + '&sk=friends_mutual'
    else:
        mutual_friend_url = friend_url + '/friends_mutual'
        
    mutual_friends_blocs = get_friends(driver, mutual_friend_url, friends_section='friends_mutual')
    if mutual_friends_blocs is None:
        return []

    mutual_friends = []
    for mutual_friend in mutual_friends_blocs:
        img_link = mutual_friend.find_element_by_css_selector('a')
        try:
            img = mutual_friend.find_element_by_css_selector('a > img')
            # si cette instruction ne s'execute pas, cela veut dire
            # que l'utilisateur est desactive
        except Exception:
            print('exception make_mutual_friends')
            continue
        id_url = img_link.get_attribute('data-hovercard')
        if id_url is None or len(id_url) < 1:
            continue
        mutual_friend_id, _ = get_fb_id_from_url(id_url)
        mutual_friends.append(mutual_friend_id)
    
    return mutual_friends