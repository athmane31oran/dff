from ..fburl import FB_URL
from .base import PageScrapper


class AboutPage(PageScrapper):
  def __init__(self, driver, profile_id, configpath, *args, **kwargs):
    super(AboutPage, self).__init__(driver, configpath, *args, **kwargs)
    self.profile_id = profile_id
    self.url = FB_URL.about_page(profile_id)

  def validate(self):
    # maybe validate the current url?
    if not self.has_config('selectors', ['basic_info', 'contact_info']):
      return ['About page needs selectors config. Pass them as constructor arguments' + \
        'or in config file.']
    return True

  def parse_info(self, text):
    """
      Parse about page text data and return it as an object.
    """
    result = {'raw': text}
    key = ''
    for i, item in enumerate(text.split('\n')):
        if i % 2 == 0:
            key = item.strip().lower().replace(' ', '_').replace('[^a-z]', '')
        else:
            result[key] = item
    return result

  def start(self):
    # maybe check the current url before changing the page?
    self.driver.get(self.url)

    basic_info = self.driver \
      .find_element_by_css_selector(self.get_config('selectors.basic_info')) \
      .text
    self.data['basic_info'] = self.parse_info(basic_info)

    contact_info = self.driver \
      .find_element_by_css_selector(self.get_config('selectors.contact_info')) \
      .text
    self.data['contact_info'] = self.parse_info(contact_info)
