"""
Pipeline Completo: Silver + Gold

Este arquivo executa a pipeline de dados completa:
1. Camada Silver: Validação, normalização e transformação dos dados brutos
2. Camada Gold: Criação de modelos analíticos e métricas para consumo

Uso:
    python run_full_pipeline.py
"""

import sys
from pathlib import Path
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.silver.run_silver_pipeline import SilverPipelineExecutor
from src.gold.database import GoldPipelineExecutor
from src.utils.paths import BRONZE_DIR, SILVER_DIR, GOLD_DIR


class FullPipelineExecutor:
    """
    Executor da pipeline completa de dados (Silver + Gold)
    """
    
    def __init__(self):
        self.start_time = datetime.now()
        self.silver_executor = SilverPipelineExecutor(
            bronze_dir=BRONZE_DIR,
            silver_dir=SILVER_DIR
        )
        self.gold_executor = GoldPipelineExecutor(
            silver_dir=SILVER_DIR,
            gold_dir=GOLD_DIR
        )
    
    def run(self):
        """Executa a pipeline completa"""
        try:
            print("\n" + "="*80)
            print("INICIANDO PIPELINE COMPLETA (SILVER + GOLD)")
            print("="*80 + "\n")
            
            # Step 1: Executar Silver Pipeline
            print("ETAPA 1: PROCESSANDO CAMADA SILVER")
            print("-" * 80)
            final_dfs_silver, quality_errors = self.silver_executor.run()
            
            # Step 2: Executar Gold Pipeline
            print("\nETAPA 2: PROCESSANDO CAMADA GOLD")
            print("-" * 80)
            self.gold_executor.run()
            
            
        except Exception as e:
            print(f"\nERRO DURANTE A EXECUÇÃO DA PIPELINE: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
 



if __name__ == "__main__":
    executor = FullPipelineExecutor()
    executor.run()
