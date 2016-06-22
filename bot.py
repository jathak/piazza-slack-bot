from slackclient import SlackClient
from piazza_api import Piazza
import time
import re
import humanize
import json
from datetime import datetime
import html2text
import traceback

token = "SLACK-BOT-TOKEN"
piazza_id = "PIAZZA-COURSE-ID"
piazza_email = "PIAZZA-ACCOUNT-EMAIL"
piazza_password = "PIAZZA-ACCOUNT-PASSWORD"
bot_id = None
sc = SlackClient(token)
p = Piazza()
p.user_login(email=piazza_email, password=piazza_password)

def process_bot_call(channel, user, text):
    calls = text.split("<@" + bot_id + ">")[1:]
    for call in calls:
        post_id = re.search(r'\d+', call).group()
        post_link(channel, user, post_id, piazza_id)

def post_link(channel, user, post_id, piazza_id):
    title = "Piazza Post #" + post_id
    content = "Could not fetch post content"
    time = None
    try:
        post = p.network(piazza_id).get_post(post_id)
        title = post['history'][0]['subject']
        content = format_html(post['history'][0]['content'])
        timestamp = post['history'][0]['created']
        time_format = "%Y-%m-%dT%H:%M:%SZ"
        post_time = datetime.strptime(timestamp, time_format)
        time = humanize.naturaltime(datetime.utcnow() - post_time)
    except:
        pass
    url = "https://piazza.com/class/" + piazza_id + "?cid=" + post_id
    msg = {
        "fallback": title + ", " + url,
        "title": title,
        "title_link": url,
        "text": content,
        "footer": time,
        "color": "#3e7aab",
        "mrkdwn_in": ["text"]
    }
    attach = json.dumps([msg])
    sc.api_call('chat.postMessage', channel=channel, attachments=attach,
                as_user=True)

def format_html(unicode_string):
    try:
        h = html2text.HTML2Text()
        h.body_width = 0
        unicode_string = unicode_string.replace('target="_blank"', "").replace("\n\n", "<div></div>")
        text = h.handle(unicode_string)
        text = text.replace('**', '__bold__').replace('*', '_').replace('__bold__', '*')
        text = text.replace('\n\\- ', '\n- ')
        links = find_md_links(text)
        for name, link in links:
            text = text.replace('[%s](%s)'%(name, link), '<%s|%s>'%(link, name))
        return text
    except Exception as e:
        traceback.print_exc()
        return unicode_string

INLINE_LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

def find_md_links(md):
    """ Return dict of links in markdown """
    links = INLINE_LINK_RE.findall(md)
    return links

if sc.rtm_connect():
    username = sc.server.username
    for users in sc.server.login_data['users']:
        if users['name'] == username:
            bot_id = users['id']
            break
    if not bot_id:
        raise Error("Could not find bot")
    while True:
        results = sc.rtm_read()
        for result in results:
            try:
                if result['type'] == 'message':
                    channel = result['channel']
                    user = result['user']
                    text = result['text']
                    urls = re.findall(r'https://piazza\.com/class/([\w]+)\?cid=([\d]+)', text)
                    if len(urls) > 0:
                        for piazza, post in urls:
                             post_link(channel, user, post, piazza)
                    elif bot_id in text:
                        process_bot_call(channel, user, text)
            except Exception as e:
                traceback.print_tb(e.__traceback__)
        time.sleep(1)
else:
    print("Connection Failed, invalid token?")
