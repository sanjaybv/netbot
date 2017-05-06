import urllib2
import json

string = "https://github.com/sanjaybv/netbot-hell"

str1 = list(string.partition('github.com'))

str1[0] = 'https://' + str1[0] + 'api.'
str1[2] = '/repos' + str1[2]

string = str1[0] + str1[1] + str1[2]

# req = urllib2.Request(string, {'Content-Type': 'application/json'})
# f = urllib2.urlopen(req)
# if 'message' in f:
# 	print f['message']

import requests
r = requests.get(string)
print type(r), len(r.json())

if len(r.json()) == 2 :
	print 'invalid URL'
