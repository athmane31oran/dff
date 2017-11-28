from os import path
from urllib import urlretrieve
import re
import time

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
######################
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
######################


from .webdrivers import init_driver
from .helpers import get_fb_id_from_url, get_user_link, join_or_make


def get_profile_url(driver, page='home'):
    """ 
    Permet de recuperer l'url vers la section amis FB
    Args: driver = l'instance du browser
    Return l'url 
    """
    
    return driver.find_element_by_css_selector('div[data-click="profile_icon"] > a') \
        .get_attribute('href')


def get_profile_name(driver, page='home'):
    """ 
    Permet de recuperer l'url vers la section amis FB
    Args: driver = l'instance du browser
    Return l'url 
    """
    
    if page == 'home':
        return driver.find_element_by_css_selector('#userNav li > a') \
            .get_attribute('title')
    elif page == 'profile':
        return driver.find_element_by_css_selector('#fb-timeline-cover-name > a') \
            .text


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
            pass
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


def get_friends(driver, friends_section_url, friends_section='all'):     
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

    #Perhaps the problem came from the selector, try another one
    #friends_selector = 'div[data-testid="friend_list_item"][data-pnref="%s"]' % friends_section
    friends_selector = 'div[data-pnref="%s"]' % friends_section

    next_section = None
    old_height = -1
    height = get_page_height(driver)
    #print('heights:', old_height, height)
    try:
        # Scroll down to show all friends
        #while next_section is None and old_height < height:

        while next_section is None and (page_is_loading(body) or old_height < height):
            print('scrolling')
            old_height = height
            #body.send_keys(Keys.SPACE)
            body.send_keys(Keys.END)
            next_section = get_section_next_to_friends_section(body)
            height = get_page_height(driver)
            #
        # Return all friends blocks
        print('Quit while loop!')
        return driver.find_elements_by_css_selector(friends_selector)
    except Exception:
        print("Unhandled error")
        return None

def page_is_loading(driver):
    try:
        loading_img = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "img.img.async_saving")))
        print('Loadin_img:True')
        return True 
    except Exception:
        print('Loadin_img:False')
        return False 
    
    

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
        #This field seems to be inadequate
        #friend_data['meta_text'] = friend.text
        
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


def get_user_about_section_info(driver, friends_section_url):
    """
    Permet d'extraire les blocs HTML contenant la liste des amis
    args:   driver = browser
    Retourne la liste des amis
    """

    if('profile.php' in friends_section_url):
        contact_basic_url = friends_section_url + '&sk=about&section=contact-info'
    else:
        contact_basic_url = friends_section_url + '/about?section=contact-info'
     
    driver.get(contact_basic_url)

    contact_text = driver.find_element_by_id("pagelet_contact").text
    basic_text = driver.find_element_by_id("pagelet_basic").text

    #TODO: extract individual informations one by one

    return contact_text , basic_text

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
    
    if 'profile.php' in friend_url:
        mutual_friend_url = friend_url + '&sk=friends_mutual'
    else:
        mutual_friend_url = friend_url + '/friends_mutual'
        
    mutual_friends_blocs = get_friends(driver, mutual_friend_url, friends_section='mutual')
    if mutual_friends_blocs is None:
        print 'no mutual friends'
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

def get_page_posts(driver):
    """
    BUG : does not work
    """
    #TODO: ajouter une date pour filtrer et limiter les posts 

    #if(driver.current_url != page_url):
    #    driver.get(page_url)

    #css_posts_selector = 'div.userContentWrapper'

    #page_posts = []

    css_posts_selector = 'div[role="article"]'

    timestamp = driver.find_elements_by_css_selector(css_posts_selector)
    
    print(timestamp.text)