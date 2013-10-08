try:
  import requests
  from pync import Notifier
  from BeautifulSoup import BeautifulSoup
  from dateutil.parser import parse
  from dateutil import tz
  import datetime
  import time
  import os
  import sys
  import getpass

except ImportError:
  print '''
  This script requires:
    - OS X 10.8+
    - python 2.6/2.7 and you must have:
      - requests [http://docs.python-requests.org/en/latest/]
      - pync [https://pypi.python.org/pypi/pync]
      - BeautifulSoup [https://pypi.python.org/pypi/BeautifulSoup/3.2.1]

  To get these I would use pip [https://pypi.python.org/pypi/pip]

  To install these packages with pip:
    >> pip install requests
    >> pip install pync
    >> pip install BeautifulSoup

  Usage:
    NOTE:  If you include your password here it will be displayed, it will show
    up in your bash_history.  If you omit the password you will be prompted.

    >> python %s <username> <base_url> <password (optional)>
  ''' % sys.argv[0]

base_url = ''

def get_authenticated_session(username, password):
  session = requests.Session()
  login_url = '%s/account/login/' % base_url
  session.get(login_url) # fakes CSRF -- this sets a cookie
  response = session.post(login_url, {
    'username': username,
    'password': password,
    'next_page': '/dashboard/'
    }, allow_redirects=True)
  
  if response.url == login_url:
    raise Exception("Error Logging In -- Check your username/password")

  return session

def parse_dash_board(page):
  def convert_time_stamp(stamp):
    return parse(stamp).astimezone(tz.tzlocal())

  def parse_row(row):
    cells = row.findAll('td')
    return {
      'id': cells[2].find('a')['href'].split('/')[2],
      'name': cells[2].text,
      'owner': cells[3].text,
      'last_update': convert_time_stamp(cells[5].find('time')['datetime'])

    }

  # A hack way to parse out all of the rows from the table that we care about
  soup = BeautifulSoup(page)
  rows = soup.findAll('tr', { "class" : "odd" }) 
  rows += soup.findAll('tr', { "class" : "even" })
  return map(parse_row, rows)

def get_dash_board(session):
  dashboard_url = '%s/dashboard/' % base_url
  return session.get(dashboard_url).content

def get_reviews(session):
  return parse_dash_board(get_dash_board(session))

def review_url(id):
  return "%s/r/%s/" % (base_url, str(id))

def notify_new_review(review):
  Notifier.notify(review['name'], 
    title = 'New Review [%s]' % review['owner'],
    open = review_url(review['id'])
  )

def notify_review_update(review):
  Notifier.notify(review['name'], 
    title = 'Review Update [%s]' % review['owner'],
    open = review_url(review['id'])
  )

def clear_old_reviews(new_reviews, old_reviews):
  active_reviews = [x['id'] for x in new_reviews]
  for id in old_reviews.keys():
    if id not in active_reviews:
      del old_reviews[id]

def process_reviews(new_reviews, old_reviews):
  new_offset = datetime.timedelta(minutes = 35)
  clear_old_reviews(new_reviews, old_reviews)
  for review in new_reviews:
    if review['id'] not in old_reviews:
      if review['last_update'] + new_offset > datetime.datetime.now(tz.tzlocal()):
        notify_new_review(review)
    elif not review == old_reviews[review['id']]:
      notify_review_update(review)
    else:
      continue
    old_reviews[review['id']] = review


def run(username, password, delay = 120):
  print "Connecting..."
  session = get_authenticated_session(username, password)
  print "Connected..."
  old_reviews = {}
  while True:
    try:
      reviews = get_reviews(session)
      process_reviews(reviews, old_reviews)
    except Exception as e:
      print 'Error processing reviews:'
      print e
    time.sleep(delay)

if __name__ == '__main__':
  try:
    if len(sys.argv) < 3:
      print 'Usage: \n >> python %s <username> <base_url> <password (optional)>' % sys.argv[0]
      sys.exit(1)
    base_url = sys.argv[2]
    password = sys.argv[3] if len(sys.argv) == 4 else getpass.getpass() 
    run(sys.argv[1], password)
  except KeyboardInterrupt:
    Notifier.remove(str(os.getpid()))
