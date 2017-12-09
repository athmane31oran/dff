from os import path

from ..fburl import FB_URL
from ..helpers import join_or_make
from .base import PageScrapper


class Login(PageScrapper):
  def __init__(self, driver, username, password, configpath, *args, **kwargs):
    super(Login, self).__init__(driver, configpath, *args, **kwargs)

    self.username = username
    self.password = password
    self.url = FB_URL.BASE_URL

  def validate(self):
    if not self.has_config('selectors', ['email', 'password', 'submit']):
      return self.config_error(
        ['Loging page needs selectors config. Pass them as constructor arguments' + \
          'or in config file.'])
    return True

  def start(self):
    self.goto(self.url)

    self.driver.find_element_by_css_selector(self.get_config("selectors.email")) \
      .send_keys(self.username)
    self.driver.find_element_by_css_selector(self.get_config("selectors.password")) \
      .send_keys(self.password)
    self.driver.find_element_by_css_selector(self.get_config("selectors.submit")) \
      .click()

    # TODO: how to know that we are actually logged in?
    self.data['logged_in'] = self.driver.current_url == self.url