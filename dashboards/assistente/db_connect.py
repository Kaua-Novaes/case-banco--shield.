import duckdb
from pathlib import Path
import re
class DB:
    """
    Classe para gerenciar a conexão com o banco de dados DuckDB.
    para o assistente de IA.
    """


    ALLOWED_VIEW = "ai_contratos"

    # Palavras proibidas (DDL / DML / risco)
    FORBIDDEN_KEYWORDS = [
        "insert", "update", "delete", "drop",
        "create", "alter", "truncate",
        "attach", "detach", "copy",
        "pragma", "export", "import",
        "with", "join"
    ]

    def __init__(self, gold_dir: Path):
        """
        :param gold_dir: Diretório do nível Gold
        """

        self.db_path = gold_dir / "gold_analytics.db"
        self.gold_dir = gold_dir

        self.con = duckdb.connect(str(self.db_path))


    def _validate_query(self, query: str):
        """
        Valida se a query é segura para execução pela IA.
        """
        q = query.lower().strip()

        if not q.startswith("select"):
            raise ValueError("Apenas queries SELECT são permitidas.")

        for keyword in self.FORBIDDEN_KEYWORDS:
            if re.search(rf"\b{keyword}\b", q):
                raise ValueError(f"Uso proibido da palavra-chave: {keyword}")

        # if f"from {self.ALLOWED_VIEW}" not in q:
        #     raise ValueError(
        #         f"Queries devem consultar exclusivamente a view '{self.ALLOWED_VIEW}'."
        #     )

    def execute_query(self, query: str):
        """
        Executa uma query SQL no banco de dados DuckDB.

        :param query: Query SQL a ser executada
        :return: Resultado da query como um DataFrame Pandas
        """
        self._validate_query(query)
        result = self.con.execute(query).fetchdf()
        return result
    


