import streamlit as st
from backend import ClassificacaoCalculator
import pandas as pd

st.set_page_config(
    page_title="CP - A",
    page_icon=":robot_face:",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Streamlit app layout
st.markdown("<h1 style='text-align: center;'>Campeonato Portugal - Série A</h1>", unsafe_allow_html=True)
st.header("", divider='rainbow')

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

if st.button("Calcular tabela", use_container_width=True):
    calc = ClassificacaoCalculator()
    final_standings = calc.calcular_classificacao_final(match_results)
    
    # Convert final_standings to a DataFrame for display
    data = {
        "Posição": [i+7 for i in range(len(final_standings))],
        "Team": [team for team, _ in final_standings],
        "Vitórias": [stats['Vitórias'] for _, stats in final_standings],
        "GM": [stats['GM'] for _, stats in final_standings],
        "GS": [stats['GS'] for _, stats in final_standings],
        "DG": [stats['GM'] - stats['GS'] for _, stats in final_standings],
        "Pontos": [stats['Pontos'] for _, stats in final_standings]
    }
    standings_df = pd.DataFrame(data)
    
    def highlight_last_two_rows(s):
        return ['background-color: red' if i >= len(s) - 2 else '' for i in range(len(s))]
    styled_df = standings_df.style.apply(highlight_last_two_rows, subset=['Team', 'Pontos', 'Vitórias', 'GM', 'GS', 'DG', 'Posição'])
    
    # Exibir o DataFrame com estilo
    st.dataframe(styled_df, hide_index=True, use_container_width=True)