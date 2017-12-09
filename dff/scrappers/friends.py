from os import path

from selenium.webdriver.common.keys import Keys

from ..fburl import FB_URL
from ..helpers import join_or_make, page_is_loading, save_photos
from ..scrapper import get_page_height
from .base import PageScrapper


class Friends(PageScrapper):
  def __init__(self, driver, profile_url, configpath, save_photos=save_photos, *args, **kwargs):
    super(Friends, self).__init__(driver, configpath, *args, **kwargs)

    self.profile_url = profile_url
    self.friends_url = FB_URL.friends_page(profile_url)
    self.mutual_friends_url = FB_URL.friends_page(profile_url, mutual=True)
    self.save_photos = save_photos

    if self.get_config('base_path'):
      self.config['photos']['path'] = path.join(self.get_config('base_path'), self.get_config('photos.path'))

  def validate(self):
    if not self.has_config('selectors', ['next_section']):
      return self.config_error(
        ['Friends page needs selectors config. Pass them as constructor arguments' + \
          'or in config file.'])

    return True

  def start(self):
    if self.get_config('friends.get'):
      self.goto(self.friends_url)
      self.data['friends_blocks'] = self.get_friends()
      self.data['friends'] = self.transform_friends_blocks(self.data['friends_blocks'])

      friends, mutual = self.get_config('friends.get_friends'), self.get_config('friends.get_mutual')
      self.get_friends_friends(friends=friends, mutual=mutual)

    if self.get_config('friends.save'):
      self.save()

  def save(self):
    if self.get_config('friends.download_thumb'):
      paths = self.save_photos(self.data['friends'], self.get_config('photos.path'), suffix='.thumb')
      print 'paths', len(paths)
      for i, friend in enumerate(self.data['friends']):
        self.data['friends'][i]['img_path'] = paths[i]

  def get_friends_friends(self, friends=False, mutual=False):
    if 'friends' not in self.data:
      raise Exception("First find some friends before looking for mutual friends")

    if not friends and not mutual:
      return

    for i, friend in enumerate(self.data['friends']):
      if mutual:
        url = FB_URL.friends_page(friend['url'], mutual=True)
        self.goto(url)
        self.data['friends'][i]['mutual_friends'] = self.get_mutual_friends_ids()
      if friends:
        url = FB_URL.friends_page(friend['url'])
        self.goto(url)
        blocks = self.get_friends()
        print 'friend friends', len(blocks)
        self.data['friends'][i]['friends'] = self.transform_friends_blocks(blocks)

  def get_mutual_friends_ids(self):
    mutual_friends_blocs = self.get_friends(section='mutual')
    if mutual_friends_blocs is None:
      return []

    mutual_friends = []
    for mutual_friend in mutual_friends_blocs:
      img_link = mutual_friend.find_element_by_css_selector('a')
      try:
        img = mutual_friend.find_element_by_css_selector('a > img')
        # si cette instruction ne s'execute pas, cela veut dire
        # que l'utilisateur est desactive
      except Exception as e:
        if self.get_config('debug'):
          print('get_mutual_friends_ids exception:\n' + str(e))
        continue
      id_url = img_link.get_attribute('data-hovercard')
      if id_url is None or len(id_url) < 1:
        continue
      mutual_friend_id, _ = FB_URL.fb_id_from_url(id_url)
      mutual_friends.append(mutual_friend_id)
    
    return mutual_friends
    
  def get_friends(self, section='all'):
    if section == 'all' : 
      friend_selector = self.get_config('selectors.friend')
    else:
      friend_selector = self.get_config('selectors.mutual_friend')

    try:
      # Scroll down to show all friends
      body = self.driver.find_element_by_css_selector('body')
      self.show_all(body, self.get_config('num_pages'))
      # friends blocks
      return self.driver.find_elements_by_css_selector(friend_selector)
    except Exception as e:
      if self.get_config('debug'):
        print("get_friends exception:\n" + str(e))
      return None

  def transform_friends_blocks(self, friends_blocks):
    """ 
    Permet d'extraire les donnees des amis
    args:   list friends_blocks = la liste des blocs html des amis
    Return list les donnees des amis {name, url, img_url, meta_text, id, username}
    """

    if friends_blocks is None: return None

    friends_data = []
    
    for friend in friends_blocks:
      friend_data = {}
      img_link = friend.find_element_by_css_selector(self.get_config('selectors.img_link'))
      try:
        img = friend.find_element_by_css_selector(self.get_config('selectors.deactivated'))
        # si cette instruction ne s'execute pas, cela veut dire
        # que l'utilisateur est desactive
      except Exception as e:
        if self.get_config('debug'):
          print('transform_friends_blocks: deactivated account\n', str(e))
        continue
      
      friend_data['name'] = img.get_attribute('aria-label')
      friend_data['url'] = FB_URL.extrat_profile_url(img_link.get_attribute('href'))
      friend_data['img_url'] = img.get_attribute('src')
      friend_data['meta_text'] = friend.text
      
      try:
        friend_data['id'], _ = FB_URL.fb_id_from_url(
            img_link.get_attribute('data-hovercard'))
      except Exception as e:
        if self.get_config('debug'):
          print('transform_friends_blocks: couldnt get the FB id for:%s\n' % friend_data['url'], str(e))
        continue
      try:
        user_id, id_type = FB_URL.fb_id_from_url(friend_data['url'])
        if id_type == 'username':
          friend_data['username'] = user_id
      except Exception as e:
         if self.get_config('debug'):
           print('transform_friends_blocks: couldnt get username for:%s\n' % friend_data['url'], str(e))
             
      friends_data.append(friend_data)
    
    return friends_data