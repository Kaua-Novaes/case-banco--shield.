# Documentação Completa - SHIELD Analytics System

## Índice
1. [Estrutura do Banco de Dados](#estrutura-do-banco-de-dados)
2. [Dicionário de Colunas](#dicionário-de-colunas)
3. [KPIs e Métricas](#kpis-e-métricas)
4. [Tabelas de Dimensão](#tabelas-de-dimensão)
5. [Pipeline de Dados](#pipeline-de-dados)

---

## Estrutura do Banco de Dados

### Visão Geral da Arquitetura Medalhão

```
medalion-architeture/
├── 01-bronze-raw/              # Dados brutos (CSV)
│   ├── dim_localidade.csv
│   ├── dim_produto.csv
│   └── fato_contratos.csv
├── 02-silver-validated/        # Dados validados (Parquet)
│   ├── dim_banks.parquet
│   ├── dim_categoria.parquet
│   ├── dim_localidade.parquet
│   ├── dim_produto.parquet
│   ├── fato_contratos.parquet
│   └── quality_summary_*.parquet
└── 03-gold-enriched/           # Dados prontos para BI (Parquet)
    └── gold_fato_contratos_detalhada.parquet
```

### Tabela Gold Principal: `gold_fato_contratos_detalhada`

A tabela de consumo principal é uma **ONE BIG TABLE (tabela desnormalizada)** que consolida:
- Fatos de contratos
- Dados de dimensões (bancos, produtos, categorias, localidades)
- Métricas calculadas de negócio
- Features derivadas para análise

---

## Dicionário de Colunas

### 📍 Identificadores e Chaves

| Coluna | Tipo | Descrição | Exemplo |
|--------|------|-----------|---------|
| `contract_id` | INTEGER | Identificador único do contrato | 12458 |
| `ano_mes` | STRING | Período do contrato (YYYYMM) | "202501" |
| `product_id` | INTEGER | Identificador do produto | 5 |
| `location_id` | INTEGER | Identificador da localidade | 15 |
| `dim_banks_id` | INTEGER | Identificador do banco | 1 |

---

### 🏦 Informações de Banco (Dimensão)

| Coluna | Tipo | Descrição | Exemplo | Fonte |
|--------|------|-----------|---------|-------|
| `bank_name` | STRING | Nome oficial do banco | "Banco Shield", "Hidra Bank" | dim_banks |
| `is_competitor` | INTEGER (0/1) | Flag indicando se é competidor | 1 (sim), 0 (não) | Calculado |

**Lógica de `is_competitor`:**
```
is_competitor = 1 SE dim_banks_id ≠ 1 SENÃO 0
```
- `dim_banks_id = 1` → Banco Shield (não é competidor)
- `dim_banks_id > 1` → Outros bancos (competidores)

---

### 🛍️ Informações de Produto (Dimensão)

| Coluna | Tipo | Descrição | Exemplo | Intervalo |
|--------|------|-----------|---------|-----------|
| `product_name` | STRING | Nome do produto | "Crédito Pessoal", "Auto", "Consignado", "Cartões" | - |
| `category_name` | STRING | Categoria do produto | "Crédito", "Investimento" | - |
| `prazo` | INTEGER | Prazo em meses (tenor) | 12, 24, 36, 60 | 1-240 |
| `taxa_base` | FLOAT | Taxa base anual (APR) | 0.08, 0.12, 0.15 | 0-100% |

---

### 🌍 Informações de Localidade (Dimensão)

| Coluna | Tipo | Descrição | Exemplo | 
|--------|------|-----------|---------|
| `location_name` | STRING | Nome da localidade/região | "São Paulo", "Rio de Janeiro", "Minas Gerais" |
| `location_id` | INTEGER | Identificador único da localidade | 1, 2, 3 |
| `macro_region` | STRING | Macro-região | "North", "South", "East", "West", "Capital" |
| `regional_risk_factor` | FLOAT | Fator de risco regional | 0.5-1.5 |

---

### 💰 Métricas Financeiras (Fato)

| Coluna | Tipo | Descrição | Cálculo | Unidade |
|--------|------|-----------|---------|---------|
| `units` | INTEGER | Quantidade de unidades/contratos | Contagem | Unidades |
| `financed_amount` | FLOAT | Valor financiado total | Soma de todas as operações | R$ |
| `outstanding_balance` | FLOAT | Saldo devedor pendente | Valor ainda a receber | R$ |
| `dpd_30` | INTEGER | Dias em atraso (DPD) | Dias em atraso do contrato | Dias |
| `risk_score` | FLOAT | Score de risco do contrato | 0.00 a 1.00 (0-100%) | Score |

---

### 📊 Métricas Derivadas (Calculadas)

| Coluna | Tipo | Fórmula | Descrição | Intervalo |
|--------|------|---------|-----------|-----------|
| `pct_amortized` | FLOAT | `outstanding_balance / financed_amount` | Percentual do saldo devedor em relação ao valor financiado | 0-1 (0-100%) |
| `is_high_risk` | INTEGER (0/1) | `1 SE dpd_30 ≥ 30 SENÃO 0` | Flag indicando contrato em atraso crítico | 0 ou 1 |

**Interpretação:**
- `pct_amortized = 0.30` → 30% do contrato ainda está pendente
- `pct_amortized = 0.00` → Contrato totalmente amortizado
- `is_high_risk = 1` → Contrato com 30+ dias em atraso (RISCO!)

---

## KPIs e Métricas

### Documentação de Todos os KPIs da Classe `ShieldMetrics`

#### 1. **Volume Total** 
```python
def volume_total(df) -> float
```

**Descrição:** Soma de todos os valores financiados em um período.

**Fórmula:**
$$\text{Volume Total} = \sum \text{financed\_amount}$$

**Parâmetros:**
- `df` (DataFrame): Dados filtrados

**Retorno:** float - Soma total em R$

**Exemplo:**
```python
vol = ShieldMetrics.volume_total(df_filtered)
# Retorna: 1500000000.50 (R$ 1,5 bilhão)
```

**Uso no Dashboard:** Métrica KPI principal no topo (col1)

---

#### 2. **Opções Únicas de Coluna**
```python
def options(df, column) -> numpy.ndarray
```

**Descrição:** Retorna todos os valores únicos de uma coluna (para preenchimento de filtros).

**Fórmula:**
$$\text{Opções} = \text{unique(coluna)}$$

**Parâmetros:**
- `df` (DataFrame): Dados
- `column` (str): Nome da coluna

**Retorno:** Array com valores únicos

**Exemplo:**
```python
bancos = ShieldMetrics.options(df, "bank_name")
# Retorna: ['Banco Shield', 'Hidra Bank']

regioes = ShieldMetrics.options(df, "location_name")
# Retorna: ['North', 'South', 'East', 'West', 'Capital']
```

**Uso no Dashboard:** Preenchimento dos multiselects de filtros

---

#### 3. **Market Share**
```python
def market_share(df, banco_ref='Banco Shield') -> float
```

**Descrição:** Percentual de participação de mercado de um banco em relação ao total.

**Fórmula:**
$$\text{Market Share (\%)} = \frac{\text{Volume do Banco}}{\text{Volume Total}} \times 100$$

**Parâmetros:**
- `df` (DataFrame): Dados filtrados
- `banco_ref` (str, default='Banco Shield'): Nome do banco de referência

**Retorno:** float - Percentual (0-100)

**Exemplo:**
```python
share = ShieldMetrics.market_share(df_filtered, 'Banco Shield')
# Se o banco tem R$ 600M de R$ 1.500M = 40%

share = ShieldMetrics.market_share(df_filtered, 'Hidra Bank')
# Se o banco tem R$ 900M de R$ 1.500M = 60%
```

**Tratamento de Erro:**
- Se volume total = 0 → retorna 0

**Uso no Dashboard:** KPI "SHIELD SHARE" em amarelo (alerta)

---

#### 4. **Contratos Ativos**
```python
def contratos_ativos(df) -> int
```

**Descrição:** Total de contratos únicos no período/filtro.

**Fórmula:**
$$\text{Contratos Ativos} = \text{COUNT}(\text{contract\_id})$$

**Parâmetros:**
- `df` (DataFrame): Dados filtrados

**Retorno:** int - Número de contratos

**Exemplo:**
```python
contratos = ShieldMetrics.contratos_ativos(df_filtered)
# Retorna: 45230 (45 mil contratos)
```

**Nota:** Conta linhas únicas de contract_id (não afetado por agrupamentos)

**Uso no Dashboard:** KPI "CONTRATOS ATIVOS" em branco

---

#### 5. **Nível de Risco Médio**
```python
def risco_medio(df) -> float
```

**Descrição:** Score de risco médio multiplicado por 100 para exibição em percentual.

**Fórmula:**
$$\text{Risco Médio (\%)} = \text{MEAN}(\text{risk\_score}) \times 100$$

**Parâmetros:**
- `df` (DataFrame): Dados filtrados

**Retorno:** float - Percentual (0-100)

**Exemplo:**
```python
risco = ShieldMetrics.risco_medio(df_filtered)
# Se média de risk_score = 0.072 → retorna 7.2%
```

**Interpretação:**
- 0-3% → Risco Baixo
- 3-7% → Risco Moderado
- 7-12% → Risco Elevado
- >12% → Risco Crítico

**Uso no Dashboard:** KPI "NÍVEL DE RISCO" em vermelho (COLOR_HYDRA)

---

#### 6. **Volume por Tempo**
```python
def volume_tempo(df) -> DataFrame
```

**Descrição:** Série temporal do volume financiado agrupada por período (ano-mês) e banco.

**Fórmula:**
$$\text{Volume por Período} = \sum \text{financed\_amount} \text{ GROUP BY } \{ano\_mes, bank\_name\}$$

**Parâmetros:**
- `df` (DataFrame): Dados filtrados

**Retorno:** DataFrame com colunas:
- `ano_mes` (str): "YYYY-MM"
- `bank_name` (str): Nome do banco
- `financed_amount` (float): Soma do volume

**Exemplo:**
```python
df_time = ShieldMetrics.volume_tempo(df)
#   ano_mes  bank_name        financed_amount
# 0  2024-01 Banco Shield       500000000.00
# 1  2024-01 Hidra Bank         600000000.00
# 2  2024-02 Banco Shield       520000000.00
# 3  2024-02 Hidra Bank         580000000.00
```

**Transformações Aplicadas:**
- `ano_mes` convertido de "202401" para "2024-01" (formato legível)

**Uso no Dashboard:** Gráfico de área "DISPUTA DE TERRITÓRIO" (ABA 1)

---

#### 7. **Volume por Região (Com Data)**
```python
def volume_regiao_total(df) -> DataFrame
```

**Descrição:** Volume financiado por localidade, banco e período.

**Fórmula:**
$$\text{Volume Regional} = \sum \text{financed\_amount} \text{ GROUP BY } \{location\_name, bank\_name, ano\_mes\}$$

**Parâmetros:**
- `df` (DataFrame): Dados filtrados

**Retorno:** DataFrame com colunas:
- `location_name` (str): Nome da região
- `bank_name` (str): Nome do banco
- `ano_mes` (str): Período
- `financed_amount` (float): Soma do volume

**Exemplo:**
```python
df_reg = ShieldMetrics.volume_regiao_total(df)
#   location_name      bank_name        ano_mes  financed_amount
# 0 São Paulo      Banco Shield       202401    250000000.00
# 1 São Paulo      Hidra Bank         202401    300000000.00
# 2 Rio de Janeiro Banco Shield       202401    150000000.00
```

**Nota:** Mantém dimensão temporal diferentemente de `volume_regiao_total` (versão simples)

**Uso:** Análises regionais com histórico temporal

---

#### 8. **Share por Produto**
```python
def share_por_produto(df) -> DataFrame
```

**Descrição:** Participação de volume por produto e banco.

**Fórmula:**
$$\text{Share Produto} = \sum \text{financed\_amount} \text{ GROUP BY } \{product\_name, bank\_name\}$$

**Parâmetros:**
- `df` (DataFrame): Dados filtrados

**Retorno:** DataFrame com colunas:
- `product_name` (str): Nome do produto
- `bank_name` (str): Nome do banco
- `financed_amount` (float): Soma do volume

**Exemplo:**
```python
df_prod = ShieldMetrics.share_por_produto(df)
#    product_name   bank_name         financed_amount
# 0  Crédito Pessoal Banco Shield     400000000.00
# 1  Crédito Pessoal Hidra Bank       500000000.00
# 2  Auto           Banco Shield       300000000.00
# 3  Auto           Hidra Bank         380000000.00
# 4  Consignado     Banco Shield       200000000.00
# 5  Consignado     Hidra Bank         150000000.00
```

**Nota:** Perfeito para visualização empilhada (stacked bar)

**Uso no Dashboard:** Gráfico de barras horizontal "SHARE POR PRODUTO" (ABA 1)

---

#### 9. **Melhor Produto por Região (Banco Específico)**
```python
def region_product(df, banco_ref='Banco Hidra') -> dict
```

**Descrição:** Identifica a região e produto com maior volume para um banco específico.

**Fórmula:**
1. Filtrar por banco: `df[df['bank_name'] == banco_ref]`
2. Agrupar e somar: `GROUP BY {location_name, product_name}`
3. Ordena descendente e pega o primeiro: `ORDER BY financed_amount DESC LIMIT 1`

**Parâmetros:**
- `df` (DataFrame): Dados filtrados
- `banco_ref` (str, default='Banco Hidra'): Nome do banco

**Retorno:** dict com chaves:
- `location_name` (str): Região de maior volume
- `product_name` (str): Produto de maior volume

**Exemplo:**
```python
resultado = ShieldMetrics.region_product(df, 'Banco Hidra')
# Retorna: {'location_name': 'São Paulo', 'product_name': 'Crédito Pessoal'}
```

**Interpretação:**
- Indica onde a Hidra tem força máxima
- Usado para identificar mercados críticos

**Uso no Dashboard:** Texto informativo na ABA 2 com aviso de risco competitivo

---

#### 10. **Agrupamento por Região e Banco**
```python
def group_region(df) -> DataFrame
```

**Descrição:** Volume total por região e banco (consolidado, sem série temporal).

**Fórmula:**
$$\text{Volume Regional} = \sum \text{financed\_amount} \text{ GROUP BY } \{location\_name, bank\_name\}$$

**Parâmetros:**
- `df` (DataFrame): Dados filtrados

**Retorno:** DataFrame com colunas:
- `location_name` (str): Nome da região
- `bank_name` (str): Nome do banco
- `financed_amount` (float): Soma do volume

**Exemplo:**
```python
df_reg = ShieldMetrics.group_region(df)
#   location_name      bank_name        financed_amount
# 0 São Paulo      Banco Shield       400000000.00
# 1 São Paulo      Hidra Bank         600000000.00
# 2 Rio de Janeiro Banco Shield       300000000.00
# 3 Rio de Janeiro Hidra Bank         250000000.00
# 4 Minas Gerais   Banco Shield       200000000.00
# 5 Minas Gerais   Hidra Bank         150000000.00
```

**Diferença com `volume_regiao_total`:**
- `volume_regiao_total`: COM série temporal (ano_mes)
- `group_region`: SEM série temporal (consolidado)

**Uso no Dashboard:** Gráfico de barras agrupadas "DOMÍNIO GEOGRÁFICO" (ABA 2)

---

#### 11. **Risco, Volume e Contratos por Produto**
```python
def risco_volume_contratos(df) -> DataFrame
```

**Descrição:** Agregação multi-métrica por produto e banco (volume, risco médio e contagem).

**Fórmula:**
$$\text{Agregação} = \text{GROUP BY } \{product\_name, bank\_name\} \text{ AGGREGATE}:$$
- $\sum \text{financed\_amount}$
- $\text{MEAN}(\text{risk\_score})$
- $\text{COUNT}(\text{contract\_id})$

**Parâmetros:**
- `df` (DataFrame): Dados filtrados

**Retorno:** DataFrame com colunas:
- `product_name` (str): Nome do produto
- `bank_name` (str): Nome do banco
- `financed_amount` (float): Volume total
- `risk_score` (float): Score médio (0-1)
- `contract_id` (int): Contagem de contratos

**Exemplo:**
```python
df_risk = ShieldMetrics.risco_volume_contratos(df)
#    product_name   bank_name        financed_amount risk_score contract_id
# 0 Crédito Pessoal Banco Shield      400000000      0.045        5200
# 1 Crédito Pessoal Hidra Bank        500000000      0.078        6500
# 2 Auto           Banco Shield       300000000      0.032        1200
# 3 Auto           Hidra Bank         380000000      0.095        1800
```

**Uso no Dashboard:** Scatter plot "RADAR DE RISCO E VOLUME" (ABA 3)

**Interpretação do Gráfico:**
- **Eixo X:** financed_amount (volume)
- **Eixo Y:** risk_score (risco)
- **Tamanho da bolha:** contract_id (quantidade)
- **Cor:** bank_name (banco)
- **Linha vermelha:** y=0.10 (danger zone)

---

## Tabelas de Dimensão

### `dim_banks` - Dimensão de Bancos

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `dim_banks_id` | INTEGER (PK) | Identificador único |
| `nome_oficial` | STRING | Nome oficial do banco |

**Dados de Exemplo:**
```
dim_banks_id | nome_oficial
1            | Banco Shield
2            | Hidra Bank
```

---

### `dim_categoria` - Dimensão de Categorias

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `dim_categoria_id` | INTEGER (PK) | Identificador único |
| `nome_oficial` | STRING | Nome da categoria |

**Dados de Exemplo:**
```
dim_categoria_id | nome_oficial
1                | Crédito
2                | Investimento
3                | Seguros
```

---

### `dim_produto` - Dimensão de Produtos

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `product_id` | INTEGER (PK) | Identificador único |
| `product_name` | STRING | Nome do produto |
| `dim_categoria_id` | INTEGER (FK) | Referência a categoria |
| `tenor_months` | INTEGER | Prazo em meses |
| `base_rate_apr` | FLOAT | Taxa base anual |

**Dados de Exemplo:**
```
product_id | product_name       | dim_categoria_id | tenor_months | base_rate_apr
1          | Crédito Pessoal    | 1                | 24           | 0.12
2          | Auto               | 1                | 36           | 0.08
3          | Consignado         | 1                | 12           | 0.06
4          | Cartões            | 1                | 1            | 0.15
```

---

### `dim_localidade` - Dimensão de Localidades

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `location_id` | INTEGER (PK) | Identificador único |
| `location_name` | STRING | Nome da localidade |
| `macro_region` | STRING | Macro-região |
| `risk_factor_region` | FLOAT | Fator de risco regional |

**Dados de Exemplo:**
```
location_id | location_name      | macro_region | risk_factor_region
1           | São Paulo          | Capital      | 0.8
2           | Rio de Janeiro     | East         | 1.0
3           | Minas Gerais       | East         | 1.2
4           | Brasília           | Capital      | 0.9
5           | Salvador           | North        | 1.3
```

---

### `fato_contratos` - Tabela Fato

| Coluna | Tipo | Descrição | Restrições |
|--------|------|-----------|-----------|
| `contract_id` | INTEGER (PK) | ID único do contrato | NOT NULL |
| `ano_mes` | STRING | Período YYYYMM | NOT NULL |
| `dim_banks_id` | INTEGER (FK) | Referência a banco | NOT NULL |
| `product_id` | INTEGER (FK) | Referência a produto | NOT NULL |
| `location_id` | INTEGER (FK) | Referência a localidade | NOT NULL |
| `units` | INTEGER | Quantidade de unidades | ≥ 0 |
| `financed_amount` | FLOAT | Valor financiado | > 0 |
| `outstanding_balance` | FLOAT | Saldo devedor | ≥ 0 |
| `dpd` | INTEGER | Dias em atraso | ≥ 0 |
| `risk_score` | FLOAT | Score de risco | 0-1 |

---

## Pipeline de Dados

### Fluxo Completo

```
BRONZE (Raw)
    ↓
    [CSV Files]
    ├── dim_localidade.csv
    ├── dim_produto.csv
    └── fato_contratos.csv
    ↓
SILVER (Validated)
    ↓
    [Schema Enforcer]
    ├── Validação de tipos
    ├── Regras de negócio
    ├── Relacionamentos
    └── Quality Report
    ↓
    [Parquet Files]
    ├── dim_banks.parquet
    ├── dim_categoria.parquet
    ├── dim_localidade.parquet
    ├── dim_produto.parquet
    ├── fato_contratos.parquet
    └── quality_summary.parquet
    ↓
GOLD (Analytics Ready)
    ↓
    [DuckDB Processing]
    └── One Big Table Creation
    ↓
    [Parquet Export]
    └── gold_fato_contratos_detalhada.parquet
    ↓
CONSUMPTION (BI/Streamlit)
    ↓
    [Streamlit Dashboard]
    ├── Visão Geral
    ├── Regiões
    └── Risco & Qualidade
```

### Etapas do Pipeline Silver

1. **Schema Enforcement**: Conversão de tipos, validação NOT NULL
2. **Business Rules**: Validação de limites (mín/máx)
3. **Dimension Creation**: Geração de tabelas dimension
4. **Relationship Validation**: Integridade referencial
5. **Export & Reporting**: Salvamento e geração de relatórios

### Etapas do Pipeline Gold

1. **Register Silver Tables**: Lê Parquet como views no DuckDB
2. **Create Gold Fact**: Desnormalização e cálculo de features
3. **Export to Parquet**: Exportação para consumo

---

## Resumo das Regras de Negócio

### Validações de Schema
- `ano_mes`: Formato YYYYMM convertido para datetime
- `financed_amount`: Numérico positivo
- `outstanding_balance`: Numérico ≥ 0
- `risk_score`: Float entre 0 e 1

### Regras de Limites
- `financed_amount`: Mínimo > 0
- `units`: Mínimo ≥ 0, máximo razoável
- `dpd`: Mínimo ≥ 0, máximo ~120 dias
- `risk_score`: Mínimo ≥ 0, máximo ≤ 1
- `tenor_months`: Entre 1 e 240 meses

### Integridade Referencial
- `dim_banks_id` deve existir em `dim_banks`
- `product_id` deve existir em `dim_produto`
- `location_id` deve existir em `dim_localidade`
- `dim_categoria_id` deve existir em `dim_categoria`

---

## Exemplos de Uso

### Exemplo 1: Filtrar por Banco e Calcular Share

```python
from dashboards.analytics.metrics import ShieldMetrics
import pandas as pd

# Carregar dados
df = pd.read_parquet('medalion-architeture/03-gold-enriched/gold_fato_contratos_detalhada.parquet')

# Filtrar apenas Banco Shield
df_shield = df[df['bank_name'] == 'Banco Shield']

# Calcular métricas
volume = ShieldMetrics.volume_total(df_shield)
market_share = ShieldMetrics.market_share(df, 'Banco Shield')
contratos = ShieldMetrics.contratos_ativos(df_shield)

print(f"Volume: R$ {volume:,.0f}")
print(f"Market Share: {market_share:.2f}%")
print(f"Contratos: {contratos:,}")
```

### Exemplo 2: Análise Regional

```python
# Volume por região
df_regions = ShieldMetrics.group_region(df)
print(df_regions.sort_values('financed_amount', ascending=False))

# Melhor produto por região (Hidra)
top_hidra = ShieldMetrics.region_product(df, 'Hidra Bank')
print(f"Hidra domina em {top_hidra['location_name']} com {top_hidra['product_name']}")
```

### Exemplo 3: Análise de Risco

```python
# Agregação com risco
df_risk = ShieldMetrics.risco_volume_contratos(df)

# Produtos de alto risco
high_risk = df_risk[df_risk['risk_score'] > 0.08]
print(high_risk)

# Risco médio geral
risco_geral = ShieldMetrics.risco_medio(df)
print(f"Risco médio do mercado: {risco_geral:.2f}%")
```

---

## Qualidade de Dados

### Tipos de Erros Registrados

| Tipo de Erro | Descrição | Severidade |
|---|---|---|
| `MISSING_COLUMN` | Coluna obrigatória ausente | 🔴 Crítica |
| `NOT_NULL_VIOLATION` | Campo obrigatório nulo | 🔴 Crítica |
| `TYPE_CAST_ERROR` | Erro ao converter tipo | 🟡 Alta |
| `MIN_VIOLATION` | Valor abaixo do mínimo | 🟡 Alta |
| `MAX_VIOLATION` | Valor acima do máximo | 🟡 Alta |
| `RELATIONSHIP_ERROR` | Referência inválida | 🟡 Alta |

### Relatório de Qualidade (`quality_summary`)

O arquivo `quality_summary_[TIMESTAMP].parquet` contém:
- Total de erros encontrados
- Número de tabelas afetadas
- Contagem por tipo de erro
- Contagem por tabela

---

## Dashboard Streamlit

### Visualizações Principais

**ABA 1: Visão Geral**
- 4 KPIs principais (Volume, Share, Contratos, Risco)
- Gráfico de área temporal (Disputa de Território)
- Gráfico de barras por produto (Share)

**ABA 2: Regiões**
- Gráfico de barras agrupadas (Domínio Geográfico)
- Insight sobre força dos competidores por região

**ABA 3: Risco & Qualidade**
- Scatter plot (Risco × Volume × Contratos)
- Tabela de indicadores de qualidade de dados

---

## Paleta de Cores

| Cor | Código | Uso |
|---|---|---|
| Cyan Neon | `#00F0FF` | Banco Shield |
| Red Neon | `#FF2A2A` | Hidra Bank / Risco |
| Ouro | `#FFD700` | Alertas |
| Dark Background | `#090C10` | Fundo da página |
| Card Background | `#161B22` | Cards |

---
