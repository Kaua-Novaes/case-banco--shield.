from datetime import datetime
import pandas as pd

class RulesValidator:
    """
    Valida dados contra regras de negócio, verificando valores mínimos e máximos.
    
    Registra violações e retorna o dataframe filtrado com os dados válidos.
    """
    def __init__(self, df: pd.DataFrame, table_name: str, rules: dict):
        self.df = df
        self.table_name = table_name
        self.rules = rules.get(table_name, {})
        self.errors = []

    def run(self):
        for col, constraints in self.rules.items():
            if col not in self.df.columns:
                continue

            if "min" in constraints:
                invalid = self.df[self.df[col] < constraints["min"]]
                self._log_errors(col, invalid, "MIN_VIOLATION")

                self.df = self.df[self.df[col] >= constraints["min"]]

            if "max" in constraints:
                invalid = self.df[self.df[col] > constraints["max"]]
                self._log_errors(col, invalid, "MAX_VIOLATION")

                self.df = self.df[self.df[col] <= constraints["max"]]

        return self.df, self.errors

    def _log_errors(self, col, invalid_df, error_type):
        for _, row in invalid_df.iterrows():
            self.errors.append({
                "tabela": self.table_name,
                "coluna": col,
                "tipo_erro": error_type,
                "valor_encontrado": row[col],
                "descricao": f"Violação da regra {error_type}",
                "data_processamento": datetime.now()
            })
