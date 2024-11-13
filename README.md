## Bibliotecas:
    import sys
    from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QLineEdit, QPushButton, QLabel, QFileDialog, QSpacerItem, QSizePolicy
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont
    import psycopg2
    import pandas as pd
    import os
~~~

#### EXECUTAR APP_2 (banco genérico criado em localhost)
     REGRAS:
        - O Shapefile FAZENDA precisa ter as colunas "fazenda" e "area_ha";
        - O Shapefile TALHAO precisa ter as colunas "CHAVE" e "area_ha",
        - A planilha FAZENDA precisa ser preenchida a mão (todos os campos - exceto fazenda_id que é gerada no banco e geometria que sera importada do shp )
        - A planilha TALHAO precisa estar no formado BD_AGRO
        - As planilhas devem estar armazenadas na pasta chamada "planilhas"
        - Os shps precisam estar em uma pasta chamada "shp"

~~~

#### SELECIONAR DIRETORIO
    - Diretório na pasta C,
    - Pasta "planilhas" e "shp".

#### ADICIONAR NOVO POLO (input_polo)
    - Conexão com o banco,
    - Colocar o id do cliente,
    - Colocar o nome do  Cliente,
    - Clicar em Adicionar.

#### ATUALIZAR SHAPEFILE
    - Converte arquivo .shp em geojson,
    - Cruza o geojson FAZENDA com a planilha fazenda, e copia a geometria e area_ha (é preciso que tenha a coluna cod_fazenda no excel e no shp),
    - Cruza o geojson TALHAO com o BD_AGRO, e copia a geometria e area_ha (é preciso que tenha a coluna CHAVE, tanto no shp quanto no excel),

#### ATUALIZAR PERIMETRO/FAZENDA
    - Verifica se os dados ja existem no banco,
    - Sobe a planilha FAZENDA para o banco,
    - Preencher fazenda_id na planilha "FAZENDA"

#### ATUALIZAR TALHAO (input_talhao)
    - Trata o BD_AGRO para o formato do banco,
    - Remove Linhas Sem geometria,
    - Adiciona o estagio_id, 

    - Cruza com a planilha fazendo (id = fazenda e cod_fazenda) - Pega as colunas - cliente_id, polo_id e fazenda_id:
    - Verifica se os dados ja existem no banco,:
    - Sobre a planilha talhao.:

#### APP
    - Interface.
    - Interface com apenas 1 botão.:
