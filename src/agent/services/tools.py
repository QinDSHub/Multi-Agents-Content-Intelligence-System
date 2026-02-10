import requests
from bs4 import BeautifulSoup

def google_search(query, max_results=3):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        resp = requests.get(
            "https://www.google.com/search",
            headers=headers,
            params={"q": query},
            timeout=15,
        )
        resp.raise_for_status()
    except requests.RequestException:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    
    results = []
    for g in soup.find_all('div', class_='tF2Cxc')[:max_results]:
        title = g.find('h3').text if g.find('h3') else ""
        link = g.find('a')['href'] if g.find('a') else ""
        snippet = g.find('span', class_='aCOpRe').text if g.find('span', class_='aCOpRe') else ""
        results.append({"title": title, "link": link, "snippet": snippet})
    
    return results

