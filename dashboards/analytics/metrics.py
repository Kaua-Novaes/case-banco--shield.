import pandas as pd

# Exibir todas as linhas e colunas
"""
Modulo para decentralizar o cálculo de métricas específicas do Banco Shield.
"""


import pandas as pd

class ShieldMetrics:

    @staticmethod
    def volume_total(df):
        return df['financed_amount'].sum()

    @staticmethod
    def options(df,column):
        return df[column].unique()

    @staticmethod
    def market_share(df, banco_ref='Banco Shield'):
        total = df['financed_amount'].sum()
        if total == 0:
            return 0
        shield = df[df['bank_name'] == banco_ref]['financed_amount'].sum()
        return (shield / total) * 100

    @staticmethod
    def contratos_ativos(df):
        return len(df['contract_id'])

    @staticmethod
    def risco_medio(df):
        return df['risk_score'].mean() * 100

    @staticmethod
    def volume_tempo(df):
        df['ano_mes'] = df['ano_mes'].apply(lambda x: f"{x[:4]}-{x[4:6]}")
        return (
            df.groupby(['ano_mes', 'bank_name'])['financed_amount']
            .sum()
            .reset_index()
        )

    @staticmethod
    def volume_regiao_total(df):
        return (
            df
            .groupby(['location_name', 'bank_name','ano_mes'], as_index=False)
            ['financed_amount']
            .sum()
        )
    
    @staticmethod
    def share_por_produto(df):
        return (
            df.groupby(['product_name', 'bank_name'])['financed_amount']
            .sum()
            .reset_index()
        )
    

    @staticmethod
    def region_product(df, banco_ref='Banco Hidra'):
        return (
            df[df['bank_name'] == banco_ref]
            .groupby(['location_name', 'product_name'])['financed_amount']
            .sum()
            .reset_index()
            .sort_values('financed_amount', ascending=False)
            .iloc[0][['location_name', 'product_name']]
            .to_dict()
        )
    @staticmethod
    def group_region(df):
        return (
            df.groupby(['location_name', 'bank_name'])['financed_amount']
            .sum()
            .reset_index()
        )
    
    @staticmethod
    def risco_volume_contratos(df):
        return df.groupby(['product_name', 'bank_name']).agg({
            'financed_amount': 'sum', 
            'risk_score': 'mean',
            'contract_id': 'count'
        }).reset_index()





if __name__ == "__main__":

    # Ler o arquivo Parquet
    df = pd.read_parquet('/Users/kauanovaes/Desktop/Analise de dados - Estudo/medalion-architeture/02-silver-validated/quality_summary_20251224_015213.parquet')
    

    print(df.to_json(orient="records"))