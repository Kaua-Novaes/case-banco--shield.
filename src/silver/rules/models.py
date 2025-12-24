"""
Módulo de validação de esquemas para a camada Silver.

Este arquivo define e valida os esquemas de dados (data types) 
para as tabelas de fatos e dimensões da camada Silver do Data Lake.
"""

FATO_CONTRATOS_SCHEMA =  {
    "contract_id": "string",
    "ano_mes": "datetime64[ns]",
    "bank": "string",
    "product_id": "int64",
    "location_id": "int64",
    "units": "int64",
    "financed_amount": "float64",
    "outstanding_balance": "float64",
    "dpd": "int64",
    "delinquent_amount_30p": "float64",
    "risk_score": "float64"
}

DIM_PRODUTO_SCHEMA = {
    "product_id": "int64",
    "product_name": "string",
    "category": "string",
    "tenor_months": "int64",
    "base_rate_apr": "float64"
}

DIM_LOCALIDADE_SCHEMA = {
    "location_id": "int64",
    "location_name": "string",
    "macro_region": "string",
    "risk_factor_region": "float64"
}

