import pandas as pd
from datetime import datetime

class RelationshipValidator:
    """
    Valida integridade referencial entre tabelas Silver
    """

    def __init__(
        self,
        fact_df: pd.DataFrame,
        table_name: str,
        reference_tables: dict[str, pd.DataFrame],
        relationships: list[dict]
    ):
        """
        :param fact_df: DataFrame da tabela fato
        :param table_name: nome da tabela fato
        :param reference_tables: dict com dfs das dimensões
        :param relationships: regras de relacionamento
        """
        self.fact_df = fact_df
        self.table_name = table_name
        self.reference_tables = reference_tables
        self.relationships = relationships



    def run(self):
        """
        Valida relacionamentos entre tabela fato e dimensões.
        
        Verifica se todas as chaves estrangeiras existem nas tabelas de referência
        e remove registros com referências inválidas.
        
        Returns:
            tuple: (DataFrame validado, DataFrame com erros encontrados)
        """
        dq_errors = []

        df_valid = self.fact_df.copy()
        
        for rel in self.relationships:
            fk = rel["fk"]
            ref_table = rel["ref_table"]
            ref_key = rel["ref_key"]

            dim_df = self.reference_tables.get(ref_table)
            
            if dim_df is None:
                raise ValueError(f"Tabela de referência {ref_table} não encontrada")
            
            
            invalid = df_valid[~df_valid[fk].isin(dim_df[ref_key])]
            if not invalid.empty:
                dq_errors.append(
                {
                    "tabela": self.table_name,
                    "coluna": fk,
                    "tipo_erro": "FK_NOT_FOUND",
                    "valor_encontrado": None,
                    "descricao": f"Chave estrangeira {fk} não encontrada na tabela {ref_table}",
                    "data_processamento": datetime.now()
                }
                )

                # remove inválidos
                df_valid = df_valid[df_valid[fk].isin(dim_df[ref_key])]

        return df_valid, dq_errors
