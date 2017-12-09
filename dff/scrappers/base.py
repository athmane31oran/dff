from abc import ABCMeta, abstractmethod

import yaml
from selenium.webdriver.common.keys import Keys

from ..helpers import dict_merge, page_is_loading
from ..scrapper import get_page_height


class ArgumentsException(Exception):
  def __init__(self, error_bag):
    self.error_bag = error_bag
    error_message = "Incorrect arguments.\n"
    error_message += "Errors:\n" + str(error_bag['errors']) + '\n'
    error_message += "Config:\n" + str(error_bag['config'])
    super(ArgumentsException, self).__init__(error_message)



def YMLReader(filepath, defaults={}, debug=False):
  try:
    with open(filepath) as f:
      config = yaml.safe_load(f)
  except Exception as e:
    config = {}
    if debug:
      print 'YMLReader Exception:\n' + str(e)
  return dict_merge(config, defaults)
    

class PageScrapper(object):
  """
    Scrapes a facebook profile information.
  """
  __metaclass__ = ABCMeta

  def __init__(self, driver, configpath, reader=YMLReader, **kwargs):
    self.driver = driver
    self.configpath = configpath
    self.config_reader = reader
    self.data = {}
    debug = kwargs['debug'] if 'debug' in kwargs else False
    self.config = self.config_reader(configpath, kwargs, debug=debug)
    validation = self.validate()
    if not validation == True:
      raise ArgumentsException(validation)

  def goto(self, url):
    if self.driver.current_url != url:
      self.driver.get(url)

  def get_config(self, key):
    conf = self.config
    for k in key.split('.'):
      if isinstance(conf, dict) and k in conf:
        conf = conf[k]
      else:
        return None
    
    return conf

  def set_config(self, key, value):
    raise Exception('not implemented')
    conf = self.config
    keys = key.split('.')
    last_key = keys.pop()
    for k in keys:
      if isinstance(conf, dict):
        if k not in conf:
          conf[k] = {}
        conf = conf[k]
        
    conf[key] = value

  def has_config(self, key_prefix, key_suffixes=None):
    """
      checks if a config key exists.
      if key_suffixes is None, only the key_prefix is checked and used as a full key
      ex: has_config('path.base') checks if 'path.base' exists in the config

      otherwise, it checks if the key_prefix exists and all it's suffixes exists inside it
      ex: has_config('path', ['base', 'profile']) checks if 'path.base' and 'path.profile'
      exists in the config
    """

    if key_suffixes is None:
      return self.has_conf(key_prefix, self.config)

    if not isinstance(key_suffixes, list):
      raise Exception('has_config accepts only a list of child keys')

    for suffix in key_suffixes:
      if not self.has_conf('.'.join([key_prefix, suffix]), self.config):
        return False

    return True

  def has_conf(self, key, config={}):
    keys = key.split('.')
    first_key = keys.pop(0)

    if first_key in config:
      if len(keys) == 0:
        return True
      
      new_keys = '.'.join(map(str, keys))
      if isinstance(config[first_key], dict):
        return self.has_conf(new_keys, config[first_key])

    return False

  def config_error(self, errors):
    return {
      'errors': errors,
      'config': self.config
    }

  def should_scroll(self, next_section, body, old_height, height, max_iterations, i):
    """ checks if scroll is still necessary to show the full section """
    if max_iterations >= 0 and i >= max_iterations:
      return False

    return next_section is None and (page_is_loading(body) or old_height < height)

  def get_next_section(self):
    """
      Selectionne la premiere section qui suit la section en cours
      Return Block de section ou None
    """
    for selector in self.get_config('selectors.next_section'):
      try:
        return self.driver.find_root_by_css_selector(selector)
      except Exception as e:
        pass
          
    return None

  def show_all(self, root, iter=-1, direction='up'):
    """ Scroll until the current section is all shown 
      iter = -1: scroll to the end of the section
      iter >= 0: scroll iter times
    """
    next_section = None
    old_height = -1
    height = get_page_height(self.driver)
    i = 0
    while self.should_scroll(next_section, root, old_height, height, iter, i):
      old_height = height
      root.send_keys(Keys.END)
      next_section = self.get_next_section()
      height = get_page_height(self.driver)
      i += 1

  @abstractmethod
  def start(self):
    pass

  @abstractmethod
  def validate(self):
    pass