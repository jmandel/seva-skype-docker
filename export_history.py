import sqlite3
import json
import sys
import re
import md5
from feedgen.feed import FeedGenerator

# e.g. python export_history.py /home/jmandel/.Skype/jcmandel/main.db > export.json

c = sqlite3.connect(sys.argv[1])
c.row_factory = sqlite3.Row
cur = c.cursor()

start_date = "2014-06-01"

chatnames = {
  '#ewoutkramer/$f6a8a0ea0abcc75d': {
    'title': 'Committers chat',
    'slug': 'committers_chat'
  },
  '#lmckenzi/$grahamegrieve;da9763898aba4d78': {
    'title': 'Implementers Chat',
    'slug': 'implementers_chat'
  }
}

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
      order by timestamp;
    """%(start_date, chatid))
    #posts = [dict(r) for r in cur.fetchall()]
    #print json.dumps(posts, indent=2)

    fg = FeedGenerator()
    fg.id('https://chat.fhir.me/feeds/%s.rss'%chat['slug'])
    fg.link(href='skype://%s'%chatid, rel='related')
    fg.title('FHIR Skype %s'%chat['title'])
    fg.author( {'name':'FHIR Core Team','email':'fhir@lists.hl7.org'} )
    fg.link(href='https://chat.fhir.me/feeds/%s.atom'%chat['slug'], rel='self')
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

      body = p['body_xml']
      body = re.sub("<quote>.*?</quote>", "", body)
      #print body.encode('utf8')

      fe = fg.add_entry()
      fe.id('https://chat.fhir.me/chats/%s/messages/%s'%(chat['slug'], chathash))
      fe.author({'name': authorname, 'uri': 'skypeid:%s'%p['author']})
      fe.title('Message from %s'%authorname);
      fe.pubdate(p['timestamp'])
      if p['edited_timestamp']:
        fe.updated(p['edited_timestamp'])
      else:
        fe.updated(p['timestamp'])
      fe.content(body)

    fo = open("%s.rss"%chat['slug'], "w")
    print >>fo, fg.atom_str(pretty=True)
    fo.close()
