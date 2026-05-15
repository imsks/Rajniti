import requests
from bs4 import BeautifulSoup

BASE_URL = "https://prsindia.org"

all_links = []

for page in range(1, 60):  # start from 1
    url = f"https://prsindia.org/mptrack?page={page}&per-page=50&MpTrackSearch%5Bloc_sabha%5D=18th_lok_sabha"

    print(f"Fetching page {page}")

    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    found = 0

    for a in soup.find_all("a", href=True):
        if "/mptrack/18th-lok-sabha/" in a["href"]:
            link = BASE_URL + a["href"]
            all_links.append(link)
            found += 1

    print("Found:", found)

    # stop if no more MPs
    if found == 0:
        break

# remove duplicates
all_links = list(set(all_links))

print("Total MPs:", len(all_links))

# save links
with open("prs_links.txt", "w") as f:
    for link in all_links:
        f.write(link + "\n")

print("✅ DONE")
