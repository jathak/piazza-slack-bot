from slackclient import SlackClient
from piazza_api import Piazza
import time
import re
import humanize
import json
from datetime import datetime
import html2text
import traceback

def process_bot_call(channel, user, text, thread=None):
    calls = text.split("<@" + bot_id + ">")[1:]
    for call in calls:
        post_id = re.search(r'\d+', call).group()
        post_link(channel, user, post_id, piazza_id, thread)

def make_attachment(post, network, followup, url):
    title = "Piazza Post"
    content = "Could not fetch post content"
    time = None
    image = None
    child = None
    a_name, a_photo = "", None
    try:
        title = post['history'][0]['subject']
        if followup:
            title = 'Followup #{} to {}'.format(followup, title)
            child = post['children'][int(followup) - 1]
            content, image = format_html(child['subject'])
            timestamp = child['created']
            a_name, a_photo = find_followup_author(child, network)
        else:
            content, image = format_html(post['history'][0]['content'])
            timestamp = post['history'][0]['created']
            a_name, a_photo = find_authors(post['history'], network)
        time_format = "%Y-%m-%dT%H:%M:%SZ"
        post_time = datetime.strptime(timestamp, time_format)
        time = humanize.naturaltime(datetime.utcnow() - post_time)
    except:
        pass
    footer = time
    if a_name is not None:
        footer = a_name + " - " + time
    msg = {
        "fallback": content if followup else title + ", " + url,
        "title": title,
        "title_link": url,
        "text": content,
        "footer": footer,
        "footer_icon": a_photo,
        "image_url": image,
        "color": "#3e7aab",
        "mrkdwn_in": ["text"]
    }
    return json.dumps([msg])

def make_reply(reply, network):
    content, image = format_html(reply['subject'])
    timestamp = reply['created']
    time_format = "%Y-%m-%dT%H:%M:%SZ"
    post_time = datetime.strptime(timestamp, time_format)
    time = humanize.naturaltime(datetime.utcnow() - post_time)
    a_name, a_photo = find_followup_author(reply, network)
    footer = time
    if a_name is not None:
        footer = a_name + " - " + time
    return {
        "fallback": content,
        "text": content,
        "footer": footer,
        "footer_icon": a_photo,
        "image_url": image,
        "mrkdwn_in": ["text"]
    }
    

def post_link(channel, user, post_id, piazza_id, thread=None, followup=None):
    post, network = None, None
    try:
        network = p.network(piazza_id)
        post = network.get_post(post_id)
    except:
        return
    url = "https://piazza.com/class/" + piazza_id + "?cid=" + post_id
    attach = make_attachment(post, network, followup, url)
    response = None
    if thread:
        response = sc.api_call('chat.postMessage', channel=channel,
            attachments=attach, as_user=True, thread_ts=thread)
    else:
        response = sc.api_call('chat.postMessage', channel=channel,
            attachments=attach, as_user=True)
    replies = []
    if followup and not thread:
        for reply in post['children'][int(followup) - 1]['children']:
            replies.append(make_reply(reply, network))
    if replies:
        sc.api_call('chat.postMessage', channel=channel, as_user=True, 
            attachments=json.dumps(replies), thread_ts=response['ts'])
        

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

def find_followup_author(child, network):
    try:
        anon = child['anon'] != 'no'
        uid = child['uid'] if 'uid' in child else None
        if not uid:
            return None, None
        user_data = network.get_users([uid])
        user = user_data[0]
        name = user['name']
        photo = None
        if anon:
            name += " (anon)"
        if user['photo']:
            photo = PHOTO_SERVER + '/' + uid + '/' + user['photo']
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
            true_link = link
            if link.startswith('/'):
                true_link = 'https://piazza.com' + link
            text = text.replace('[%s](%s)'%(name, link), '<%s|%s>'%(true_link, name))
        for image in images:
            true_image = image
            if image.startswith('/'):
                true_image = 'https://piazza.com' + image
            text = text.replace('![](%s)'%(image), '<%s|Image>'%(true_image))
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

def handle_message(result):
    channel = result['channel']
    user = result['user']
    if user == bot_id:
        return
    text = result['text']
    urls = re.findall(r'https://piazza\.com/class/([\w]+)\?cid=([\d]+)', text)
    all_names = '|'.join(other_piazza_names)
    at_nums = re.findall(r'(\A|\s|' + all_names + r')@(\d+)(?:\s|\Z|,|\?|;|:|\.)', text)
    at_nums_followup = re.findall(r'(\A|\s|' + all_names + r')@(\d+)#(\d+)(?:\s|\Z|,|\?|;|:|\.)', text)
    thread = None
    if 'thread_ts' in result and result['thread_ts'] != result['ts']:
        thread = result['thread_ts']

    posts = set()
    for pid, post in urls:
        posts.add((pid, post, None))
    for course, post in at_nums:
        course = course.strip()
        pid = other_piazza_ids[other_piazza_names.index(course)] if course else piazza_id
        posts.add((pid, post, None))
    for course, post, followup in at_nums_followup:
        course = course.strip()
        pid = other_piazza_ids[other_piazza_names.index(course)] if course else piazza_id
        posts.add((pid, post, followup))
    
    if len(posts) > 0:
        for pid, post, followup in posts:
            post_link(channel, user, post, pid, thread, followup)
    elif bot_id in text:
        process_bot_call(channel, user, text, thread)

if __name__ == "__main__":
    from bot_config import *

    bot_id = None
    sc = SlackClient(token)
    p = Piazza()
    p.user_login(email=piazza_email, password=piazza_password)

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
                        handle_message(result)
                except Exception as e:
                    print(e)
                    sc.rtm_connect()
            time.sleep(1)
    else:
        print("Connection Failed, invalid token?")
