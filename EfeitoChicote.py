import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulação Efeito Chicote", layout="wide")
st.title("📦 Simulação do Efeito Chicote - Visualização da Amplificação de Pedidos")
st.markdown("Este app mostra como pequenas variações na demanda do cliente se amplificam na cadeia de suprimentos.")

# -------------------------
# Inputs
# -------------------------
st.sidebar.header("⚙️ Parâmetros da Simulação")
semanas = st.sidebar.number_input("Número de semanas", min_value=5, max_value=20, value=10, step=1)

st.sidebar.subheader("Estoques iniciais")
est_ini_v = st.sidebar.number_input("Varejista", min_value=0, value=50, step=1)
est_ini_cd = st.sidebar.number_input("Distribuidor/CD", min_value=0, value=80, step=1)
est_ini_f = st.sidebar.number_input("Fábrica", min_value=0, value=100, step=1)

st.sidebar.subheader("Demanda do cliente")
demanda_input = st.sidebar.text_input(
    f"Informe a demanda para {semanas} semanas (ex: 10,10,12,...)",
    value="10,10,10,15,20,18,22,20,25,20"
)

# -------------------------
# Processar entrada
# -------------------------
try:
    demanda_cliente = [int(x.strip()) for x in demanda_input.split(",")]
    if len(demanda_cliente) < semanas:
        demanda_cliente += [demanda_cliente[-1]] * (semanas - len(demanda_cliente))
except:
    st.error("Erro ao processar a demanda. Use apenas números separados por vírgula.")
    st.stop()

# -------------------------
# Criar DataFrame
# -------------------------
df = pd.DataFrame({'Semana': range(1, semanas+1)})
entidades = ['Varejista', 'CD', 'Fábrica']

for ent in entidades:
    df[f'{ent}_Demanda'] = 0
    df[f'{ent}_Estoque_Inicial'] = 0
    df[f'{ent}_Pedido'] = 0
    df[f'{ent}_Recebido'] = 0
    df[f'{ent}_Estoque_Final'] = 0

df.loc[0, 'Varejista_Estoque_Inicial'] = est_ini_v
df.loc[0, 'CD_Estoque_Inicial'] = est_ini_cd
df.loc[0, 'Fábrica_Estoque_Inicial'] = est_ini_f

# -------------------------
# Simulação (sem estoque de segurança)
# -------------------------
for i in range(semanas):
    # Varejista
    df.loc[i, 'Varejista_Demanda'] = demanda_cliente[i]
    df.loc[i, 'Varejista_Recebido'] = 0 if i==0 else df.loc[i-1, 'CD_Pedido']
    df.loc[i, 'Varejista_Pedido'] = max(0, df.loc[i, 'Varejista_Demanda'] - df.loc[i, 'Varejista_Estoque_Inicial'])
    df.loc[i, 'Varejista_Estoque_Final'] = df.loc[i, 'Varejista_Estoque_Inicial'] + df.loc[i, 'Varejista_Recebido'] - df.loc[i, 'Varejista_Demanda']
    if i < semanas-1:
        df.loc[i+1, 'Varejista_Estoque_Inicial'] = df.loc[i, 'Varejista_Estoque_Final']

    # CD
    df.loc[i, 'CD_Demanda'] = df.loc[i, 'Varejista_Pedido']
    df.loc[i, 'CD_Recebido'] = 0 if i==0 else df.loc[i-1, 'Fábrica_Pedido']
    df.loc[i, 'CD_Pedido'] = max(0, df.loc[i, 'CD_Demanda'] - df.loc[i, 'CD_Estoque_Inicial'])
    df.loc[i, 'CD_Estoque_Final'] = df.loc[i, 'CD_Estoque_Inicial'] + df.loc[i, 'CD_Recebido'] - df.loc[i, 'CD_Demanda']
    if i < semanas-1:
        df.loc[i+1, 'CD_Estoque_Inicial'] = df.loc[i, 'CD_Estoque_Final']

    # Fábrica
    df.loc[i, 'Fábrica_Demanda'] = df.loc[i, 'CD_Pedido']
    df.loc[i, 'Fábrica_Recebido'] = 0 if i==0 else df.loc[i-1, 'Fábrica_Pedido']
    df.loc[i, 'Fábrica_Pedido'] = max(0, df.loc[i, 'Fábrica_Demanda'] - df.loc[i, 'Fábrica_Estoque_Inicial'])
    df.loc[i, 'Fábrica_Estoque_Final'] = df.loc[i, 'Fábrica_Estoque_Inicial'] + df.loc[i, 'Fábrica_Recebido'] - df.loc[i, 'Fábrica_Demanda']
    if i < semanas-1:
        df.loc[i+1, 'Fábrica_Estoque_Inicial'] = df.loc[i, 'Fábrica_Estoque_Final']

# -------------------------
# Mostrar tabela
# -------------------------
# -------------------------
# Tabela amigável
# -------------------------
st.subheader("📊 Tabela Resumida da Cadeia de Suprimentos")

# Selecionar apenas colunas importantes
df_mostra = df[['Semana',
                'Varejista_Demanda', 'Varejista_Pedido',
                'CD_Pedido', 'Fábrica_Pedido']].copy()

# Renomear colunas para visualização
df_mostra.columns = ['Semana',
                     'Demanda Cliente (Varejista)', 'Pedido Varejista → CD',
                     'Pedido CD → Fábrica', 'Pedido Fábrica']

# Destacar aumento de pedidos com cores
def highlight_increase(val):
    if val > 20:  # pode ajustar o limite de destaque
        color = 'background-color: #ffcccc; font-weight: bold'
    else:
        color = ''
    return color

st.dataframe(df_mostra.style.applymap(highlight_increase, subset=['Pedido Varejista → CD', 'Pedido CD → Fábrica']))

# -------------------------
# Gráfico do efeito chicote
# -------------------------
st.subheader("📈 Demanda vs Pedidos ao longo da cadeia")

plt.figure(figsize=(10,6))
plt.plot(df['Semana'], df['Varejista_Demanda'], marker='o', label='Demanda Cliente (Varejista)')
plt.plot(df['Semana'], df['Varejista_Pedido'], marker='x', label='Pedido Varejista → CD')
plt.plot(df['Semana'], df['CD_Pedido'], marker='^', label='Pedido CD → Fábrica')
plt.xlabel("Semana")
plt.ylabel("Quantidade")
plt.title("Efeito Chicote: Amplificação de Pedidos")
plt.grid(True)
plt.legend()
st.pyplot(plt)

# -------------------------
# Explicação automática do efeito chicote
# -------------------------
st.subheader("📝 Por que o pedido do CD cresce tanto?")

st.markdown("""
O pedido do **CD** cresce muito em relação à demanda inicial do cliente devido ao **efeito chicote**:

1. **Demanda variável do cliente**: pequenas flutuações na demanda do varejista são percebidas como mudanças maiores pelo CD, que precisa repor seu estoque.
2. **Atraso de 1 semana**: cada pedido só chega na semana seguinte, então o CD tende a **pedir mais para não correr risco de falta**, amplificando a variação.
3. **Ajuste baseado no estoque**: mesmo sem estoque de segurança, o CD tenta suprir a demanda total do varejista. Se a demanda sobe, ele aumenta fortemente o pedido.
4. **Amplificação ao longo da cadeia**: esse efeito se repete na fábrica, tornando os pedidos cada vez mais voláteis à medida que se aproximam da produção.

💡 Resultado: **uma pequena variação na demanda do cliente gera grandes oscilações nos pedidos do CD e da fábrica**, evidenciando o clássico efeito chicote.
""")