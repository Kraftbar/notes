# Scrape asset links for an artist from Google Arts & Culture.
# From the former `paintings` repo. Set `url` to an artist entity page.
import requests
from bs4 import BeautifulSoup
artists='''
https://artsandculture.google.com/entity/leonardo-da-vinci/m04lg6
'''
url = ''

response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
# Find all <a> tags with href attribute that starts with "/asset/"
links = soup.find_all('a', href=lambda href: href and href.startswith('/asset/'))

# Extract and print the href values
for link in links:
    print(link['href'])
