import duckdb
from pathlib import Path
from src.utils.paths import GOLD_DIR, SILVER_DIR

class GoldPipelineExecutor:
    """
    Camada Gold do Banco Shield.
    Responsável por transformar dados validados da Silver
    em modelos analíticos prontos para consumo (BI / Streamlit).
    """

    def __init__(self, silver_dir: Path, gold_dir: Path):
        self.silver_dir = silver_dir
        self.gold_dir = gold_dir

        self.db_path = self.gold_dir / "gold_analytics.db"
        self.gold_dir.mkdir(parents=True, exist_ok=True)

        self.con = duckdb.connect(str(self.db_path))

    def run(self):
        print("\n=== INICIANDO PIPELINE GOLD ===\n")

        self._register_silver_tables()
        self._create_gold_fact()
        self._create_ai_view()     
        self._export_parquet()

        print("\n=== PIPELINE GOLD FINALIZADO ===\n")

    # ------------------------------------------------------------------
    # 1. REGISTRO DAS TABELAS SILVER
    # ------------------------------------------------------------------
    def _register_silver_tables(self):
        """
        Registra os arquivos Parquet da Silver como views no DuckDB.
        """
        for file in self.silver_dir.glob("*.parquet"):
            if "quality" in file.name:
                continue

            table_name = file.stem
            self.con.execute(f"""
                CREATE OR REPLACE VIEW stg_{table_name} AS
                SELECT * FROM read_parquet('{file}')
            """)

    # ------------------------------------------------------------------
    # 2. ONE BIG TABLE (FATO DESNORMALIZADA)
    # ------------------------------------------------------------------
    def _create_gold_fact(self):
        """
        Cria a tabela fato desnormalizada (One Big Table),
        otimizada para consumo analítico.
        """
        query = """
        CREATE OR REPLACE TABLE gold_fato_contratos_detalhada AS
        SELECT
            -- Identificadores
            f.contract_id,
            f.ano_mes,

            -- Banco
            f.dim_banks_id,
            b.nome_oficial AS bank_name,
            CASE WHEN f.dim_banks_id <> 1 THEN 1 ELSE 0 END AS is_competitor,

            -- Produto
            p.product_id,
            p.product_name,
            c.nome_oficial AS category_name,
            p.tenor_months AS prazo,
            p.base_rate_apr AS taxa_base,

            -- Localidade
            l.location_id,
            l.location_name,
            l.macro_region,
            l.risk_factor_region AS regional_risk_factor,

            -- Métricas principais
            f.units,
            f.financed_amount,
            f.outstanding_balance,
            f.dpd AS dpd_30,
            f.risk_score,

            -- Features de negócio
            (f.outstanding_balance / NULLIF(f.financed_amount, 0)) AS pct_amortized,
            CASE WHEN f.dpd >= 30 THEN 1 ELSE 0 END AS is_high_risk

        FROM stg_fato_contratos f
        LEFT JOIN stg_dim_banks b
            ON f.dim_banks_id = b.dim_banks_id
        LEFT JOIN stg_dim_produto p
            ON f.product_id = p.product_id
        LEFT JOIN stg_dim_categoria c
            ON p.dim_categoria_id = c.dim_categoria_id
        LEFT JOIN stg_dim_localidade l
            ON f.location_id = l.location_id
        """
        self.con.execute(query)


    # ------------------------------------------------------------------
    # 3. EXPORTAÇÃO PARA PARQUET
    # ------------------------------------------------------------------
    def _export_parquet(self):
        """
        Exporta a tabela Gold principal para Parquet,
        garantindo performance no Streamlit.
        """
        output_file = self.gold_dir / "gold_fato_contratos_detalhada.parquet"

        self.con.execute(f"""
            COPY gold_fato_contratos_detalhada
            TO '{output_file}'
            (FORMAT PARQUET)
        """)


    # ------------------------------------------------------------------
    # 4. VIEW SEMÂNTICA PARA IA
    # ------------------------------------------------------------------
    def _create_ai_view(self):
        """
        Cria uma view semântica simplificada
        para consumo da IA (LLM).
        """
        self.con.execute("""
            CREATE OR REPLACE VIEW ai_contratos AS
            SELECT
                ano_mes,
                bank_name,
                contract_id,
                is_competitor,
                product_name,
                category_name,
                prazo,
                taxa_base,
                location_name,
                macro_region,
                regional_risk_factor,
                units,
                financed_amount,
                outstanding_balance,
                dpd_30,
                risk_score,
                is_high_risk,
                pct_amortized
            FROM gold_fato_contratos_detalhada
        """)


if __name__ == "__main__":

    gold_executor = GoldPipelineExecutor(SILVER_DIR, GOLD_DIR)
    gold_executor.run()