from bs4 import BeautifulSoup
from RedisCache.cache import redis_cache


@redis_cache(hash_use=True)
def get_user_links_by_text(*, text):
    if text:
        soup = BeautifulSoup(text, 'html.parser')
        all_a = soup.find_all('a')

        links = [a.attrs.get('href') for a in all_a]
        user_links = []
        for link in links:
            l_link = link.lower()
            if ('t.me/' in l_link
               and 't.me/+' not in l_link
               and 'joinchat' not in l_link
               and not l_link.endswith('bot')
               and not l_link.endswith('chat')):

                user_links.append(link)

        return user_links
    return []