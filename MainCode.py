import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Jogo da Cerveja", layout="wide")

# ===================== HEADER =====================
st.title("Jogo da Cerveja - Simulação do Efeito Chicote")
st.markdown("""
<!-- Espaço reservado para figura -->
<div style='width:100%; height:200px; border:2px dashed gray; display:flex; align-items:center; justify-content:center;'>
    <span>Insira aqui uma figura ilustrativa do Beer Game</span>
</div>
""", unsafe_allow_html=True)

st.markdown("Simule decisões semanais de pedidos e observe o efeito chicote ao longo da cadeia.")

# ===================== CONFIG =====================
st.sidebar.header("Configurações")
num_weeks = st.sidebar.slider("Número de semanas", 5, 30, 15)

entities = ["Varejista", "Atacadista", "Distribuidor", "Fábrica"]

# ===================== INPUT =====================
st.header("Entrada de pedidos semanais")

data = {}

for entity in entities:
    st.subheader(entity)
    orders = []
    for week in range(num_weeks):
        value = st.number_input(f"{entity} - Semana {week+1}", min_value=0, step=1, key=f"{entity}_{week}")
        orders.append(value)
    data[entity] = orders

# Demanda do cliente final
st.header("Demanda do cliente final")
demand = []
for week in range(num_weeks):
    value = st.number_input(f"Demanda - Semana {week+1}", min_value=0, step=1, key=f"demand_{week}")
    demand.append(value)

# ===================== DATAFRAME =====================
df = pd.DataFrame(data)
df["Demanda"] = demand

df.index = [f"Semana {i+1}" for i in range(num_weeks)]

# ===================== PLOTS =====================
st.header("Resultados")

fig, ax = plt.subplots()
for entity in entities:
    ax.plot(df.index, df[entity], marker='o', label=entity)

ax.plot(df.index, df["Demanda"], linestyle='--', marker='x', label="Demanda Cliente")

ax.set_xticks(range(len(df.index)))
ax.set_xticklabels(df.index, rotation=45)
ax.set_title("Efeito Chicote - Pedidos ao longo das semanas")
ax.set_ylabel("Quantidade")
ax.legend()

st.pyplot(fig)

# ===================== VARIABILIDADE =====================
st.header("Análise do efeito chicote")

variability = {entity: pd.Series(data[entity]).std() for entity in entities}
variability["Demanda"] = pd.Series(demand).std()

var_df = pd.DataFrame(list(variability.items()), columns=["Entidade", "Desvio Padrão"])

st.dataframe(var_df)

st.markdown("""
Quanto maior o desvio padrão ao subir na cadeia, maior o efeito chicote.
""")

# ===================== GITHUB INSTRUCTIONS =====================
st.header("Como rodar via GitHub")

st.markdown("""
1. Crie um repositório no GitHub
2. Salve este arquivo como `app.py`
3. Crie um `requirements.txt` com:
```
streamlit
pandas
matplotlib
```
4. Rode localmente com:
```
streamlit run app.py
```
5. Ou publique no Streamlit Cloud conectando ao repositório.
""")
