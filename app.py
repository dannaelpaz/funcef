import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="Correção Previdenciária", layout="wide")

st.title("📊 Planejamento de Correção Previdenciária")
st.subheader("💼 Análise dos aportes vs. aporte ideal de 12%")

# ✅ Função para gerar o dataframe inicial
@st.cache_data
def carregar_dados_iniciais():
    periodo = pd.date_range(start="2021-03-01", end="2025-06-01", freq="MS").strftime("%Y-%m").tolist()

    aportes_participante = [
        288, 150, 150, 150, 150, 150, 150, 150, 166.5, 249.15, 712.8, 712.8, 
        594, 297, 297, 467.93, 342.15, 342.15, 342.15, 342.15, 342.15, 342.15, 
        369.55, 369.55, 369.55, 369.55, 369.55, 535.94, 1386.12, 1386.12, 577.55, 
        468.52, 369.55, 369.55, 369.55, 386.5, 386.5, 386.5, 386.5, 386.5, 693.06, 
        386.5, 386.5, 386.5, 404.45, 404.45, 404.45, 404.45, 624.51, 624.51, 632.1
    ]

    while len(aportes_participante) < len(periodo):
        aportes_participante.append(0)

    remuneracao_base = [valor / 0.05 for valor in aportes_participante]
    df = pd.DataFrame({
        "Mês/Ano": periodo,
        "Remuneração Bruta (Base)": remuneracao_base,
        "Aportado": aportes_participante
    })
    return df

# Carregar dados iniciais
df = carregar_dados_iniciais()

# ✅ Edição da remuneração bruta
st.subheader("✍️ Edite sua remuneração bruta, se necessário")
df_editado = st.data_editor(
    df,
    column_config={
        "Remuneração Bruta (Base)": st.column_config.NumberColumn(
            "Remuneração Bruta (Base)", min_value=0, step=100
        )
    },
    use_container_width=True,
    key="editor"
)

# ✅ Cálculo dos campos financeiros
aporte_ideal = df_editado["Remuneração Bruta (Base)"] * 0.12
diferenca = aporte_ideal - df_editado["Aportado"]

rentabilidade_mensal = 0.0085  # 0.85% ao mês
hoje = datetime(2025, 6, 1)
datas = pd.date_range(start="2021-03-01", periods=len(df_editado), freq='MS')
meses_corrigir = [(hoje.year - data.year) * 12 + (hoje.month - data.month) for data in datas]

correcao = [dif * ((1 + rentabilidade_mensal) ** meses) if dif > 0 else 0
            for dif, meses in zip(diferenca, meses_corrigir)]

total_corrigido = [dif + cor if dif > 0 else 0 for dif, cor in zip(diferenca, correcao)]

# ✅ Adicionando colunas calculadas
df_editado["12% Ideal"] = aporte_ideal
df_editado["Diferença (Débito)"] = diferenca
df_editado["Correção Monetária"] = correcao
df_editado["Total Corrigido"] = total_corrigido

st.subheader("📜 Resultado da Análise Atualizada")
st.dataframe(df_editado, use_container_width=True)

# ✅ Total geral
total_devido = df_editado["Total Corrigido"].sum()
st.subheader("💰 Total necessário para correção hoje:")
st.metric(label="Total Corrigido", value=f"R$ {total_devido:,.2f}")

# ✅ Gráfico
st.subheader("📈 Evolução dos Aportes e Débitos Corrigidos")
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df_editado["Mês/Ano"], df_editado["Aportado"], label="Aportado", marker="o")
ax.plot(df_editado["Mês/Ano"], df_editado["12% Ideal"], label="Ideal (12%)", marker="s")
ax.plot(df_editado["Mês/Ano"], df_editado["Total Corrigido"], label="Débito Corrigido", marker="x")
ax.set_xticks(df_editado["Mês/Ano"][::4])
ax.set_xticklabels(df_editado["Mês/Ano"][::4], rotation=45)
ax.set_ylabel("R$ Valor")
ax.set_title("Aportes, Ideal e Débito Corrigido ao longo do tempo")
ax.legend()
st.pyplot(fig)

# ✅ Download da base editada
st.subheader("⬇️ Baixar Dados Editados")
csv = df_editado.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Baixar CSV da Análise",
    data=csv,
    file_name='planejamento_previdencia_editado.csv',
    mime='text/csv',
)

# ✅ Simples armazenamento local (opcional)
if st.button("💾 Salvar Dados Localmente"):
    df_editado.to_csv("dados_salvos.csv", index=False)
    st.success("Dados salvos com sucesso no arquivo 'dados_salvos.csv'.")
