"""
Módulo para definir os caminhos dos diretórios do projeto.

Este módulo centraliza todas as configurações de caminhos utilizadas 
em todo o projeto, seguindo o padrão de Arquitetura Medallion.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "medalion-architeture"

BRONZE_DIR = DATA_DIR / "01-bronze-raw"
SILVER_DIR = DATA_DIR / "02-silver-validated"
GOLD_DIR   = DATA_DIR / "03-gold-enriched"
