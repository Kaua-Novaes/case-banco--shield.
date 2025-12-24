import os
import pandas as pd
from src.silver.validators.schema_enforcer import SchemaEnforcer


class NormalizeData:
    """
    Responsável por:
    - Varrer todos arquivos da camada bronze
    - Verificar se está mapeada no Schema do models
    - Transformar o csv em dataframe
    - Normalizar utilizadando a classe schemmaenforcer
    """

    def __init__(self,schema_enforcer:SchemaEnforcer,input_dir:str,schema_map:dict):
        """
        :param schema_enforecer: classe schemaenforcer para tratamento dos dados
        :param input_dir: diretório de entrada com os dados em csv
        :param schema_map: map de schema de acordo com o nome do diretório
        """
        
        self.schema_enforcer = schema_enforcer
        self.input_dir = input_dir
        self.schema_map = schema_map

        #-- lista de erros 
        self.errors = []

        #--lista de DFs que serão retornados
        self.df_silver = {}



    def _list_dir(self)->list:
        return os.listdir(self.input_dir)


    def run(self):
        #utiliza a função para listar os diretórios do diretorio de entrada
        list_dir = self._list_dir()

        for file in list_dir:
            #-- informaçoes de nome e formato dos arquivos
            input_path = os.path.join(self.input_dir,file)
            name,ext = os.path.splitext(file)

            #-- saida do arquivo como parquet
            schemma = self.schema_map.get(name,"") 


            #-- pula o arquivo se caso nao estiver mapeado no map de diretórios
            if not schemma or ext != ".csv":
                print(f"{name} não mapeado no map de schemmas")
                continue


            df = pd.read_csv(input_path)

            try:
                #faz o tratamento esperado de acordo com o schemma
                df_enforce = self._normalize_data(df,schemma,name)
                self.df_silver[name] = df_enforce
                print(f"Arquivo {file} normalizado e salvo como {name}")

            except Exception:
                print(f"Não foi possível converter o arquivo {file}")
            
        return self.df_silver,self.errors

    def _normalize_data(self, df: pd.DataFrame, schema: dict, table_name: str)->pd.DataFrame:
        """
        :param df: arquivo csv convertido em dataframe
        :param schema: schema completo dos tipos das colunas
        :param table_name: nome da tabela para armazenar o log de qualidade
        """

        enforcer = self.schema_enforcer(
            df=df,
            schema=schema,
            table_name=table_name,
            errros_list=self.errors
        )
        return enforcer.run()


