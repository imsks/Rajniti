import json
import re
import time

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://prsindia.org"


def extract_number(text):
    nums = re.findall(r"\d+", text)
    return int(nums[0]) if nums else 0


def extract_stats(soup):
    attendance = 0
    questions = 0
    debates = 0

    # 🔥 look for text labels directly
    all_text = soup.get_text(" ", strip=True).lower()

    # attendance
    if "attendance" in all_text:
        idx = all_text.find("attendance")
        snippet = all_text[idx : idx + 100]
        attendance = extract_number(snippet)

    # questions
    if "questions" in all_text:
        idx = all_text.find("questions")
        snippet = all_text[idx : idx + 100]
        questions = extract_number(snippet)

    # debates
    if "debates" in all_text:
        idx = all_text.find("debates")
        snippet = all_text[idx : idx + 100]
        debates = extract_number(snippet)

    return {"attendance": attendance, "questions": questions, "debates": debates}


def scrape_mp(link):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(link, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    name = link.split("/")[-1].replace("-", " ").title()

    perf = extract_stats(soup)

    return {"name": name, "performance": perf}


all_mps = []

# 🔥 FIXED pagination
for page in range(1, 60):
    url = f"{BASE_URL}/mptrack?page={page}&per-page=20&MpTrackSearch%5Bloc_sabha%5D=18th_lok_sabha"

    print(f"Page {page}")

    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    links = []

    for a in soup.find_all("a", href=True):
        if "/mptrack/18th-lok-sabha/" in a["href"]:
            links.append(BASE_URL + a["href"])

    links = list(set(links))

    print("Found:", len(links))

    if len(links) == 0:
        break

    for link in links:
        try:
            print("Scraping:", link)
            mp = scrape_mp(link)
            all_mps.append(mp)
        except Exception as e:
            print(f"Error scraping {link}: {e}")
            continue

        time.sleep(0.5)


# remove duplicates by name
unique = {}
for mp in all_mps:
    unique[mp["name"]] = mp

final_data = list(unique.values())


with open("../app/data/performance.json", "w", encoding="utf-8") as f:
    json.dump(final_data, f, indent=2, ensure_ascii=False)


print("✅ DONE:", len(final_data))
