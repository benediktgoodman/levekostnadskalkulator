import streamlit as st

def main():
    st.title("Velkommen til boligkostnadskalkulatoren")
    st.write("""
    Skal du ut og kjøpe bolig? Da kan det være lurt å finne ut hvor mye det vil koste deg på forhånd.
    
    Mange kalkulatorer der ute viser bare en del av bildet. De tar ofte ikke hensyn til hvordan 
    lånekostnadene endrer seg når renten stiger eller synker, eller de overser andre viktige 
    faktorer som påvirker de totale boligkostnadene.
    
    Denne boligkostnadskalkulatoren er annerledes. Den har som mål å vise deg "hele sannheten" om 
    hvor mye du faktisk kan ende opp med å betale når alt er tatt i betraktning.
    
    Med denne kalkulatoren kan du:
    
    - Se hvordan rentendringer påvirker dine månedlige kostnader
    - Få en fullstendig oversikt over alle kostnader knyttet til boligkjøp og -eie
    - Utforske ulike scenarier for boligpriser, egenkapital og eierandeler
    - Beregne kostnader for to personer som bor sammen
    - Visualisere kostnadsfordelingen med interaktive diagrammer
    
    Kom i gang ved å velge 'Bygg ditt eget kostnadsscenario' i menyen til venstre!
    """)

if __name__ == "__main__":
    main()