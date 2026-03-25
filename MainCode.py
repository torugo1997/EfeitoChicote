import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Jogo da Cerveja (Interativo)", layout="wide")

# ===================== HEADER =====================
st.title("Jogo da Cerveja - Efeito Chicote (Aula 26/03)")

# ===================== CONFIG =====================
NUM_WEEKS = 10
LEAD_TIME = 2
INITIAL_STOCK = 12
TARGET_STOCK = 12

entities = ["Varejista", "Atacadista", "Distribuidor", "Fábrica"]

# ===================== SESSION STATE =====================
if "orders" not in st.session_state:
    st.session_state.orders = {e: [None]*NUM_WEEKS for e in entities}

if "inventory" not in st.session_state:
    st.session_state.inventory = {e: [INITIAL_STOCK]*NUM_WEEKS for e in entities}

if "backlog" not in st.session_state:
    st.session_state.backlog = {e: [0]*NUM_WEEKS for e in entities}

if "incoming" not in st.session_state:
    st.session_state.incoming = {e: [0]*(NUM_WEEKS+LEAD_TIME) for e in entities}

# Demanda real (oculta)
if "true_demand" not in st.session_state:
    st.session_state.true_demand = [4,4,4,4,8,8,8,8,8,8]

# Demanda visível (liberada aos poucos)
if "visible_demand" not in st.session_state:
    st.session_state.visible_demand = [None]*NUM_WEEKS
    st.session_state.visible_demand[0] = st.session_state.true_demand[0]

# ===================== SIDEBAR =====================
st.sidebar.header("Selecione sua entidade")
entity = st.sidebar.selectbox("Entidade", entities)
entity_index = entities.index(entity)

st.header(f"Decisões - {entity}")

# ===================== VISÃO LIMITADA =====================
st.subheader("Informação disponível")

if entity_index == 0:
    st.write("Demanda conhecida até agora:")
    st.write(st.session_state.visible_demand)
else:
    prev_entity = entities[entity_index - 1]
    st.write(f"Pedidos recebidos de {prev_entity}:")
    st.write(st.session_state.orders[prev_entity])

# ===================== LOOP =====================
for week in range(NUM_WEEKS):
    st.subheader(f"Semana {week+1}")

    # Pode decidir?
    if entity_index == 0:
        can_decide = True
    else:
        prev_entity = entities[entity_index - 1]
        can_decide = st.session_state.orders[prev_entity][week] is not None

    if not can_decide:
        st.info("Aguardando etapa anterior...")
        continue

    # ===================== DINÂMICA =====================
    received = st.session_state.incoming[entity][week]

    if week == 0:
        prev_inventory = INITIAL_STOCK
        prev_backlog = 0
    else:
        prev_inventory = st.session_state.inventory[entity][week-1]
        prev_backlog = st.session_state.backlog[entity][week-1]

    if entity_index == 0:
        demand = st.session_state.visible_demand[week] or 0
    else:
        prev_entity = entities[entity_index - 1]
        demand = st.session_state.orders[prev_entity][week] or 0

    total_demand = demand + prev_backlog

    served = min(prev_inventory + received, total_demand)
    backlog = total_demand - served
    inventory = prev_inventory + received - served

    st.session_state.inventory[entity][week] = inventory
    st.session_state.backlog[entity][week] = backlog

    # ===================== INFO =====================
    st.write(f"Recebido: {received}")
    st.write(f"Estoque: {inventory}")
    st.write(f"Backlog: {backlog}")
    st.write(f"Demanda enfrentada: {total_demand}")

    # ===================== SUGESTÃO =====================
    # suggested_order = max(0, TARGET_STOCK - inventory + backlog + demand)
    # st.info(f"Sugestão de pedido: {suggested_order}")

    # ===================== INPUT =====================
    if st.session_state.orders[entity][week] is None:
        value = st.number_input(
            f"Pedido na semana {week+1}",
            min_value=0,
            step=1,
            key=f"{entity}_{week}"
        )

        if st.button(f"Confirmar semana {week+1}", key=f"btn_{entity}_{week}"):
            st.session_state.orders[entity][week] = value

            # Atualiza pipeline
            if entity_index < len(entities) - 1:
                next_entity = entities[entity_index + 1]
                if week + LEAD_TIME < NUM_WEEKS:
                    st.session_state.incoming[next_entity][week + LEAD_TIME] += value

            # 🔥 LIBERA PRÓXIMA DEMANDA APENAS NA FÁBRICA
            if entity == "Fábrica" and week + 1 < NUM_WEEKS:
                st.session_state.visible_demand[week + 1] = st.session_state.true_demand[week + 1]

            st.success("Pedido registrado!")

    else:
        st.write(f"Pedido registrado: {st.session_state.orders[entity][week]}")

# ===================== RESULTADOS =====================
all_filled = all(
    all(v is not None for v in st.session_state.orders[e])
    for e in entities
)

if all_filled:
    st.header("Resultados finais")

    df = pd.DataFrame(st.session_state.orders)
    df["Demanda Real"] = st.session_state.true_demand
    df.index = [f"Semana {i+1}" for i in range(NUM_WEEKS)]

    st.dataframe(df)

    # ===================== PEDIDOS =====================
    fig, ax = plt.subplots()

    for e in entities:
        ax.plot(df.index, df[e], marker='o', label=e)

    ax.plot(df.index, df["Demanda Real"], linestyle='--', marker='x', label="Demanda")

    ax.set_title("Efeito Chicote - Pedidos")
    ax.legend()
    plt.xticks(rotation=45)

    st.pyplot(fig)

    # ===================== ESTOQUE =====================
    st.subheader("Estoque")

    fig2, ax2 = plt.subplots()
    for e in entities:
        ax2.plot(st.session_state.inventory[e], marker='o', label=e)

    ax2.legend()
    st.pyplot(fig2)

    # ===================== BACKLOG =====================
    st.subheader("Backlog")

    fig3, ax3 = plt.subplots()
    for e in entities:
        ax3.plot(st.session_state.backlog[e], marker='o', label=e)

    ax3.legend()
    st.pyplot(fig3)

    # ===================== VARIABILIDADE =====================
    st.header("Análise do efeito chicote")

    variability = {e: pd.Series(st.session_state.orders[e]).std() for e in entities}
    variability["Demanda"] = pd.Series(st.session_state.true_demand).std()

    st.dataframe(pd.DataFrame(list(variability.items()), columns=["Entidade", "Desvio Padrão"]))

else:
    st.warning("Aguardando todas as decisões para exibir os resultados finais...")

# ===================== OBS =====================
st.markdown("""
⚠️ IMPORTANTE:
- Lead time = 2 semanas  
- Demanda é liberada com atraso (somente após decisão da fábrica)  
- Cada entidade vê apenas o elo anterior  
- O efeito chicote emerge naturalmente  
""")
