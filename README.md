# 🛡️ SHIELD Analytics System

Um sistema completo de análise de dados e BI para monitoramento de contratos financeiros, utilizando a **Arquitetura Medalhão** (Bronze → Silver → Gold) com pipeline de dados automatizado e dashboard interativo.

**Versão:** 2.4  
**Data:** 24 de dezembro de 2025

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Estrutura do Projeto](#estrutura-do-projeto)
3. [Requisitos](#requisitos)
4. [Instalação](#instalação)
5. [Como Usar](#como-usar)
6. [Pipeline de Dados](#pipeline-de-dados)
7. [Dashboard Streamlit](#dashboard-streamlit)
8. [Notebook de Análise](#notebook-de-análise)
9. [Documentação](#documentação)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

O SHIELD Analytics System é uma plataforma de análise de dados desenvolvida para o Banco Shield, permitindo:

✅ **Monitoramento de Contratos** - Acompanhamento de volume, risco e qualidade  
✅ **Análise Competitiva** - Comparação com concorrentes (ex: Hidra Bank)  
✅ **Inteligência de Mercado** - Análise por região, produto e período  
✅ **Gestão de Risco** - Identificação de contratos em atraso crítico  
✅ **BI Interativo** - Dashboard e notebooks para análise exploratória  

### Arquitetura Medalhão

```
📁 BRONZE (Raw Data)
   └─ Dados brutos em CSV
      • dim_localidade.csv
      • dim_produto.csv
      • fato_contratos.csv

      ↓ [Validação + Transformação]

📁 SILVER (Validated Data)
   └─ Dados validados em Parquet
      • dim_banks.parquet
      • dim_categoria.parquet
      • dim_localidade.parquet
      • dim_produto.parquet
      • fato_contratos.parquet
      • quality_summary_*.parquet

      ↓ [Desnormalização + Cálculos]

📁 GOLD (Analytics Ready)
   └─ Dados prontos para consumo
      • gold_fato_contratos_detalhada.parquet
      ↓
   📊 Dashboard (Streamlit)
   📓 Notebooks (Jupyter)
   📈 BI Tools (Power BI, Tableau, etc)
```

---

## 📁 Estrutura do Projeto

```
Analise de dados - Estudo/
│
├── 📄 README.md                           # Este arquivo
├── 📄 DOCUMENTATION.md                    # Documentação completa (colunas, KPIs, etc)
│
├── 🔧 run_full_pipeline.py                # Script para executar pipeline completa
│
├── 📁 medalion-architeture/               # Estrutura Medalhão
│   ├── 01-bronze-raw/                     # Dados brutos (CSV)
│   │   ├── dim_localidade.csv
│   │   ├── dim_produto.csv
│   │   └── fato_contratos.csv
│   │
│   ├── 02-silver-validated/               # Dados validados (Parquet)
│   │   ├── dim_banks.parquet
│   │   ├── dim_categoria.parquet
│   │   ├── dim_localidade.parquet
│   │   ├── dim_produto.parquet
│   │   ├── fato_contratos.parquet
│   │   └── quality_summary_*.parquet
│   │
│   └── 03-gold-enriched/                  # Dados para BI (Parquet)
│       └── gold_fato_contratos_detalhada.parquet
│
├── 📁 src/                                # Código fonte
│   ├── silver/                            # Pipeline Silver
│   │   ├── run_silver_pipeline.py         # Executor do pipeline Silver
│   │   └── validators/                    # Validadores de dados
│   │       ├── schema_enforcer.py         # Validação de tipos
│   │       ├── schema_enforcement.py
│   │       ├── dimension_conformation.py
│   │       ├── bussines_rules.py          # Regras de negócio
│   │       └── relationship_validator.py  # Validação de relacionamentos
│   │
│   ├── gold/                              # Pipeline Gold
│   │   └── database.py                    # Executor do pipeline Gold (DuckDB)
│   │
│   └── utils/                             # Utilitários
│       └── paths.py                       # Configuração de caminhos
│
├── 📁 dashboards/                         # Dashboard Streamlit
│   ├── main.py                            # Aplicação principal
│   ├── analytics/
│   │   ├── metrics.py                     # Cálculo de KPIs (ShieldMetrics)
│   │   └── filters.py                     # Filtros disponíveis
│   └── utils/
│       ├── ui_utils.py                    # Componentes UI
│       └── styles.css                     # Estilos customizados
│
├── 📓 SHIELD_Analytics_KPI_Analysis.ipynb # Notebook de análise
│
└── 📄 requirements.txt                    # Dependências do projeto

```

---

## 📦 Requisitos

### Python
- **Python 3.9+** (recomendado 3.10 ou 3.11)

### Dependências Principais
```
pandas >= 1.5.0
duckdb >= 0.8.0
plotly >= 5.0.0
streamlit >= 1.20.0
jupyter >= 1.0.0
```

### Opcional (para BI avançado)
- Power BI
- Tableau
- Apache Superset

---

## 🚀 Instalação

### 1. Clonar Repositório

```bash
# Navegar até o diretório do projeto
git clone https://github.com/Kaua-Novaes/case-banco--shield.git
```

### 2. Criar Ambiente Virtual (Recomendado)

**MacOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

```bash
pip install pandas duckdb plotly streamlit jupyter numpy
```

### 4. Verificar Instalação

```bash
python -c "import pandas; import duckdb; import plotly; print('✅ Tudo instalado!')"
```

---

## 📖 Como Usar

### Opção 1️⃣: Executar Pipeline Completa (Silver + Gold)

**Descrição:** Processa dados brutos (Bronze) → Valida e normaliza (Silver) → Cria modelos analíticos (Gold)

```bash
python run_full_pipeline.py
```

**O que acontece:**
1. ✅ Lê arquivos CSV da camada Bronze
2. ✅ Valida schema, tipos de dados e regras de negócio
3. ✅ Cria dimensões (bancos, categorias, localidades)
4. ✅ Valida relacionamentos e integridade referencial
5. ✅ Salva dados validados em Parquet (Silver)
6. ✅ Cria tabela desnormalizada otimizada para BI (Gold)
7. ✅ Gera relatório de qualidade de dados

**Saída esperada:**
```
================================================================================
INICIANDO PIPELINE COMPLETA (SILVER + GOLD)
================================================================================

ETAPA 1: PROCESSANDO CAMADA SILVER
--------------------------------------------------------------------------------
[1/5] Executando validação de schema...
   ✓ 3 tabelas processadas
   ⚠ XX erros encontrados

[2/5] Aplicando regras de negócio...
   ✓ Validações de limites executadas

[3/5] Criando dimensões...
   ✓ dim_banks criada
   ✓ dim_categoria criada

[4/5] Validando relacionamentos...
   ✓ Integridade referencial validada

[5/5] Salvando e gerando relatórios...
   ✓ Arquivos Parquet salvos
   ✓ Relatório de qualidade gerado

ETAPA 2: PROCESSANDO CAMADA GOLD
--------------------------------------------------------------------------------
=== INICIANDO PIPELINE GOLD ===

✓ Tabelas Silver registradas como views
✓ Tabela Gold criada (One Big Table)
✓ Arquivo Parquet exportado

=== PIPELINE GOLD FINALIZADO ===
```

### Opção 2️⃣: Executar Apenas Pipeline Silver

```bash
python -m src.silver.run_silver_pipeline
```

Processa apenas Bronze → Silver (útil para reprocessar dados)

### Opção 3️⃣: Executar Apenas Pipeline Gold

```bash
python -m src.gold.database
```

Processa apenas Silver → Gold (útil após atualizar dados Silver)

---

## 📊 Dashboard Streamlit

### Iniciar o Dashboard

```bash
streamlit run dashboards/main.py
```

O dashboard abrirá em `http://localhost:8501`

### Funcionalidades

#### 🎚️ Filtros (Topo da página)
- **Entidade**: Selecione um ou mais bancos
- **Setor**: Filtre por regiões/localidades
- **Arsenal**: Escolha produtos específicos

#### 📈 Aba 1: Visão Geral
- **4 KPIs Principais**:
  - Volume Total (R$)
  - Market Share do Banco Shield (%)
  - Contratos Ativos
  - Nível de Risco Médio (%)
- **Gráfico de Área**: Evolução temporal de volume (Disputa de Território)
- **Gráfico de Barras**: Share por produto

#### 🌍 Aba 2: Regiões
- **Gráfico de Barras Agrupadas**: Volume por região e banco
- **Insight Automático**: Identifica força do Hidra Bank por região

#### ⚠️ Aba 3: Risco & Qualidade
- **Scatter Plot Interativo**: Risco × Volume × Quantidade de Contratos
- **Danger Zone**: Linha vermelha em 10% de risco
- **Tabela de Qualidade**: Indicadores de qualidade dos dados

### Paleta de Cores

| Banco | Cor | Código |
|-------|-----|--------|
| Banco Shield | Cyan Neon | `#00F0FF` |
| Hidra Bank | Red Neon | `#FF2A2A` |
| Alerta | Ouro | `#FFD700` |
| Risco | Vermelho | `#FF4B4B` |

---

## 📓 Notebook de Análise

### Abrir o Notebook

```bash
jupyter notebook SHIELD_Analytics_KPI_Analysis.ipynb
```

Ou use o VS Code com a extensão Jupyter.

### Conteúdo do Notebook

O notebook contém **12 seções principais**:

1. **Setup e Importações**
   - Importação de bibliotecas
   - Definição da classe ShieldMetrics

2. **Carregamento de Dados**
   - Leitura do Parquet Gold
   - Análise estrutural
   - Estatísticas descritivas

3. **KPI 1: Volume Total**
   - Cálculo total e por banco
   - Comparações

4. **KPI 2 & 3: Market Share e Contratos**
   - Participação de mercado
   - Quantidade de contratos por banco

5. **KPI 4: Nível de Risco**
   - Score de risco com classificação
   - Contratos em alto risco

6. **KPI 5: Volume por Tempo**
   - Série temporal
   - Gráfico de área

7. **KPI 6: Share por Produto**
   - Participação por tipo de produto
   - Visualização empilhada

8. **KPI 7: Análise Regional**
   - Volume por região
   - Barras agrupadas por banco

9. **KPI 8: Risco vs Volume**
   - Scatter plot interativo
   - Tamanho de bolha = contratos

10. **Insights e Conclusões**
    - Achados principais
    - Recomendações

### Executar Células

Selecione uma célula e pressione:
- **Jupyter**: `Shift + Enter`
- **VS Code**: `Ctrl/Cmd + Enter`

### Exemplo de Uso

```python
# Importar dados
df = pd.read_parquet('medalion-architeture/03-gold-enriched/gold_fato_contratos_detalhada.parquet')

# Usar ShieldMetrics
volume = ShieldMetrics.volume_total(df)
share = ShieldMetrics.market_share(df, 'Banco Shield')
risco = ShieldMetrics.risco_medio(df)

# Filtrar
df_filtered = df[df['bank_name'] == 'Banco Shield']
volume_shield = ShieldMetrics.volume_total(df_filtered)

# Visualizar
df_tempo = ShieldMetrics.volume_tempo(df)
fig = px.area(df_tempo, x='ano_mes', y='financed_amount', color='bank_name')
fig.show()
```

---

## 🔄 Pipeline de Dados

### Fluxo Completo

```
[BRONZE] → [SILVER] → [GOLD] → [BI/CONSUMO]
  CSV      Parquet   Parquet   Streamlit
            ↓
         quality_report
         (diagnóstico)
```

### Etapas do Pipeline Silver

| Etapa | Descrição | Validações |
|-------|-----------|-----------|
| **1. Schema Enforcement** | Conversão de tipos de dados | Type casting, NOT NULL |
| **2. Business Rules** | Validação de regras de negócio | Mín/máx, ranges |
| **3. Dimension Creation** | Criação de dimensões | Valores únicos |
| **4. Relationship Validation** | Integridade referencial | Foreign keys, orphaned records |
| **5. Export & Reporting** | Salvamento e relatórios | Quality metrics |

### Etapas do Pipeline Gold

| Etapa | Descrição | Tecnologia |
|-------|-----------|-----------|
| **1. Register Tables** | Registra Parquets como views | DuckDB |
| **2. Create Fact Table** | Desnormaliza e calcula features | SQL |
| **3. Export Parquet** | Exporta para consumo | Parquet |

### Tratamento de Erros

Erros encontrados durante a validação são registrados em:
- `quality_report_[TIMESTAMP].parquet` - Erros detalhados
- `quality_summary_[TIMESTAMP].parquet` - Resumo consolidado

**Tipos de erros capturados:**
- `MISSING_COLUMN` - Coluna obrigatória ausente
- `NOT_NULL_VIOLATION` - Campo nulo obrigatório
- `TYPE_CAST_ERROR` - Erro na conversão de tipo
- `MIN_VIOLATION` / `MAX_VIOLATION` - Valor fora do intervalo
- `RELATIONSHIP_ERROR` - Referência inválida


---


## 🤖 Integração com Jarvis (IA)

Para ativar o assistente inteligente **Jarvis** dentro do dashboard, é necessário configurar uma chave de API do Google Gemini.

> **⚠️ Nota:** A utilização da API do Gemini pode gerar custos dependendo do volume de requisições e do plano da sua conta Google.

### Como Ativar

1. **Obtenha a API Key:** Gere sua chave no [Google AI Studio](https://aistudio.google.com/).
2. **Configure o Ambiente:** Navegue até o arquivo de configuração:
`dashboards/assistente/gemini_api.env`
3. **Adicione a Chave:** Cole sua API Key no arquivo (substituindo o conteúdo existente se necessário):
```env
GEMINI_API_KEY=cole_sua_chave_aqui
```


4. **Reinicie o Dashboard:** Pare a execução atual (Ctrl+C) e rode novamente:
```bash
streamlit run dashboards/main.py

```

## 📚 Documentação

### DOCUMENTATION.md

Documentação completa com:
- ✅ Dicionário de todas as colunas (30+)
- ✅ Descrição de 11 KPIs com fórmulas
- ✅ Estrutura das tabelas de dimensão
- ✅ Regras de negócio
- ✅ Exemplos de uso em Python

**Acesse:** [DOCUMENTATION.md](DOCUMENTATION.md)

### SILVER_PIPELINE_README.md

Documentação específica do pipeline Silver:
- Validações implementadas
- Sistema de qualidade
- Relatórios gerados

**Acesse:** [SILVER_PIPELINE_README.md](SILVER_PIPELINE_README.md)

---


### Problema: Dados desatualizados

**Solução:**
```bash
# Reexecute o pipeline completo
python run_full_pipeline.py

# Ou apenas o Gold se os dados Silver já foram atualizados
python -m src.gold.database
```

---

## 📞 Suporte

Para dúvidas ou problemas:

1. ✅ Verifique a **DOCUMENTATION.md** para referência completa
3. ✅ Revise os **exemplos de uso** acima
4. ✅ Verifique **logs e erros** na saída do terminal

---

## 📋 Checklist de Setup

- [ ] Python 3.9+ instalado
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo pipeline executado com sucesso (`python run_full_pipeline.py`)
- [ ] Dashboard abre sem erros (`streamlit run dashboards/main.py`)
- [ ] Notebook executa sem erros (`jupyter notebook SHIELD_Analytics_KPI_Analysis.ipynb`)
- [ ] Arquivo Gold existe (`medallion-architeture/03-gold-enriched/gold_fato_contratos_detalhada.parquet`)

---

## 🎯 Próximos Passos

1. **Explorar os dados**
   - Abra o notebook de análise
   - Execute as células sequencialmente
   - Customize as visualizações

2. **Usar o Dashboard**
   - Filtre por banco, região, produto
   - Analise tendências temporais
   - Monitore indicadores de risco

3. **Integrar com BI**
   - Exporte dados do Gold para Power BI/Tableau
   - Crie relatórios customizados
   - Configure alertas automáticos

4. **Monitoramento Contínuo**
   - Agende execução do pipeline (cron/scheduler)
   - Configure alertas de qualidade
   - Implemente logs e métricas


---

**Última atualização:** 24 de dezembro de 2025  
