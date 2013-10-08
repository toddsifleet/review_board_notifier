Review Board Notifier
=====================

A tool that notifies you via OS X notification center of any changes in review board.


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
=======

  NOTE:  If you include your password here it will be displayed, it will show
  up in your bash_history.  If you omit the password you will be prompted.

      >> python review_board_notifier <username> <base_url> <password (optional)>
