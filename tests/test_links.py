from html.parser import HTMLParser
from urllib.parse import unquote,urlsplit

class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k in ['href','src'] and v:self.links.append(v)

def test_local_links_and_assets(root):
    for page in root.glob('*.html'):
        parser=Links();parser.feed(page.read_text(encoding='utf8'))
        for href in parser.links:
            u=urlsplit(href)
            if u.scheme or u.netloc or not u.path:continue
            assert (page.parent/unquote(u.path)).is_file(),(page.name,href)
