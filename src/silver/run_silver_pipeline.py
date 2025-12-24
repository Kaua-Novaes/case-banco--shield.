import pandas as pd
from datetime import datetime
from pathlib import Path
from src.silver.validators.schema_enforcement import NormalizeData
from src.silver.validators.schema_enforcer import SchemaEnforcer
from src.silver.validators.bussines_rules import RulesValidator
from src.silver.validators.dimension_conformation import DimensionBuilder
from src.silver.validators.relationship_validator import RelationshipValidator
from src.silver.rules.models import (
    FATO_CONTRATOS_SCHEMA,
    DIM_PRODUTO_SCHEMA,
    DIM_LOCALIDADE_SCHEMA
)
from src.silver.rules.bussines_rules import BUSSINES_RULES
from src.silver.rules.dimension_rules import DIMENSION_RULES
from src.silver.rules.relationship import RULES_RELATIONSHIPS
from src.utils.paths import BRONZE_DIR, SILVER_DIR


class SilverPipelineExecutor:
    """
    Executor da camada Silver do pipeline de dados.
    
    Responsável por:
    - Validação de schema
    - Aplicação de regras de negócio
    - Criação de dimensões
    - Validação de relacionamentos
    - Salvamento de tabelas em CSV
    - Registro de qualidade de dados
    """
    
    def __init__(self, bronze_dir: Path, silver_dir: Path):
        self.bronze_dir = bronze_dir
        self.silver_dir = silver_dir
        self.execution_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.quality_errors = []
        
        # Criar diretório silver se não existir
        Path(self.silver_dir).mkdir(parents=True, exist_ok=True)
    
    def run(self):
        """Executa o pipeline completo da camada Silver"""
        print("\n" + "="*80)
        print("INICIANDO PIPELINE SILVER")
        print("="*80 + "\n")
        
        # Step 1: Schema Enforcement
        print("[1/5] Executando validação de schema...")
        silver_dfs, schema_errors = self._schema_enforcement()
        self.quality_errors.extend(schema_errors)
        
        # Step 2: Business Rules
        print("[2/5] Aplicando regras de negócio...")
        validated_dfs, rules_errors = self._business_rules(silver_dfs)
        self.quality_errors.extend(rules_errors)
        
        # Step 3: Dimension Creation
        print("[3/5] Criando novas dimensões...")
        silver_dfs, dimension_errors = self._dimension_creation(validated_dfs)
        self.quality_errors.extend(dimension_errors)
        
        # Step 4: Relationship Enforcement
        print("[4/5] Validando relacionamentos...")
        final_dfs, relationship_errors = self._relationship_enforcement(silver_dfs)
        self.quality_errors.extend(relationship_errors)
        
        # Step 5: Save and Quality Report
        print("[5/5] Salvando tabelas e gerando relatório de qualidade...\n")
        self._save_tables(final_dfs)
        self._save_quality_report()
        
        print("="*80)
        print("PIPELINE SILVER FINALIZADO COM SUCESSO!")
        print("="*80 + "\n")
        
        return final_dfs, self.quality_errors
    
    def _schema_enforcement(self):
        """Step 1: Valida schema dos dados"""
        schema_map = {
            "fato_contratos": FATO_CONTRATOS_SCHEMA,
            "dim_produto": DIM_PRODUTO_SCHEMA,
            "dim_localidade": DIM_LOCALIDADE_SCHEMA
        }
        
        normalize_data = NormalizeData(
            schema_enforcer=SchemaEnforcer,
            input_dir=self.bronze_dir,
            schema_map=schema_map
        )
        
        silver_dfs, schema_errors = normalize_data.run()
        
        print(f"   ✓ {len(silver_dfs)} tabelas processadas")
        print(f"   ⚠ {len(schema_errors)} erros encontrados")
        
        return silver_dfs, schema_errors
    
    def _business_rules(self, silver_dfs):
        """Step 2: Aplica regras de negócio"""
        rules_errors = []
        validated_dfs = {}
        
        for table_name, df in silver_dfs.items():
            validator = RulesValidator(
                df=df,
                table_name=table_name,
                rules=BUSSINES_RULES
            )
            
            df_valid, errors = validator.run()
            validated_dfs[table_name] = df_valid
            
            if errors:
                rules_errors.extend(errors)
                print(f"   ⚠ Tabela '{table_name}': {len(errors)} erros de regra")
            else:
                print(f"   ✓ Tabela '{table_name}': validado")
        
        return validated_dfs, rules_errors
    
    def _dimension_creation(self, validated_dfs):
        """Step 3: Cria novas dimensões e mapeia relacionamentos"""
        dimension_errors = []
        silver_dims = {}
        
        # Criar dim_banks
        bank_dim = DimensionBuilder.build_dimension(
            df=validated_dfs['fato_contratos'],
            column='bank',
            dim_name='dim_banks',
            dimension_rule=DIMENSION_RULES
        )
        silver_dims['dim_banks'] = bank_dim[0]
        print(f"   ✓ Dimensão 'dim_banks' criada ({len(bank_dim[0])} registros)")
        
        # Mapear fato_contratos com dim_banks
        fato_contratos_updated = DimensionBuilder.map_and_validate(
            fact_d=validated_dfs['fato_contratos'],
            dim_df=silver_dims['dim_banks'],
            fact_column='bank',
            dim_column='nome_oficial',
            dim_id_name='dim_banks_id',
            table_name='fato_contratos'
        )
        
        # Criar dim_categoria
        category_dim = DimensionBuilder.build_dimension(
            df=validated_dfs['dim_produto'],
            column='category',  
            dim_name='dim_categoria',
            dimension_rule={}
        )
        silver_dims['dim_categoria'] = category_dim[0]
        print(f"   ✓ Dimensão 'dim_categoria' criada ({len(category_dim[0])} registros)")
        
        # Mapear dim_produto com dim_categoria
        dim_produto_updated = DimensionBuilder.map_and_validate(
            fact_d=validated_dfs['dim_produto'],
            dim_df=silver_dims['dim_categoria'],
            fact_column='category',
            dim_column='nome_oficial',
            dim_id_name='dim_categoria_id',
            table_name='dim_produto'
        )
        
        # Atualizar dfs com dimensões criadas e mapeadas
        validated_dfs['fato_contratos'] = fato_contratos_updated[0]
        validated_dfs['dim_produto'] = dim_produto_updated[0]
        validated_dfs['dim_banks'] = silver_dims['dim_banks']
        validated_dfs['dim_categoria'] = silver_dims['dim_categoria']
        
        return validated_dfs, dimension_errors
    
    def _relationship_enforcement(self, silver_dfs):
        """Step 4: Valida relacionamentos entre tabelas"""
        relationship_errors = []
        relationship_dfs = {}
        
        for table_name, df in silver_dfs.items():
            relationship_rules = RULES_RELATIONSHIPS.get(table_name, [])
            
            if not relationship_rules:
                relationship_dfs[table_name] = df
                continue
            
            relationship_validator = RelationshipValidator(
                fact_df=df,
                table_name=table_name,
                reference_tables=silver_dfs,
                relationships=relationship_rules
            )
            
            df_valid, errors = relationship_validator.run()
            relationship_dfs[table_name] = df_valid
            
            if errors:
                relationship_errors.extend(errors)
                total_errors = sum(len(e) for e in errors)
                print(f"   ⚠ Tabela '{table_name}': {total_errors} erros de relacionamento")
            else:
                print(f"   ✓ Tabela '{table_name}': relacionamentos válidos")
        
        return relationship_dfs, relationship_errors
    
    def _save_tables(self, final_dfs):
        """Salva tabelas processadas como CSV na camada Silver"""
        for table_name, df in final_dfs.items():
            output_path = Path(self.silver_dir) / f"{table_name}.parquet"
            df.to_parquet(output_path, index=False)
            print(f"   ✓ {table_name}.parquet salvo ({len(df)} registros)")
    
    def _save_quality_report(self):
        """Salva relatório de qualidade com colunas padronizadas"""
        all_errors_list = []
        
        # Definindo as colunas que vão ser usadas no relatório final
        cols_desejadas = ['tabela', 'coluna', 'tipo_erro', 'valor_encontrado', 'descricao', 'data_processamento']

        for error in self.quality_errors:
            # Converter para lista de dicts independente do formato original
            temp_list = []
            if isinstance(error, pd.DataFrame):
                temp_list = error.to_dict('records')
            elif isinstance(error, dict):
                temp_list = [error]
            elif isinstance(error, list):
                temp_list = error
            
            # Limpeza: Manter apenas as colunas de erro, descartando colunas de dados do contrato
            for entry in temp_list:
                # Só adiciona se a entrada tiver as chaves principais de erro
                if any(key in entry for key in ['tipo_erro', 'error_type', 'column', 'coluna']):
                    clean_entry = {k: v for k, v in entry.items() if k in cols_desejadas}
                    all_errors_list.append(clean_entry)

        if not all_errors_list:
            print("   ✓ Nenhum erro encontrado")
            quality_report = pd.DataFrame(columns=cols_desejadas) # DF vazio com colunas fixas
        else:
            quality_report = pd.DataFrame(all_errors_list)
        
        # Adiciona o timestamp de execução
        quality_report['execution_timestamp'] = self.execution_timestamp
        
        output_path = Path(self.silver_dir) / f"quality_report_{self.execution_timestamp}.parquet"
        
        # Garante que não haverá mistura de colunas estranhas
        quality_report.to_parquet(output_path, index=False)
        
        
        total_errors = len(quality_report)
        print(f"   ✓ Relatório de qualidade salvo ({total_errors} erros registrados)")
        
        # Gerar e salvar resumo de qualidade
        self._save_quality_summary(quality_report)
        
        if total_errors > 0:
            print(f"\n   Resumo de erros por tipo:")
            # Tentar diferentes nomes de coluna para tipo de erro
            error_type_cols = ['error_type', 'tipo_erro', 'tipo_de_erro', 'rule']
            error_type_col = None
            for col in error_type_cols:
                if col in quality_report.columns:
                    error_type_col = col
                    break
            
            if error_type_col:
                error_counts = quality_report[error_type_col].value_counts()
                for error_type, count in error_counts.items():
                    print(f"      - {error_type}: {count}")
    


    
    def _save_quality_summary(self, quality_report):
        """Salva um resumo consolidado do relatório de qualidade"""
        summary_data = []
        
        if quality_report.empty:
            summary_df = pd.DataFrame({
                'metric': ['Total de Erros', 'Tabelas com Erros'],
                'valor': [0, 0],
                'timestamp': [self.execution_timestamp, self.execution_timestamp]
            })
        else:
            # Contar erros por tabela
            table_col = None
            for col in ['tabela', 'table']:
                if col in quality_report.columns:
                    table_col = col
                    break
            
            error_type_col = None
            for col in ['error_type', 'tipo_erro', 'tipo_de_erro', 'rule']:
                if col in quality_report.columns:
                    error_type_col = col
                    break
            
            # Total de erros
            total_errors = len(quality_report)
            
            # Tabelas afetadas
            if table_col:
                tables_affected = quality_report[table_col].nunique()
            else:
                tables_affected = 0
            
            summary_data = {
                'Total de Erros': [total_errors],
                'Tabelas com Erros': [tables_affected],
                'Timestamp': [self.execution_timestamp]
            }
            
            # Erros por tipo
            if error_type_col:
                for error_type, count in quality_report[error_type_col].value_counts().items():
                    summary_data[f'Erros {error_type}'] = [count]
            
            # Erros por tabela
            if table_col:
                for table, count in quality_report[table_col].value_counts().items():
                    summary_data[f'{table} - Erros'] = [count]
            
            summary_df = pd.DataFrame(summary_data)
        
        # Salvar resumo
        summary_path = Path(self.silver_dir) / f"quality_summary.parquet"
        summary_df.to_parquet(summary_path, index=False)
        print(f"   ✓ Resumo de qualidade salvo")


if __name__ == "__main__":
    executor = SilverPipelineExecutor(
        bronze_dir=BRONZE_DIR,
        silver_dir=SILVER_DIR
    )
    
    final_dfs, quality_errors = executor.run()
