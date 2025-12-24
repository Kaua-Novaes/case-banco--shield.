RULES_RELATIONSHIPS = {
    "fato_contratos": [
    {
        "fk": "product_id",
        "ref_table": "dim_produto",
        "ref_key": "product_id"
    },
    {
        "fk": "location_id",
        "ref_table": "dim_localidade",
        "ref_key": "location_id"
    },
    {
        "fk": "dim_banks_id",
        "ref_table": "dim_banks",
        "ref_key": "dim_banks_id"
    }
    ],
    "dim_produto": [
    {
        "fk": "dim_categoria_id",
        "ref_table": "dim_categoria",
        "ref_key": "dim_categoria_id"
    },
    ]
}
