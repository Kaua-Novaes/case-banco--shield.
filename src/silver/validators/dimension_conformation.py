import pandas as pd
import re
from datetime import datetime

class DimensionBuilder:
    """
    Ferramentas para transformar colunas Silver.
    """

    @staticmethod
    def clean_text(text):
        """
        :param text: texto que será limpo e padronizado para o formato esperado
        """
        if pd.isna(text): return None
        text = str(text).lower().strip()
        text = re.sub(r'[^a-z0-9]', '', text) 
        return text

   
    @staticmethod
    def apply_dimension_rule(value:str, dimension_rule:dict):
        """
        :param value: valor que será tratado
        :param dimension_rule: dicionario de regras para a dimensão
        """
        value_clean = value.strip().title()
        return dimension_rule.get(value_clean, value_clean)

    @staticmethod
    def build_dimension(df: pd.DataFrame, column: str, dim_name: str, dimension_rule:dict):
        """
        :param df: dataframe de origem dos dados
        :param column: coluna que será transformada em tabela
        :param dim_name: nome da nova dimension que será criada
        :param dimension_rule: regras para os nomes da dimmension
        """
        
        #-- Cria um DataFrame temporário com a coluna original e a versão limpa
        temp_df = df[[column]].drop_duplicates().dropna().copy()
        

        temp_df['nome_oficial'] = temp_df[column].apply(lambda x: DimensionBuilder.apply_dimension_rule(x, dimension_rule))
        df[column] = df[column].apply(lambda x: DimensionBuilder.apply_dimension_rule(x, dimension_rule))
        temp_df['key_clean'] = temp_df['nome_oficial'].apply(DimensionBuilder.clean_text)

        #-- Remove duplicatas baseado na coluna tratada
        dim = temp_df.drop_duplicates(subset=['key_clean']).copy()

        #-- Cria o ID sequencial
        dim[f"{dim_name}_id"] = range(1, len(dim) + 1)
        #-- Retorna a dimensão e o mapa de de-para para atualizar a tabela fato
        return dim[[f"{dim_name}_id", 'nome_oficial']], temp_df




    @staticmethod
    def map_and_validate(fact_d:pd.DataFrame, dim_df:pd.DataFrame, fact_column:str, dim_column:str, dim_id_name:str, table_name:str):
        """
        :param fact_df: df de origem ex: fato_contratos.csv
        :param dim_df: dimension que será criada a partir do df de origem
        :param fact_column: coluna do df de origem
        :param dim_column: coluna do dim que será feita o merge
        :param dim_id_name: id da coluna FK da dimension criada
        :param table_name: nome da tabela para o log de qualidade
        """

        fact_df = fact_d.copy()
        #-- Tenta o merge (Left Join para não perder linhas da fato)
        fact_df = fact_df.merge(
            dim_df[[dim_id_name, dim_column]], 
            left_on=fact_column, 
            right_on=dim_column, 
            how="left"
        )

        errors_list = []

        #-- Identifica registros que não deram match (ID ficou nulo)
        # Isso captura tanto valores que eram Nulos na origem quanto valores que não existem na dimensão
        invalid_mask = fact_df[dim_id_name].isna()
        
        if invalid_mask.any():
            # Extrai os valores únicos que falharam para não poluir a lista de erros
            missing_values = fact_df.loc[invalid_mask, fact_column].unique()
            
            for valor in missing_values:
                tipo_erro = "NOT_NULL_VIOLATION" if pd.isna(valor) else "DIMENSION_NOT_FOUND"
                descricao = "Campo obrigatório nulo" if pd.isna(valor) else f"Valor '{valor}' não encontrado na dimensão {dim_id_name}"
                
                errors_list.append({
                    "tabela": table_name,
                    "coluna": fact_column,
                    "tipo_erro": tipo_erro,
                    "valor_encontrado": valor,
                    "descricao": descricao,
                    "data_processamento": datetime.now()
                })
 

        #-- Limpeza: remove a coluna de texto original e a coluna redundante do merge
        # Mantém apenas o ID na tabela fato
        fact_df = fact_df.drop(columns=[fact_column, dim_column])
        
        return fact_df, errors_list