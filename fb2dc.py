import configparser
import requests
from bs4 import BeautifulSoup
from discord_webhook import DiscordWebhook, DiscordEmbed
from os.path import exists

# Read Config
config = configparser.ConfigParser()
config.read('setting.ini', encoding='UTF-8')

# First Request, only can get part of content
webhook_url = config['config']['webhook_url']
fan_page_url = config['config']['fan_page_url']

response = requests.get(fan_page_url)
soup = BeautifulSoup(response.text, "html.parser")
result = soup.find("div", {"class": "fd"})
fb_contents = result.get_text()

# Is a new post?
is_file_exists = exists(".tmp1")
if is_file_exists:
    f = open(".tmp1", 'r')
    last = f.readline()
    f.close()
else:
    last = ""

if last != fb_contents:
    # Record the title
    f = open(".tmp1", 'w')
    f.write(fb_contents)
    f.close()

    # Parse the url for full html(contents)
    fb_href = result.find("a", href=True)['href']
    fb_full_content_url = config['config']['fb_url_html'] + fb_href

    # Request to get the new url
    new_response = requests.get(fb_full_content_url)
    new_soup = BeautifulSoup(new_response.text, "html.parser")
    new_result = new_soup.find("div", {"class": "bx"})

    # Replace <br> with \n
    for br in new_soup.find_all("br"):
        br.replace_with("\n")

    # Get post title and content
    fb_content_lines = []
    fb_content_lines = fb_content_lines + new_result.get_text().splitlines()

    post_title = fb_content_lines[0]
    post_content = "\n".join(fb_content_lines[1:])
    
    # Link to the new post
    result = soup.find("div", {"class": "fe"})
    fb_link = config['config']['fb_url'] + result.find("a", href=True)['href'].split("?")[0]
    dc_link = "[前往連結](" + fb_link +")"

    # Setup webhook
    webhook = DiscordWebhook(url=webhook_url)
    author_name = config['config']['author_name']
    author_url = config['config']['author_url']
    author_icon_url = config['config']['author_icon_url']
    description = config['config']['description']

    embed = DiscordEmbed()
    embed.set_author(name=author_name, url=author_url, icon_url=author_icon_url)
    embed.title = post_title
    embed.description = post_content
    embed.add_embed_field(name=description, value=dc_link)

    webhook.add_embed(embed)

    # Send to Discord
    response = webhook.execute()
