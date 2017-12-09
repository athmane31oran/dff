import re

class FB_URL(object):
  BASE_URL = 'https://www.facebook.com/'

  @staticmethod
  def is_fb_id(profile_id):
    return re.search('^[0-9]+$', profile_id)

  @staticmethod
  def is_fb_username(profile_id):
    return not FB_URL.is_fb_id(profile_id)

  @staticmethod
  def about_page(profile_id):
    if FB_URL.is_fb_id(profile_id):
      # TODO: maybe put these in config too, something like:
      # about_page:
      #   id: "$base_url/profile.php?id=$id&sk=about&section=contact-info"
      #   username: "$base_url/$username?section=contact-info"
      return FB_URL.BASE_URL + 'profile.php?id=' + profile_id\
        + 'sk=about&&section=contact-info'
    return FB_URL.BASE_URL + profile_id + '/about?section=contact-info'

  @staticmethod
  def fb_id_from_url(url):
    result = re.search('id=([0-9]+).*', url)
    if result:
      return result.group(1), 'id'
    
    result = re.search('facebook.com/([a-zA-Z0-9\.-]+).*', url)
    if result:
      return result.group(1), 'username'
    
    raise Exception("Couldn't extract FB id from the url: ", url)

  @staticmethod
  def extrat_profile_url(url):
    """ Gets user url from a link """
    splits = url.split('?')
    newUrl = splits[0]
    if len(splits) == 1:
      return newUrl
    
    m = re.search('id=[0-9]+', splits[1])
    if m:
      return newUrl + '?' + m.group(0)
    return newUrl

  @staticmethod
  def friends_page(profile_url, mutual=False):
    user_id, id_type = FB_URL.fb_id_from_url(profile_url)    
   
    suffix = '_mutual' if mutual else ''
    
    if id_type == 'username':
      return profile_url + '/friends' + suffix
    else:
      return '%sprofile.php?id=%s&sk=friends%s' % (FB_URL.BASE_URL, user_id, suffix)

  @staticmethod
  def photos_page(profile_url):
    user_id, id_type = FB_URL.fb_id_from_url(profile_url)

    if id_type == 'username':
      return profile_url + '/photos'
    else:
      return '%sprofile.php?id=%s&sk=photos' % (FB_URL.BASE_URL, user_id)

  @staticmethod
  def messages_page(profile_id=''):
    return FB_URL.BASE_URL + 'messages/t/' + profile_id