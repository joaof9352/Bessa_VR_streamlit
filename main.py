import streamlit as st
from backend import calcular_classificacao_final
import pandas as pd

# Streamlit app layout
st.title("Soccer League Standings Calculator")

# Dynamically create text inputs for match scores
matches = [
    ("Vila Real", "Tirsense"),
    ("Os Sandinenses", "Montalegre"),
    ("Vilar de Perdizes", "Marítimo B")
]

match_results = []
for home_team, away_team in matches:
    col1, col2 = st.columns(2)
    with col1:
        home_score = st.text_input(f"{home_team} (goals)", key=f"{home_team}_home")
    with col2:
        away_score = st.text_input(f"{away_team} (goals)", key=f"{away_team}_away")
    match_results.append((home_team, away_team, int(home_score or 0), int(away_score or 0)))

if st.button("Calcular tabela"):
    final_standings = calcular_classificacao_final(match_results)
    
    # Convert final_standings to a DataFrame for display
    data = {
        "Posição": [i+7 for i in range(len(final_standings))],
        "Team": [team for team, _ in final_standings],
        "Pontos": [stats['Pontos'] for _, stats in final_standings],
        "Vitórias": [stats['Vitórias'] for _, stats in final_standings],
        "GM": [stats['GM'] for _, stats in final_standings],
        "GS": [stats['GS'] for _, stats in final_standings]
    }
    standings_df = pd.DataFrame(data)
    
    # Display the DataFrame
    st.table(standings_df)