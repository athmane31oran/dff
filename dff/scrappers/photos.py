from os import path
import re

from ..fburl import FB_URL
from ..helpers import join_or_make, save_photos

from .base import PageScrapper


class Photos(PageScrapper):
  def __init__(self, driver, profile_url, configpath, save_photos=save_photos, *args, **kwargs):
    super(Photos, self).__init__(driver, configpath, *args, **kwargs)

    self.profile_url = profile_url
    self.url = FB_URL.photos_page(profile_url)
    self.save_photos = save_photos

    if self.get_config('base_path'):
      self.config['path'] = path.join(self.get_config('base_path'), self.get_config('path'))

  def validate(self):
    if not self.has_config('selectors', ['next_section']):
      return self.config_error(
        ['Friends page needs selectors config. Pass them as constructor arguments' + \
          'or in config file.'])

    return True

  def start(self):
    self.goto(self.url)

    self.data['blocks'] = self.get_blocks()

    self.data['photos'] = self.transform_blocks(self.data['blocks'])

    if self.get_config('save'):
      self.save()


  def save(self):
    if self.get_config('download'):
      paths = self.save_photos(self.data['photos'], self.get_config('path'))
      for i, photo in enumerate(self.data['photos']):
        self.data['photos'][i]['img_path'] = paths[i]

  def get_blocks(self):
    try:
      # Scroll down to show all friends
      body = self.driver.find_element_by_css_selector('body')
      self.show_all(body, self.get_config('num_pages'))
      # photos blocks
      return self.driver.find_elements_by_css_selector(self.get_config('selectors.img_link'))
    except Exception as e:
      if self.get_config('debug'):
        print("get_blocks exception:\n" + str(e))
      return []
    
  def transform_blocks(self, blocks):
    photos = []
    selector = self.get_config('selectors.img_i')
    for block in blocks:  
      style = block.find_element_by_css_selector(selector).get_attribute('style')
      res = re.search('url\("(https://.+)"\);$', style)
      if res:
        photos.append({'id': block.get_attribute('id'), 'img_url': res.group(1)})
    return photos