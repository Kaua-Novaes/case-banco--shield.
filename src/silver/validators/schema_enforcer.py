import pandas as pd
from datetime import datetime

class SchemaEnforcer:
    """
    Responsável por:
    - aplicar schema esperado
    - validar NOT NULL
    - registrar erros estruturais
    """

    def __init__(self, df: pd.DataFrame, schema: dict, table_name: str, errros_list:list):
        """
        :param df: dataframe da tabela que está sendo tratada
        :param schema: json de schema de tipos esperados por cada tabela
        :param table_name: nome da tabela de origem dos dados
        :param errros_list: array que será armazenado os erros
        """

        self.df_raw = df.copy()
        self.schema = schema
        self.table_name = table_name
        
        
        #-- lista dedicada para controle de qualidade de validação dos dados
        self.errors = errros_list

        #-- tudo começa como string
        for col in self.df_raw.columns:
            self.df_raw[col] = self.df_raw[col].astype("string")


    def _cast_column(self, col: str, dtype: str):
        """
        :param col: nome da coluna no dataframe
        :param dtype: tipo de dados esperado na coluna
        """

        try:
            # Se o destino for inteiro, passamos por float primeiro para evitar o erro '1013.0'
            if "int" in dtype.lower():
                self.df_raw[col] = pd.to_numeric(self.df_raw[col], errors='raise').astype(dtype)
            #tratamento para o tipo datetime
            elif "datetime" in dtype.lower():
                self.df_raw[col] = pd.to_datetime(
                    self.df_raw[col].astype(str) + "01",
                    format="%Y%m%d",
                    errors="raise"
                )
            else:
                self.df_raw[col] = self.df_raw[col].astype(dtype)
        except Exception as e:
            print(f"Erro ao converter coluna {col} para {dtype}: {e}")
            invalid_rows = self.df_raw[
                self.df_raw[col].isna() | self.df_raw[col].str.strip().eq("")
            ]

            for _, row in invalid_rows.iterrows():
                self.errors.append({
                    "tabela": self.table_name,
                    "coluna": col,
                    "tipo_erro": "TYPE_CAST_ERROR",
                    "valor_encontrado": row[col],
                    "descricao": f"Não foi possível converter para {dtype}",
                    "data_processamento": datetime.now()
                })

            # remove registros inválidos
            self.df_raw = self.df_raw.drop(invalid_rows.index)


    def _check_not_null(self, col: str):
        """
        :param col: nome da coluna que está sendo tratadad
        """
        
        null_rows = self.df_raw[
        self.df_raw[col].isna() | 
        (self.df_raw[col].astype(str).str.lower() == "nan") |
        (self.df_raw[col].astype(str).str.strip() == "")
    ]

        for _, row in null_rows.iterrows():
            self.errors.append({
                "tabela": self.table_name,
                "coluna": col,
                "tipo_erro": "NOT_NULL_VIOLATION",
                "valor_encontrado": None,
                "descricao": "Campo obrigatório nulo",
                "data_processamento": datetime.now()
            })

        self.df_raw = self.df_raw[self.df_raw[col].notna()]


    def run(self):
        for col, dtype in self.schema.items():
            if col not in self.df_raw.columns:
                self.errors.append({
                    "tabela": self.table_name,
                    "coluna": col,
                    "tipo_erro": "MISSING_COLUMN",
                    "valor_encontrado": None,
                    "descricao": "Coluna obrigatória ausente",
                    "data_processamento": datetime.now()
                })
                continue

            self._check_not_null(col)
            self._cast_column(col, dtype)


        return self.df_raw
