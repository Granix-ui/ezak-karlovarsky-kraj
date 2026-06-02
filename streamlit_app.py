import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import re
import pandas as pd

st.set_page_config(page_title="E-ZAK Karlovarský kraj", layout="wide")
st.title("🛡️ E-ZAK Karlovarský kraj")
st.markdown("Prohledávání všech zadavatelů v kraji – aktivní zakázky")

# Seznam zadavatelů (můžeš ho libovolně upravovat)
zadavatele = [
    {"Název": "Karlovarský kraj", "URL": "https://ezak.kr-karlovarsky.cz/profile_display_1.html"},
    {"Název": "Krajská nemocnice Karlovy Vary", "URL": "https://ezak.kr-karlovarsky.cz/profile_display_2.html"},
    {"Název": "Nemocnice Cheb", "URL": "https://ezak.kr-karlovarsky.cz/profile_display_3.html"},
    {"Název": "Dětské centrum Karlovy Vary", "URL": "https://ezak.kr-karlovarsky.cz/profile_display_4.html"},
    {"Název": "Agentura krajského rozvoje", "URL": "https://ezak.kr-karlovarsky.cz/profile_display_5.html"},
    {"Název": "Císařské lázně", "URL": "https://ezak.kr-karlovarsky.cz/profile_display_6.html"},
    # Přidej další, pokud chceš
]

# Zobrazení tabulky se seznamem vyhledávaných zadavatelů
st.subheader("📋 Seznam prohledávaných zadavatelů")
df = pd.DataFrame(zadavatele)
st.dataframe(df, use_container_width=True, hide_index=True)

if st.button("🔄 Načíst aktivní zakázky", type="primary"):
    now = datetime.now()
    total_active = 0

    with st.spinner("Prohledávám všechny zadavatele..."):
        for item in zadavatele:
            base_url = item["URL"]
            nazev = item["Název"]

            try:
                # Přidáme filtr na aktivní zakázky
                url = base_url
                if "?" not in url:
                    url += "?state=active&archive=ACTUAL"
                else:
                    url += "&state=active&archive=ACTUAL"

                response = requests.get(url, timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "lxml")

                contract_links = soup.find_all("a", href=re.compile(r"contract_display_"))

                active = []
                for a in contract_links:
                    name = a.text.strip()
                    if not name: 
                        continue
                    link = urljoin(url, a["href"])

                    tr = a.find_parent("tr")
                    if not tr: 
                        continue
                    tds = tr.find_all("td")
                    if len(tds) < 5: 
                        continue

                    deadline_str = tds[-1].text.strip().replace("\xa0", " ")

                    try:
                        if ":" in deadline_str:
                            dl = datetime.strptime(deadline_str, "%d.%m.%Y %H:%M")
                        else:
                            dl = datetime.strptime(deadline_str, "%d.%m.%Y")
                        if dl > now:
                            active.append(f"[{name}]({link}) — lhůta {deadline_str}")
                    except:
                        continue

                if active:
                    st.markdown(f"### {nazev}")
                    for item in active:
                        st.markdown(f"- {item}", unsafe_allow_html=True)
                    total_active += len(active)

            except Exception:
                st.warning(f"{nazev} — nepodařilo se načíst")

    if total_active == 0:
        st.info("Momentálně nejsou žádné aktivní zakázky u těchto zadavatelů.")
    else:
        st.success(f"Celkem nalezeno {total_active} aktivních zakázek")

st.caption("E-ZAK Karlovarský kraj scanner")
