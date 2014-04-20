COUNT = 15

@handler('/video/redditaccount', 'Reddit Account')
def MainMenu():
  oc = ObjectContainer(
    objects = [
      DirectoryObject(
        title = 'Front Page',
        key = Callback(FrontPage)
      ),
      DirectoryObject(
        title = 'Saved',
        key = Callback(Saved)
      ),
      PrefsObject(
        title = 'Settings'
      )
    ]
  )
  return oc

def FrontPage():
  return ListVideos()

def Saved():
  return ListVideos('/saved')

def ListVideos(path = '', page_status = {'link_count': 0, 'after': ''}):
  oc = ObjectContainer()
  if IsLoggedIn():
    while len(oc) < COUNT:
      AddVideos(oc, path, page_status)
    oc.add(DirectoryObject(
      title = 'Next',
      key = Callback(ListVideos, path = path, page_status = page_status)
    ))
  else:
    oc.add(DirectoryObject(
      title = 'No Dice',
      key = Callback(Dummy)
    ))
  return oc

def IsLoggedIn():
  if HTTP.GetCookiesForURL('http://reddit.com'):
    return True
  if Prefs['username'] and Prefs['password']:
    login_response = JSON.ObjectFromURL(
      'https://ssl.reddit.com/api/login',
      values = {
        'user': Prefs['username'],
        'passwd': Prefs['password'],
        'api_type': 'json',
        'rem': 'True'
      }
    )
    if login_response['json'] and not login_response['json']['errors']:
      return True
  return False

def AddVideos(oc, path, page_status):
  links = JSON.ObjectFromURL('http://reddit.com%s/.json?limit=%s&count=%s&after=%s' % (path, COUNT, page_status['link_count'], page_status['after']))
  page_status['link_count'] = page_status['link_count'] + COUNT
  page_status['after'] = links['data'].get('after')
  for link in links['data']['children']:
    link_data = link.get('data')
    if link_data.get('domain') in ['youtu.be', 'youtube.com'] and link_data['media']:
      video_data = link_data['media'].get('oembed')
      oc.add(MovieObject(
        title = link_data.get('title'),
        summary = video_data.get('title'),
        thumb = video_data.get('thumbnail_url'),
        url = link_data.get('url')
      ))

def Dummy():
  pass
