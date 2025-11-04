import requests
from bs4 import BeautifulSoup

url = "https://www.olx.pt/imoveis/apartamento-casa-a-venda/"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(r.text, "html.parser")

for ad in soup.select("div[data-cy='l-card']"):
    title = ad.select_one("h6").get_text(strip=True)
    price = ad.select_one("p[data-testid='ad-price']").get_text(strip=True)
    link = ad.select_one("a")["href"]
    print(title, price, "https://www.olx.pt" + link)
