""""
Modulo para aplicar filtros específicos do Banco Shield.
"""
import pandas as pd
import numpy as np

class ShieldFilters:
    @staticmethod
    def apply_filters(df, bancos, produtos, regioes):
        """    
        :param df: DataFrame a ser filtrado
        :param bancos: nome do banco
        :param produtos: nome do produto
        :param regioes: nome da região
        """
        bancos = bancos if bancos else df['bank_name'].unique().tolist()
        produtos = produtos if produtos else df['product_name'].unique().tolist()
        regioes = regioes if regioes else df['location_name'].unique().tolist()
        
        return df[
            df['bank_name'].isin(bancos) &
            df['product_name'].isin(produtos) &
            df['location_name'].isin(regioes)
        ]
    


def load_data_teste():
    dates = pd.date_range(start="2024-01-01", end="2025-12-01", freq="MS")
    bancos = ["Banco Shield", "Hidra Bank"]
    produtos = ["Crédito Pessoal", "Auto", "Consignado", "Cartões"]
    regioes = ["North", "South", "East", "West", "Capital"]
    
    data = []
    for date in dates:
        for banco in bancos:
            factor = 1.2 if banco == "Hidra Bank" else 1.0 # Hidra crescendo
            for prod in produtos:
                vol = np.random.randint(50, 800) * 1000 * factor
                data.append({
                    "data": date,
                    "banco": banco,
                    "produto": prod,
                    "regiao": np.random.choice(regioes),
                    "volume": vol,
                    "contratos": int(vol / np.random.randint(1000, 5000)),
                    "risco": np.random.uniform(0.02, 0.18) if banco == "Hidra Bank" else np.random.uniform(0.01, 0.08)
                })
    df = pd.DataFrame(data)
    df['ano_mes'] = df['data'].dt.strftime('%Y-%m')
    return df