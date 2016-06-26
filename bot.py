from slackclient import SlackClient
from piazza_api import Piazza
import time
import re
import humanize
import json
from datetime import datetime
import html2text
import traceback

from bot_config import token, piazza_id, piazza_email, piazza_password

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
    image = None
    a_name, a_photo = "", None
    try:
        network = p.network(piazza_id)
        post = network.get_post(post_id)
        title = post['history'][0]['subject']
        content, image = format_html(post['history'][0]['content'])
        timestamp = post['history'][0]['created']
        time_format = "%Y-%m-%dT%H:%M:%SZ"
        post_time = datetime.strptime(timestamp, time_format)
        time = humanize.naturaltime(datetime.utcnow() - post_time)
        a_name, a_photo = find_authors(post['history'], network)
    except:
        pass
    url = "https://piazza.com/class/" + piazza_id + "?cid=" + post_id
    footer = time
    if a_name is not None:
        footer = a_name + " - " + time
    msg = {
        "fallback": title + ", " + url,
        "title": title,
        "title_link": url,
        "text": content,
        "footer": footer,
        "footer_icon": a_photo,
        "image_url": image,
        "color": "#3e7aab",
        "mrkdwn_in": ["text"]
    }
    attach = json.dumps([msg])
    sc.api_call('chat.postMessage', channel=channel, attachments=attach,
                as_user=True)

PHOTO_SERVER = "https://d1b10bmlvqabco.cloudfront.net/photos"

def find_authors(history, network):
    try:
        authors = [(e['anon'] != 'no', e['uid'] if 'uid' in e else None) for e in history]
        ids = set([x[1] for x in authors])
        user_data = network.get_users([x for x in ids if x is not None])
        users = {}
        for u in user_data:
            users[u['id']] = u
        if len(ids) == 1:
            anon, uid = authors[0]
            if uid is None:
                return None, None
            user = users[uid]
            name = user['name']
            photo = None
            if anon:
                name += " (anon)"
            if user['photo']:
                photo = PHOTO_SERVER + '/' + uid + '/' + user['photo']
            return name, photo
        elif len(ids) == 2:
            anon1, uid1 = authors[0]
            name1, name2 = "Anonymous", "Anonymous"
            if uid1 is not None:
                user1 = users[uid1]
                name1 = user1['name']
                if anon1:
                    name1 += " (anon)"
            anon2, uid2 = authors[1]
            if uid2 is not None:
                user2 = users[uid2]
                name2 = user2['name']
                if anon2:
                    name2 += " (anon)"
            return name1 + " and " + name2, None
        else:
            anon, uid = authors[0]
            name, photo = "Anonymous", None
            if uid is not None:
                user = users[uid]
                name = user['name']
                if anon:
                    name += " (anon)"
                if user['photo']:
                    photo = PHOTO_SERVER + '/' + uid + '/' + user['photo']
            name += " and " + str(len(ids) - 1) + " others"
            return name, photo
    except:
        traceback.print_exc()
        return None, None
        

def format_html(html):
    try:
        h = html2text.HTML2Text()
        h.body_width = 0
        html = html.replace('target="_blank"', "").replace("\n\n", "<div></div>")
        html = html.replace('<br />', '<br>')
        while "<pre>" in html:
            index = html.find('<pre>')
            prev = html[:index] + '```'
            build = ''
            end = html.find('</pre>')
            for i in range(index + 5, end):
                cur = html[i]
                if cur == ' ':
                    cur = '&nbsp;'
                build += cur
            build = build.replace('\n', '<br>')
            html = prev + build + '<br>```' + html[end + 6:]
        text = h.handle(html)
        text = text.replace('**', '__bold__').replace('*', '_').replace('__bold__', '*')
        text = text.replace('\n\\- ', '\n- ')
        links, images = find_md_links(text)
        for name, link in links:
            text = text.replace('[%s](%s)'%(name, link), '<%s|%s>'%(link, name))
        for image in images:
            text = text.replace('![](%s)'%(image), '<%s|Image>'%(image))
        first_image = None
        if len(images) > 0:
            first_image = images[0]
        return text, first_image
    except Exception as e:
        traceback.print_exc()
        return html, None

INLINE_LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
INLINE_IMAGE_RE = re.compile(r'!\[\]\(([^)]+)\)')

def find_md_links(md):
    """ Return dict of links in markdown """
    links = INLINE_LINK_RE.findall(md)
    images = INLINE_IMAGE_RE.findall(md)
    return links, images

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
