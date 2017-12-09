from os import path

from ..fburl import FB_URL
from ..helpers import join_or_make
from .base import PageScrapper


class HomePage(PageScrapper):
  def __init__(self, driver, screenshot_config, configpath, *args, **kwargs):
    kwargs['screenshot'] = screenshot_config
    super(HomePage, self).__init__(driver, configpath, *args, **kwargs)

    self.url = FB_URL.BASE_URL

    scrs_path = join_or_make(self.config['screenshot']['path'])
    scrs_filepath = self.config['screenshot']['filename']
    self.config['screenshot']['filepath'] = path.join(scrs_path, scrs_filepath)

  def validate(self):
    if not self.has_config('selectors.profile', ['name', 'url']):
      return self.config_error(
        ['Home page needs selectors config for profile. Pass them as constructor arguments' + \
          'or in config file.'])
    return True

  def start(self):
    self.goto(self.url)

    profile_url = self.driver.find_element_by_css_selector(
      self.get_config('selectors.profile.url')) \
      .get_attribute('href')

    profile_id_block = self.driver.find_element_by_css_selector(
      self.get_config('selectors.profile.id'))
    profile_id = profile_id_block.get_attribute('data-nav-item-id')
    
    profile_name = profile_id_block.find_element_by_css_selector(
      self.get_config('selectors.profile.name')) \
      .get_attribute('title')

    self.data['profile'] = {
      'url': profile_url,
      'name': profile_name,
      'id': profile_id
    }
    
    id, id_type = FB_URL.fb_id_from_url(self.data['profile']['url'])

    if id_type == 'username':
      self.data['profile']['username'] = id
    else:
      self.data['profile']['username'] = None

    if self.get_config('screenshot.save') == True:
      self.driver.save_screenshot(self.get_config('screenshot.filepath'))
