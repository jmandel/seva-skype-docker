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
from optparse import OptionParser

parser = OptionParser()

parser.add_option("-c", "--chats",
    dest="chats_file",
    default="chats.json",
    help="Chats file: a JSON array of chats")

parser.add_option("-s", "--skype-db",
    dest="skype_db",
    help="""Skype DB file""")

parser.add_option("-o", "--output-dir",
    dest="output_dir",
    default="static",
    help="""Output directory""")

(options, args) = parser.parse_args()
print options

start_date = "2014-06-01"

if not options.skype_db:
  parser.print_help()
  sys.exit(1)

c = sqlite3.connect(options.skype_db)
c.row_factory = sqlite3.Row
cur = c.cursor()

chats = json.load(open(options.chats_file))
template_env = Environment(loader=FileSystemLoader('templates'), autoescape=True)
page = template_env.get_template('page.html')

def generate_feeds(chat):
  print "Processing: %s"%chat['title']
  chatid = chat['id']
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

  messages = []

  fg = FeedGenerator()

  fg.id('https://chats.fhir.me/feeds/skype/%s.atom'%chat['slug'])

  fg.link(href='https://chats.fhir.me/feeds/skype/%s.atom'%chat['slug'], rel='self')
  fg.link(href='https://chats.fhir.me/feeds/skype/%s.json'%chat['slug'], rel='alternate')
  fg.link(href='https://chats.fhir.me/feeds/skype/%s.html'%chat['slug'], rel='alternate')
  fg.link(href='urn:skypechat:%s'%chatid, rel='related')

  fg.title('FHIR Skype Chat: %s'%chat['title'])

  fg.author( {'name':'FHIR Core Team','email':'fhir@lists.hl7.org'} )

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
    body = re.sub("\n", "\n<br/>", body)
    body = body

    updated = p['timestamp']
    if p['edited_timestamp']:
      updated = p['edited_timestamp']

    messages.append({
      'skypename': p['author'],
      'author': authorname,
      'timestamp': p['timestamp'],
      'updated': updated,
      'body': unescape(body)
      })

    fe = fg.add_entry()
    fe.id('https://chats.fhir.me/feeds/skype/%s/messages/%s'%(chat['slug'], chathash))
    fe.author({'name': authorname, 'uri': 'urn:skypename:%s'%p['author']})
    fe.title('Message from %s'%authorname);
    fe.pubdate(p['timestamp'])
    fe.updated(updated)
    fe.content(body, type="html")

  for d in [["feeds"], ["feeds", "skype"]]:
    try:
      os.mkdir(os.path.join(options.output_dir, *d))
    except: pass

  chat_path = os.path.join(options.output_dir,"feeds","skype", chat['slug'])

  with codecs.open(chat_path+'.atom', "w", "utf-8") as fo:
    fo.write(fg.atom_str(pretty=True))

  with codecs.open(chat_path+'.json', "w", "utf-8") as fo:
    fo.write(json.dumps(feed_to_json(fg), indent=2))

  with codecs.open(chat_path+'.html', "w", "utf-8") as fo:
    fo.write(page.render({
      'chat_name': chat['title'],
      'messages': messages,
      'slug': chat['slug'],
      'other_chats': chats
      }))


def feed_to_json(f):
  jg = {
      p: getattr(f, p)() for p in ["id", "link", "title", "author", "language"]
      }
  jg['link'][0]['href'] =  jg['link'][0]['href'].replace('atom', 'json')
  jg['link'][1]['href'] =  jg['link'][1]['href'].replace('json', 'atom')
  jg['entry'] = []

  for fe in f.entry():
    jg['entry'].append({
      p: getattr(fe, p)() for p in ["id", "author", "title", "pubdate", "updated", "content"]
      })
    jg['entry'][-1]['content'] = jg['entry'][-1]['content']['content']
    jg['entry'][-1]['pubdate'] = jg['entry'][-1]['pubdate'].isoformat()
    jg['entry'][-1]['updated'] = jg['entry'][-1]['updated'].isoformat()
    
  return jg

for chat in chats:
  generate_feeds(chat)


