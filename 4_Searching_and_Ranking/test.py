# -*- coding:utf-8 -*-

import urllib2
import pprint
from BeautifulSoup import *

proxy = urllib2.ProxyHandler({'https' : '127.0.0.1:1080'})
opener = urllib2.build_opener(proxy)
c = opener.open('https://en.wikipedia.org/wiki/China')
soup = BeautifulSoup(c.read())

# print soup.prettify()
# pprint.pprint(soup('a'))
# print soup('a')[1]['href']
# pprint.pprint(soup.contents)