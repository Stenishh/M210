import numpy as np
import streamlit as st
import pandas as pd
from pulp import LpMaximize, LpMinimize, LpProblem, LpVariable, LpStatus, value

st.set_page_config(
    page_title="Calculadora Simplex - PPL",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================== ESTILOS CSS ====================

st.markdown("""
<style>
    /* Cabeçalho principal */
    .main-header {
        font-size: 2.2rem;
        font-weight: 600;
        color: #1f77b4;
        text-align: center;
        padding: 0.5rem 0;
        margin-bottom: 0.3rem;
    }
    
    /* Subtítulo */
    .subtitle {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    /* Sub-cabeçalhos */
    .sub-header {
        font-size: 1.4rem;
        font-weight: 600;
        color: #333;
        padding: 0.5rem 0;
        border-bottom: 2px solid #e0e0e0;
        margin: 1rem 0 0.8rem 0;
    }
    
    /* Card de resultados - simples e clean */
    .result-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
    
    /* Caixa de métrica - versão simples */
    .metric-card {
        background: #f8f9fa;
        border: 2px solid #1f77b4;
        border-radius: 8px;
        padding: 1.2rem;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.3rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666;
    }
    
    /* Caixa de sucesso */
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-left: 4px solid #28a745;
        padding: 1rem 1.2rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    /* Caixa de aviso */
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-left: 4px solid #ffc107;
        padding: 1rem 1.2rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    /* Caixa de exemplo */
    .example-box {
        background-color: #f0f8ff;
        border: 1px solid #cce5ff;
        border-radius: 4px;
        padding: 1rem;
        font-size: 0.9rem;
    }
    
    /* Remove espaçamento extra */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Botões simples e clean */
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        font-weight: 500;
        border: none;
        padding: 0.6rem 1.5rem;
        border-radius: 4px;
        font-size: 1rem;
        transition: background-color 0.2s;
    }
    
    .stButton>button:hover {
        background-color: #1557a0;
    }
</style>
""", unsafe_allow_html=True)


# ==================== FUNÇÕES PRINCIPAIS ====================

def simplex(funcObj, restricoes, constantes, operadores, num_variables, tipo_otimizacao):
    """
    Resolve Problemas de Programação Linear usando biblioteca PuLP
    Agora suporta restrições do tipo ≤, ≥ e =.
    Retorna também um tableau simplificado para exibição (com uma coluna de folga/sobra por restrição).
    Observação: o tableau aqui é uma representação simples para visualização.
    """
    try:
        # Define o tipo de problema
        if tipo_otimizacao == "Maximizar":
            prob = LpProblem("PPL", LpMaximize)
        else:
            prob = LpProblem("PPL", LpMinimize)
        
        # Cria as variáveis de decisão (não-negativas)
        vars = [LpVariable(f"x{i+1}", lowBound=0) for i in range(num_variables)]
        
        # Define a função objetivo
        prob += sum([funcObj[i] * vars[i] for i in range(num_variables)]), "FuncaoObjetivo"
        
        # Adiciona as restrições conforme o operador escolhido
        for i in range(len(constantes)):
            expr = sum([restricoes[i][j] * vars[j] for j in range(num_variables)])
            op = operadores[i]
            if op == "≤":
                prob += (expr <= constantes[i], f"Restricao_{i+1}")
            elif op == "≥":
                prob += (expr >= constantes[i], f"Restricao_{i+1}")
            else:  # "="
                prob += (expr == constantes[i], f"Restricao_{i+1}")
        
        # Resolve o problema
        status = prob.solve()
        
        # Verifica se encontrou solução ótima
        if LpStatus[prob.status] != "Optimal":
            st.error(f"❌ **Não foi possível encontrar solução ótima.**\n\nStatus: {LpStatus[prob.status]}")
            if LpStatus[prob.status] == "Infeasible":
                st.warning("⚠️ O problema é **inviável** - as restrições são inconsistentes.")
            elif LpStatus[prob.status] == "Unbounded":
                st.warning("⚠️ O problema é **ilimitado** - a função objetivo pode crescer indefinidamente.")
            return None, None, None, None
        
        # Extrai a solução
        solucao = np.array([value(var) for var in vars])
        
        # Valor ótimo
        valorOtimo = value(prob.objective)
        
        # Preços-sombra (dual values das restrições)
        precoSombra = []
        for i in range(len(constantes)):
            constraint = prob.constraints.get(f"Restricao_{i+1}")
            if constraint and hasattr(constraint, 'pi') and constraint.pi is not None:
                precoSombra.append(constraint.pi)
            else:
                precoSombra.append(0.0)
        precoSombra = np.array(precoSombra)
        
        # Monta um tableau simplificado para exibição
        # Colunas: variáveis de decisão | uma coluna 's_i' por restrição (folga/sobra) | LD
        n_cons = len(constantes)
        tableau = np.zeros((n_cons + 1, num_variables + n_cons + 1))
        
        # Preenche com valores das restrições e coluna de folga/sobra
        for i in range(n_cons):
            for j in range(num_variables):
                tableau[i, j] = restricoes[i][j]
            # para <= colocamos +1 na coluna de folga, para >= colocamos -1, para = colocamos 0
            if operadores[i] == "≤":
                tableau[i, num_variables + i] = 1
            elif operadores[i] == "≥":
                tableau[i, num_variables + i] = -1
            else:
                tableau[i, num_variables + i] = 0
            tableau[i, -1] = constantes[i]
        
        # Linha da função objetivo (coeficientes)
        for i, coef in enumerate(funcObj):
            tableau[-1, i] = coef
        tableau[-1, -1] = valorOtimo
        
        return solucao, valorOtimo, precoSombra, tableau
        
    except Exception as e:
        st.error(f"❌ **Erro ao resolver o problema:**\n\n{str(e)}")
        return None, None, None, None


def validar_entrada(funcObj, restricoes, constantes, operadores):
    """Valida os dados de entrada do problema"""
    erros = []
    
    # Verifica se os coeficientes da função objetivo são números válidos
    if not all(isinstance(c, (int, float, np.floating, np.integer)) for c in funcObj):
        erros.append("⚠️ Coeficientes da função objetivo devem ser numéricos")
    
    # Verifica se há pelo menos uma restrição
    if len(restricoes) == 0:
        erros.append("⚠️ Deve haver pelo menos uma restrição")
    
    # Verifica se todas as restrições têm o mesmo número de coeficientes
    if restricoes and not all(len(r) == len(restricoes[0]) for r in restricoes):
        erros.append("⚠️ Todas as restrições devem ter o mesmo número de variáveis")
    
    # Verifica consistência entre tamanhos
    if not (len(constantes) == len(restricoes) == len(operadores)):
        erros.append("⚠️ Número de constantes, operadores e restrições deve ser o mesmo")
    
    # Verifica os operadores
    if any(op not in ["≤", "≥", "="] for op in operadores):
        erros.append("⚠️ Operadores inválidos detectados")
    
    # Nota sobre constantes negativas (permitidas, mas pode gerar inviabilidade)
    # Não bloqueamos, apenas avisamos
    if any((not isinstance(c, (int, float, np.floating, np.integer))) for c in constantes):
        erros.append("⚠️ As constantes (lado direito) devem ser numéricas")
    
    return erros


# ==================== INTERFACE PRINCIPAL ====================

# Cabeçalho
st.markdown('<div class="main-header">📊 Calculadora de Programação Linear</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Resolva problemas de otimização com o Método Simplex usando PuLP</div>', unsafe_allow_html=True)

# Informações sobre a ferramenta
with st.expander("📚 **Sobre esta Calculadora** | Clique para expandir", expanded=False):
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.markdown("""
        ### 🎯 **O que é Programação Linear?**
        
        A **Programação Linear (PPL)** é uma técnica matemática para otimizar 
        (maximizar ou minimizar) uma função objetivo linear, sujeita a um conjunto 
        de restrições lineares.
        
        **Aplicações comuns:**
        - 📦 Logística e distribuição
        - 🏭 Planejamento de produção
        - 💼 Alocação de recursos
        - 📊 Otimização de portfólio
        - 🚚 Roteirização de veículos
        """)
    
    with col_info2:
        st.markdown("""
        ### ⚙️ **Características desta Calculadora**
        
        - ✅ Suporta **2, 3 ou 4 variáveis** de decisão
        - ✅ Problemas de **Maximização** e **Minimização**
        - ✅ Restrições do tipo **≤**, **≥** e **=**
        - ✅ Calcula **ponto ótimo** e **valor ótimo**
        - ✅ Determina **preços-sombra** (shadow prices)
        - ✅ Exibe **tableau simplificado** do Simplex
        - ✅ Validação automática de entrada
        - ✅ Interface intuitiva e visual
        """)
    
    st.markdown("---")
    st.markdown("""
    ### 📖 **Como usar:**
    
    1. **Configure** o número de variáveis e restrições na barra lateral
    2. **Nomeie** as variáveis (opcional) para facilitar a interpretação
    3. **Insira** os coeficientes da função objetivo
    4. **Defina** as restrições com seus coeficientes, tipo e limites
    5. **Clique** em "Calcular Solução Ótima" para obter os resultados
    6. **Analise** os resultados: ponto ótimo, valor ótimo, preços-sombra e tableau
    """)

st.markdown("---")


# ==================== SIDEBAR - CONFIGURAÇÕES ====================

st.sidebar.markdown("### ⚙️ **Configurações do Problema**")
st.sidebar.markdown("---")

# Tipo de Otimização
tipo_otimizacao = st.sidebar.radio(
    "🎯 **Tipo de Otimização**",
    options=["Maximizar", "Minimizar"],
    index=0,
    help="Escolha se deseja maximizar ou minimizar a função objetivo"
)

st.sidebar.markdown("---")

# Número de Variáveis
num_variables = st.sidebar.selectbox(
    "🔢 **Número de Variáveis de Decisão**",
    options=[2, 3, 4],
    index=0,
    help="Escolha quantas variáveis de decisão (x₁, x₂, x₃, x₄) o problema terá"
)

# Número de Restrições
num_constraints = st.sidebar.number_input(
    "🔒 **Número de Restrições**",
    min_value=1,
    max_value=10,
    value=2,
    step=1,
    help="Quantidade de restrições do problema (máximo 10)"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏷️ **Nomear Variáveis (Opcional)**")
st.sidebar.caption("Personalize os nomes das variáveis para facilitar a interpretação")

nomes_variaveis = []
for i in range(4):  # Sempre 4 para cobrir todas as possibilidades
    if i < num_variables:
        nome = st.sidebar.text_input(
            f"Variável x{i+1}",
            value=f"x{i+1}",
            key=f"nome_var_{i}",
            max_chars=15,
            help=f"Nome personalizado para x{i+1} (máx. 15 caracteres)"
        )
        nomes_variaveis.append(nome if nome.strip() else f"x{i+1}")
    else:
        nomes_variaveis.append(f"x{i+1}")

st.sidebar.markdown("---")

# Exemplo de Problema
with st.sidebar.expander("💡 **Exemplo: Problema de Produção**"):
    st.markdown("""
    <div class="example-box">
    <strong>📦 Fábrica de Eletrodomésticos</strong><br><br>
    
    <strong>Maximizar:</strong> Z = 100x₁ + 80x₂<br>
    <small>(Lucro por Geladeira e Fogão)</small><br><br>
    
    <strong>Sujeito a:</strong><br>
    • <code>2x₁ + 1x₂ ≤ 40</code> (Horas de montagem)<br>
    • <code>1x₁ + 2x₂ ≤ 50</code> (Horas de teste)<br>
    • <code>x₁, x₂ ≥ 0</code> (Não-negatividade)<br><br>
    
    <strong>Solução Esperada:</strong><br>
    • x₁ = 10, x₂ = 20<br>
    • Z* = 2600
    </div>
    """, unsafe_allow_html=True)

# Formato do Problema
st.sidebar.markdown("---")
st.sidebar.markdown("### 📝 **Formato Geral do Problema**")
st.sidebar.info(f"""
**{tipo_otimizacao}:** Z = c₁{nomes_variaveis[0]} + c₂{nomes_variaveis[1]}{' + ...' if num_variables > 2 else ''}

**Sujeito a:**
- a₁₁{nomes_variaveis[0]} + a₁₂{nomes_variaveis[1]}{' + ...' if num_variables > 2 else ''} ≤ b₁
- a₂₁{nomes_variaveis[0]} + a₂₂{nomes_variaveis[1]}{' + ...' if num_variables > 2 else ''} ≤ b₂
- ...
- {nomes_variaveis[0]}, {nomes_variaveis[1]}{', ...' if num_variables > 2 else ''} ≥ 0
""")


# ==================== ENTRADA DE DADOS ====================

with st.form(key="ppl_form"):
    
    # Função Objetivo
    st.markdown('<div class="sub-header">📈 Função Objetivo</div>', unsafe_allow_html=True)
    
    # Monta a equação com os nomes personalizados
    equacao_obj = " + ".join([f"c{i+1}·{nomes_variaveis[i]}" for i in range(num_variables)])
    tipo_icone = "⬆️" if tipo_otimizacao == "Maximizar" else "⬇️"
    st.markdown(f"**{tipo_icone} {tipo_otimizacao} Z =** `{equacao_obj}`")
    st.caption("💡 Insira os coeficientes de cada variável na função objetivo")
    
    funcObj = []
    cols_obj = st.columns(num_variables)
    subscripts = ['₁', '₂', '₃', '₄']
    
    for i in range(num_variables):
        with cols_obj[i]:
            coef = st.number_input(
                f"**c{subscripts[i]}** (coef. de {nomes_variaveis[i]})",
                key=f"obj_{i}",
                value=1.0,
                format="%.2f",
                help=f"Coeficiente da variável {nomes_variaveis[i]} na função objetivo"
            )
            funcObj.append(coef)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Restrições
    st.markdown('<div class="sub-header">🔒 Restrições</div>', unsafe_allow_html=True)
    
    # Monta a equação com os nomes personalizados
    equacao_rest = " + ".join([f"a·{nomes_variaveis[i]}" for i in range(num_variables)])
    st.markdown(f"**Formato:** `{equacao_rest} ≤ b` (mas você pode escolher ≤, ≥ ou = por restrição)")
    st.caption("💡 Defina coeficientes, operador e lado direito (b) para cada restrição")
    
    restric = []
    const = []
    operadores = []
    
    for i in range(num_constraints):
        st.markdown(f"#### Restrição {i+1}:")
        cols_rest = st.columns(num_variables + 2)
        row = []
        
        for j in range(num_variables):
            with cols_rest[j]:
                coef = st.number_input(
                    f"**{nomes_variaveis[j]}**",
                    key=f"r{i}_c{j}",
                    value=1.0,
                    format="%.2f",
                    help=f"Coeficiente de {nomes_variaveis[j]} na restrição {i+1}"
                )
                row.append(coef)
        
        restric.append(row)
        
        with cols_rest[num_variables]:
            operador = st.selectbox(
                f"Operador (R{i+1})",
                options=["≤", "=", "≥"],
                key=f"r{i}_op",
                help="Escolha o tipo da restrição"
            )
            operadores.append(operador)
        
        with cols_rest[num_variables+1]:
            b_val = st.number_input(
                f"LD b{i+1}",
                key=f"r{i}_b",
                value=10.0,
                format="%.2f",
                help=f"Lado direito da restrição {i+1} (RHS)"
            )
            const.append(b_val)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Botão de submit com estilo
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        submit_button = st.form_submit_button(
            label="🚀 Calcular Solução Ótima",
            use_container_width=True
        )


# ==================== PROCESSAMENTO E RESULTADOS ====================

if submit_button:
    
    # Validação de entrada
    erros = validar_entrada(funcObj, restric, const, operadores)
    
    if erros:
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown("### ⚠️ **Erros de Validação**")
        for erro in erros:
            st.markdown(f"- {erro}")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Resolve o problema
        with st.spinner('🔄 **Resolvendo o problema de programação linear...**'):
            solucao, valorOtimo, precoSombra, final_tableau = simplex(funcObj, restric, const, operadores, num_variables, tipo_otimizacao)

        if solucao is not None:
            
            # ========== RESULTADOS PRINCIPAIS ==========
            st.markdown('<div class="sub-header">📊 Resultados da Otimização</div>', unsafe_allow_html=True)
            
            # Primeira linha de resultados
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### 🎯 **Ponto Ótimo**")
                
                # Tabela de solução
                df_solucao = pd.DataFrame({
                    'Variável': [nomes_variaveis[i] for i in range(num_variables)],
                    'Valor': [f'{solucao[i]:.2f}' for i in range(num_variables)]
                })
                
                # Estiliza a tabela
                st.dataframe(
                    df_solucao,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Variável": st.column_config.TextColumn("Variável", width="medium"),
                        "Valor": st.column_config.TextColumn("Valor Ótimo", width="medium")
                    }
                )

            with col2:
                rotulo_tipo = "💰 Valor Máximo" if tipo_otimizacao == "Maximizar" else "💵 Valor Mínimo"
                st.markdown(f"#### {rotulo_tipo}")
                
                df_valor = pd.DataFrame({
                    'Métrica': ['Z*'],
                    'Valor': [f'{valorOtimo:.2f}']
                })
                
                st.dataframe(
                    df_valor,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Métrica": st.column_config.TextColumn("Métrica", width="medium"),
                        "Valor": st.column_config.TextColumn("Valor Ótimo", width="medium")
                    }
                )

            with col3:
                st.markdown("#### 🏷️ **Preços-Sombra**")
                
                df_sombra = pd.DataFrame({
                    'Restrição': [f'R{i+1}' for i in range(num_constraints)],
                    'Preço-Sombra': [f'{abs(precoSombra[i]):.2f}' for i in range(num_constraints)]
                })
                
                st.dataframe(
                    df_sombra,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Restrição": st.column_config.TextColumn("Restrição", width="small"),
                        "Preço-Sombra": st.column_config.TextColumn("Valor", width="medium")
                    }
                )
            
            # ========== TABLEAU FINAL ==========
            st.markdown("---")
            with st.expander("🔢 **Tableau Final do Simplex** (Visualização Avançada)", expanded=False):
                st.markdown("### 📐 Tableau Final da Solução")
                st.caption("Esta tabela mostra uma representação simplificada do tableau (coluna de folga/sobra por restrição)")
                
                subscripts = ['₁', '₂', '₃', '₄']
                headers = [nomes_variaveis[i] for i in range(num_variables)]
                headers += [f"s{subscripts[i]}" for i in range(num_constraints)]
                headers.append("LD")
                
                row_labels = [f"R{i+1}" for i in range(num_constraints)] + ["Z"]
                
                df_tableau = pd.DataFrame(
                    final_tableau,
                    columns=headers,
                    index=row_labels
                )
                
                # Formata o tableau
                st.dataframe(
                    df_tableau.style.format("{:.2f}"),
                    use_container_width=True
                )
                
                st.markdown("""
                **📖 Legenda:**
                - **Variáveis de decisão:** Com nomes personalizados
                - **sᵢ:** Coluna de folga/sobra (1 para ≤, -1 para ≥, 0 para =) — representação simplificada
                - **LD:** Lado direito (Right-Hand Side)
                - **Rᵢ:** Linhas das restrições
                - **Z:** Linha da função objetivo
                """)
                
# ==================== RODAPÉ ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; padding: 2rem 0;'>
    <p style='font-size: 0.9rem;'>
        <strong>📊 Calculadora de Programação Linear</strong> | 
        Desenvolvido com Streamlit e PuLP | 
        Método Simplex
    </p>
    <p style='font-size: 0.8rem; margin-top: 0.5rem;'>
        💡 Dica: Use a barra lateral para configurar diferentes problemas e explore as opções de análise
    </p>
</div>
""", unsafe_allow_html=True)
