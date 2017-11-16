from .helpers import get_fb_id_from_url


def get_friends_section_url(driver, base_url):
    """ 
    Permet de recuperer l'url vers la section amis FB
    Args: driver = l'instance du browser
    Return l'url 
    """
    
    profile_url = driver.find_element_by_css_selector('[title="Profile"]').get_attribute('href')
    user_id, id_type = get_fb_id_from_url(profile_url)    
   
    if id_type == 'username':
        user_friends_url = profile_url+'/friends'
    else:
        user_friends_url = '%sprofile.php?id=%s&sk=friends' % (base_url, user_id)
        
    return user_friends_url


def get_section_next_to_friends_section(driver):
    selectors = ['#pagelet_timeline_medley_music', '#pagelet_timeline_medley_books', 
                '#pagelet_timeline_medley_photos', '#pagelet_timeline_medley_videos']
    for selector in selectors:
        try:
            return driver.find_element_by_css_selector(selector)
        except Exception:
            return None