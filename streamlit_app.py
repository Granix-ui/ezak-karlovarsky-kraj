import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

st.set_page_config(page_title="E-ZAK Karlovarský kraj", layout="wide")
st.title("🛡️ E-ZAK Karlovarský kraj")
st.markdown("Prohledávání všech zadavatelů v kraji – aktivní zakázky")

if st.button("🔄 Načíst všechny aktivní zakázky", type="primary"):
    base_url = "https://ezak.kr-karlovarsky.cz/profile_index.html"
    
    with st.spinner("Načítám seznam všech zadavatelů v Karlovarském kraji..."):
        try:
            response = requests.get(base_url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            # Najdeme všechny odkazy na profily zadavatelů
            profile_links = soup.find_all("a", href=re.compile(r"profile_display_\d+"))

            total_active = 0

            for a in profile_links:
                profile_name = a.text.strip()
                if not profile_name or len(profile_name) < 3:
                    continue
                
                profile_url = urljoin(base_url, a["href"])
                
                # Přidáme parametr pro aktivní zakázky
                if "?" in profile_url:
                    profile_url += "&state=active&archive=ACTUAL"
                else:
                    profile_url += "?state=active&archive=ACTUAL"

                try:
                    resp = requests.get(profile_url, timeout=12)
                    soup2 = BeautifulSoup(resp.text, "lxml")

                    contract_links = soup2.find_all("a", href=re.compile(r"contract_display_"))

                    active = []
                    for link in contract_links:
                        name = link.text.strip()
                        if not name: continue
                        full_link = urljoin(profile_url, link["href"])

                        # Najdeme lhůtu
                        tr = link.find_parent("tr")
                        if tr:
                            tds = tr.find_all("td")
                            if len(tds) > 4:
                                deadline_str = tds[-1].text.strip().replace("\xa0", " ")
                                try:
                                    if ":" in deadline_str:
                                        dl = datetime.strptime(deadline_str, "%d.%m.%Y %H:%M")
                                    else:
                                        dl = datetime.strptime(deadline_str, "%d.%m.%Y")
                                    if dl > datetime.now():
                                        active.append(f"[{name}]({full_link}) — lhůta {deadline_str}")
                                except:
                                    continue

                    if active:
                        st.markdown(f"### {profile_name}")
                        for item in active:
                            st.markdown(f"- {item}", unsafe_allow_html=True)
                        total_active += len(active)

                except:
                    continue

            if total_active == 0:
                st.info("Momentálně nejsou žádné aktivní zakázky v Karlovarském kraji.")
            else:
                st.success(f"Celkem nalezeno {total_active} aktivních zakázek")

        except Exception as e:
            st.error(f"Chyba při načítání: {e}")

st.caption("Specializovaný scanner pro Karlovarský kraj • E-ZAK")
