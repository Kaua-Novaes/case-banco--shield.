"""
Módulo de regras de domínio para validação de dados.

Este arquivo define e controla as regras de negócio aplicadas às tabelas de dados,
incluindo validações de valores mínimos e máximos para as colunas de cada entidade.
"""

BUSSINES_RULES = {
    "fato_contratos": {
        "financed_amount": {
            "min": 0
        },
        "outstanding_balance": {
            "min": 0
        },
        "delinquent_amount_30p": {
            "min": 0
        },
        "units": {
            "min": 0
        },
        "risk_score": {
            "min": 0,
            "max": 1
        }
    }
}
