# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 2024

@author: Benedikt Goodman
"""

import streamlit as st


def main():
    st.set_page_config(layout="centered")
    st.title("Velkommen til levekostnadskalkulatoren")
    st.write("""
🏠💰 Boligdrømmer? La oss snakke penger!

Dyrtiden preger oss alle. Derfor er det nå ekstra viktig å ta gode finansielle valg.

🔮 Dette verkøyet hjelper deg å se inn i din økonomiske fremtid:
- Hvor mye koster det egentlig i måneden å eie en gitt bolig?
- Hva slags rentesvingninger tåler du?
- Hvordan blir det når strømprisen øker?

🛠️ Verktøykassen din for smart boligkjøp:
- 📈 Se rentesvingningenes effekt på lommeboken din
- 📊 Få full oversikt over alle kostnader
- 🏘️ Utforsk ulike boligscenarier
- 👫 Beregn kostnader for deg og partneren
- 🎨 Se alt i fargerike, interaktive diagrammer

🚀 Klar for å dykke inn?
""")


if __name__ == "__main__":
    main()
