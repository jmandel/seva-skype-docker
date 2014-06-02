import sqlite3
import json
import os
import sys
import codecs
import re
import md5
from xml.sax.saxutils import unescape, escape
from feedgen.feed import FeedGenerator
from jinja2 import Environment, FileSystemLoader

# e.g. python export_history.py /home/jmandel/.Skype/jcmandel/main.db > export.json

c = sqlite3.connect(sys.argv[1])
c.row_factory = sqlite3.Row
cur = c.cursor()

start_date = "2014-06-01"

chatnames = {
  '#lmckenzi/$grahamegrieve;da9763898aba4d78': {
    'title': 'Committers chat',
    'slug': 'committers'
  },
  '#ewoutkramer/$f6a8a0ea0abcc75d': {
    'title': 'Implementers Chat',
    'slug': 'implementers'
  }
}

template_env = Environment(loader=FileSystemLoader('templates'), autoescape=True)
page = template_env.get_template('page.html')

for chatid, chat in chatnames.iteritems():
    cur.execute("""
    SELECT
      author, 
      body_xml,
      chatname,
      datetime(timestamp, 'unixepoch', 'localtime') as timestamp,
      datetime(edited_timestamp, 'unixepoch', 'localtime') as edited_timestamp,
      fullname
    FROM messages m
    LEFT OUTER JOIN Contacts c on m.author=c.skypename
    WHERE
      datetime(timestamp, 'unixepoch', 'localtime') > date("%s") and
      chatname="%s" and
      body_xml not null
      order by timestamp desc;
    """%(start_date, chatid))
    #posts = [dict(r) for r in cur.fetchall()]
    #print json.dumps(posts, indent=2)

    messages = []

    fg = FeedGenerator()
    fg.id('https://chats.fhir.me/feeds/skype/%s.atom'%chat['slug'])
    fg.link(href='urn:skypechat:%s'%chatid, rel='related')
    fg.title('FHIR Skype %s'%chat['title'])
    fg.author( {'name':'FHIR Core Team','email':'fhir@lists.hl7.org'} )
    fg.link(href='https://chats.fhir.me/feeds/skype/%s.atom'%chat['slug'], rel='self')
    fg.language('en')

    for praw in cur.fetchall():
      p = dict(praw)
      p['timestamp'] = p['timestamp']+'Z'
      if p['edited_timestamp']:
        p['edited_timestamp'] = p['edited_timestamp']+'Z'

      authorname = p['fullname']
      if not authorname: authorname = p['author']

      m = md5.new()
      m.update(json.dumps({'author': p['author'], 'timestamp': p['timestamp']}))
      chathash = m.hexdigest()

      body = escape(p['body_xml'])
      body = re.sub("<quote>.*?</quote>", "", body)
      body = re.sub("\n", "\n<br/>", body)
      body = body

      messages.append({
        'who': authorname,
        'when': p['timestamp'],
        'what': unescape(body)
      })

      fe = fg.add_entry()
      fe.id('https://chats.fhir.me/feeds/skype/%s/messages/%s'%(chat['slug'], chathash))
      fe.author({'name': authorname, 'uri': 'urn:skypename:%s'%p['author']})
      fe.title('Message from %s'%authorname);
      fe.pubdate(p['timestamp'])
      if p['edited_timestamp']:
        fe.updated(p['edited_timestamp'])
      else:
        fe.updated(p['timestamp'])
      fe.content(body, type="html")

    try:
      os.mkdir('static/feeds/skype')
    except: pass

    with codecs.open("static/feeds/skype/%s.atom"%chat['slug'], "w", "utf-8") as fo:
      fo.write(fg.atom_str(pretty=True))
    
    messages.reverse()
    with codecs.open("static/browsable/skype/%s.html"%chat['slug'], "w", "utf-8") as fo:
      fo.write(page.render({
        'chat_name': chat['title'],
        'messages': messages,
        'slug': chat['slug'],
        'other_chats': chatnames.values()
      }))
      print messages

