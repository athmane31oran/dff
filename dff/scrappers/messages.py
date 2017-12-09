from os import path
import re
import json

from selenium.webdriver.common.keys import Keys

from ..fburl import FB_URL
from ..helpers import join_or_make, save_photos, messages_loading
from .base import PageScrapper


class Messages(PageScrapper):
  def __init__(self, driver, friend_id, configpath, *args, **kwargs):
    super(Messages, self).__init__(driver, configpath, *args, **kwargs)

    self.friend_id = friend_id
    self.url = FB_URL.messages_page()

  def validate(self):
    return True

  def start(self):
    self.goto(self.url)
    self.driver.execute_script(self.get_interseptor_script())
    friend_selector = self.get_config('selectors.friend') % self.friend_id
    print 'friend_selector', friend_selector
    self.driver.find_element_by_id(friend_selector).click()

    self.data['raw_messages'] = self.get_messages()

    self.data['messages'] = self.transform_messages(self.data['raw_messages'])

    if self.get_config('save'):
      self.save()

  def get_messages(self):
    try:
      # Scroll up to show all messages
      root = self.driver.find_element_by_css_selector(self.get_config('selectors.container'))
      self.scroll_up(root, self.get_config('num_pages'))
      # raw messages
      return self.driver.find_element_by_id('interceptedResponse').text.split('*****')
    except Exception as e:
      if self.get_config('debug'):
        print("get_messages exception:\n" + str(e))
      return []

  def scroll_up(self, root, num_pages=1):
    for i in range(num_pages):
      for i in range(3 * num_pages): root.send_keys(Keys.PAGE_UP)
      while messages_loading(self.driver): pass

  def get_interseptor_script(self):
    return """
      (function(XHR) {
        "use strict";

        var element = document.createElement('div');
        element.id = "interceptedResponse";
        element.appendChild(document.createTextNode(""));
        document.body.appendChild(element);

        var open = XHR.prototype.open;
        var send = XHR.prototype.send;

        XHR.prototype.open = function(method, url, async, user, pass) {
          this._url = url; // want to track the url requested
          open.call(this, method, url, async, user, pass);
        };

        XHR.prototype.send = function(data) {
          var self = this;
          var oldOnReadyStateChange;
          var url = this._url;

          function onReadyStateChange() {
            if(self.status === 200 && self.readyState == 4 && url == '/api/graphqlbatch/') {
              document.getElementById("interceptedResponse").innerHTML += self.responseText + '*****';
            }
            if(oldOnReadyStateChange) {
              oldOnReadyStateChange();
            }
          }

          if(this.addEventListener) {
            this.addEventListener("readystatechange", onReadyStateChange,
              false);
          } else {
            oldOnReadyStateChange = this.onreadystatechange;
            this.onreadystatechange = onReadyStateChange;
          }
          send.call(this, data);
        }
      })(XMLHttpRequest);
      """

  def save(self):
    pass
    
  def transform_messages(self, raw_messages):
    messages = []
    for raw_message in raw_messages:
      if len(raw_message) <= 1: continue
      splits = raw_message.split('} {')
      if len(splits) > 2: raise Exception("didn't expect more than two splits in raw message")
      splits[0] += '}'
      message = self.transform_message(splits[0])
      messages.append(message)
    return messages

  def transform_message(self, message_text):
    obj = json.loads(message_text)
    obj = obj[obj.keys()[0]]
    messages = obj['data']['message_thread']['messages']['nodes']
    formatted_messages = []
    for m in messages:
      formatted_messages.append({
        'sender_id': m['message_sender']['id'],
        'timestamp': m['timestamp_precise'],
        'text': m['message']['text'],
        'attachements': m['blob_attachments']
      })
    return formatted_messages