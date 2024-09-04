import pandas as pd
import mysql.connector
import streamlit as st


def BD_Vendas():
    # Parametros de Login AWS
    config = {
    'user': 'user_automation_jpa',
    'password': 'luck_jpa_2024',
    'host': 'comeia.cixat7j68g0n.us-east-1.rds.amazonaws.com',
    'database': 'test_phoenix_joao_pessoa'
    }
    # Conexão as Views
    conexao = mysql.connector.connect(**config)
    cursor = conexao.cursor()

    # Script MySql para requests
    cursor.execute('''
        SELECT 
            Canal_de_Vendas,
            Vendedor,
            Nome_Segundo_Vendedor,
            Status_Financeiro,
            Data_Venda,
            Valor_Venda,
            Desconto_Global_Por_Servico
        FROM vw_sales_new
        ''')
    # Coloca o request em uma variavel
    resultado = cursor.fetchall()
    # Busca apenas o cabecalhos do Banco
    cabecalho = [desc[0] for desc in cursor.description]

    # Fecha a conexão
    cursor.close()
    conexao.close()

    # Coloca em um dataframe e muda o tipo de decimal para float
    df = pd.DataFrame(resultado, columns=cabecalho)
    df['Data_Venda'] = pd.to_datetime(df['Data_Venda'], format='%Y-%m-%d', errors='coerce')
    #df = df.applymap(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)
    return df


st.set_page_config(layout='wide')
st.session_state.df = BD_Vendas()
df = st.session_state.df

lista_canal = df['Canal_de_Vendas'].dropna().unique().tolist()
lista_canal.sort()
lista_canal.insert(0, '--- Todos ---')
lista_vendedor = df['Vendedor'].dropna().unique().tolist()
lista_vendedor.sort()
lista_vendedor.insert(0, '--- Todos ---')

st.title('Listar Vendas')
st.markdown("""
             <style>
            .stApp{
                background-color: #047c6c;
            }
            h1{
                font-size: 40pt;
                color: #d17d7f;
            }
            h2, h3, .stMarkdown, .stRadio label, .stSelectbox label{
                font-size: 10pt;
                color: #74c4bc;
            }
            .stDateInput label {
                font-size: 20pt;
                color: #74c4bc;
            }
            <style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 6])

with col1:
    col1_1, col1_2 = st.columns(2)
    with col1_1:
        data_ini = st.date_input('Data Inicio', value=pd.to_datetime('2024-1-1'))
    with col1_2:
        data_fim = st.date_input('Data Fim', value=pd.to_datetime('2025-1-1'))
    seleciona_canal = st.selectbox('Canal de Vendas', lista_canal)
    seleciona_vend = st.selectbox('Vendedor', lista_vendedor)
    botao_filtro = st.button('Filtrar')

with col2:
    col2_1, col2_2 = st.columns([2,4])
    if botao_filtro:
        data_ini = pd.to_datetime(data_ini)
        data_fim = pd.to_datetime(data_fim)
        resultado_filtrado = df[
            (df['Data_Venda'] >= data_ini) &
            (df['Data_Venda'] <= data_fim)
        ]
        resultado_filtrado['Data_Venda'] = resultado_filtrado['Data_Venda'].dt.strftime('%d/%m/%Y')

        if seleciona_canal != '--- Todos ---' and seleciona_vend != '--- Todos ---':
            with col2_1:
                resultado_filtrado = resultado_filtrado[
                    (resultado_filtrado['Canal_de_Vendas'] == seleciona_canal) &
                    (resultado_filtrado['Vendedor'] == seleciona_vend)
                    ] 
                soma_vendas = resultado_filtrado['Valor_Venda'].sum()
                st.subheader(f'Total de Vendas: {seleciona_canal} - {seleciona_vend}')
                st.write(f'R${soma_vendas:,.2f}'.replace('.', ',').replace(',','.',1))
            with col2_2:
                resultado_filtrado['Valor_Venda'] = resultado_filtrado['Valor_Venda'].apply(lambda x: f'{x:,.2f}'.replace('.', ',').replace(',','.',1))
                st.dataframe(resultado_filtrado[['Data_Venda', 'Valor_Venda', 'Vendedor']], use_container_width=True, hide_index=True)

        elif seleciona_canal != '--- Todos ---' and seleciona_vend == '--- Todos ---':
            with col2_1:
                resultado_filtrado = resultado_filtrado[resultado_filtrado['Canal_de_Vendas'] == seleciona_canal]
                soma_vendas = resultado_filtrado['Valor_Venda'].sum()
                st.subheader(f'Total de Venda do Canal {seleciona_canal}')
                st.write(f'R${soma_vendas:,.2f}'.replace('.', ',').replace(',','.',1))
            with col2_2:
                soma_venda_canal = resultado_filtrado.groupby('Vendedor')['Valor_Venda'].sum().reset_index()
                soma_venda_canal = soma_venda_canal.sort_values(by='Valor_Venda', ascending=False)
                soma_venda_canal['Valor_Venda'] = soma_venda_canal['Valor_Venda'].apply(lambda x: f'{x:,.2f}'.replace('.', ',').replace(',','.',1))
                st.subheader('Total por Vendedor')
                st.dataframe(soma_venda_canal, use_container_width=True, hide_index=True)

        elif seleciona_canal == '--- Todos ---' and seleciona_vend != '--- Todos ---':
            with col2_1:
                resultado_filtrado = resultado_filtrado[resultado_filtrado['Vendedor'] == seleciona_vend]
                soma_vendas = resultado_filtrado['Valor_Venda'].sum()
                st.subheader(f'Total de Vendas do Vendedor: {seleciona_vend}')
                st.write(f'R${soma_vendas:,.2f}'.replace('.', ',').replace(',','.',1))
            with col2_2:
                soma_venda_vend = resultado_filtrado.groupby('Canal_de_Vendas')['Valor_Venda'].sum().reset_index()
                soma_venda_vend = soma_venda_vend.sort_values(by='Valor_Venda', ascending=False)
                soma_venda_vend['Valor_Venda'] = soma_venda_vend['Valor_Venda'].apply(lambda x: f'{x:,.2f}'.replace('.', ',').replace(',','.',1))
                st.subheader('Valor de Vendas por Canal')
                st.dataframe(soma_venda_vend, use_container_width=True, hide_index=True)
            
        else: # --- TODOS ---- CANAL / --- TODOS --- VENDEDORES
            with col2_1:
                soma_venda_canal = resultado_filtrado.groupby('Canal_de_Vendas')['Valor_Venda'].sum().reset_index()
                soma_venda_canal = soma_venda_canal.sort_values(by='Valor_Venda', ascending=False)
                #soma_venda_canal['Valor_Venda'] = soma_venda_canal['Valor_Venda'].str.replace('.', '').str.replace(',','.',1).astype(float)
                soma_venda_total = soma_venda_canal['Valor_Venda'].sum()
                soma_venda_canal['Valor_Venda'] = soma_venda_canal['Valor_Venda'].apply(lambda x: f'{x:,.2f}'.replace('.', ',').replace(',','',1))
                st.subheader('Valor Total de Vendas')
                st.write(f'R${soma_venda_total:,.2f}'.replace('.', ',').replace(',','.',1))
                with col2_2:
                    st.subheader('Total de Vendas por Canal')
                    st.dataframe(soma_venda_canal, use_container_width=True, hide_index=True)
                    

        
        

    #st.write(lista_canal)
