import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QLineEdit, QPushButton, QLabel, QFileDialog, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from input_fazenda import adicionar_nome_id, processar_planilha
from input_polo import obter_ids_nomes
from input_talhao import  att_bd_agro, consultar_estagio
from shapefile import converter_shp_para_geojson, cruza_shp_planilha_perimetro,cruza_shp_planilha_bd
import os

class App(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ATIVOS")
        self.setGeometry(200, 200, 400, 600)
        
        # Definir uma fonte simples e moderna
        self.setFont(QFont("Helvetica", 10))

        # Layout principal
        self.layout = QVBoxLayout()

        # Layout para os botões no canto superior direito
        top_layout = QHBoxLayout()
        
        # Botão "Seleciona Planilha Fazenda"
        self.selecionar_button = QPushButton("Selecionar Diretório")
        self.selecionar_button.setStyleSheet(""" 
            background-color: #002060; 
            color: white; 
            padding: 10px 20px; 
            font-size: 12px; 
            font-weight: bold; 
            border-radius: 6px;
        """)
        self.selecionar_button.clicked.connect(self.selecionar_diretorio)
        
        # Spacer para empurrar os botões para a direita
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        top_layout.addItem(spacer)
        top_layout.addWidget(self.selecionar_button)
        
        # Adicionar o layout do topo no layout principal
        self.layout.addLayout(top_layout)

        # Lista para mostrar IDs e Nomes
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("background-color: #f5f5f5; border: none; padding: 8px;")
        self.layout.addWidget(QLabel("IDs e Nomes:"), alignment=Qt.AlignLeft)
        self.layout.addWidget(self.list_widget)

        # Atualizar a lista
        self.atualizar_lista()

        # Layout para campos de entrada
        input_layout = QHBoxLayout()

        # Campo para cliente_id
        self.cliente_id_input = QLineEdit()
        self.cliente_id_input.setPlaceholderText("Novo Cliente ID")
        self.cliente_id_input.setStyleSheet("padding: 6px; border: 1px solid #ddd; border-radius: 4px;")
        input_layout.addWidget(self.cliente_id_input)

        # Campo para nome
        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Novo Nome")
        self.nome_input.setStyleSheet("padding: 6px; border: 1px solid #ddd; border-radius: 4px;")
        input_layout.addWidget(self.nome_input)

        # Botão para adicionar
        self.adicionar_button = QPushButton("Adicionar")
        self.adicionar_button.setStyleSheet(""" 
            background-color: #002060; 
            color: white; 
            padding: 10px 20px; 
            font-size: 12px; 
            font-weight: bold; 
            border-radius: 6px;
        """)
        self.adicionar_button.clicked.connect(self.adicionar_nome_id)
        input_layout.addWidget(self.adicionar_button)

        self.layout.addLayout(input_layout)

 # Botão para processar SHAPEFILE
        self.processar_button3 = QPushButton("Atualizar Shapefile")
        self.processar_button3.setStyleSheet(""" 
            background-color: #002060; 
            color: white; 
            padding: 10px 20px; 
            font-size: 12px; 
            font-weight: bold; 
            border-radius: 6px;
        """)
        self.processar_button3.clicked.connect(self.shp_para_geojason) #LEMBRAR DE DAR UM JEITO NESSA ENTRADA E SAIDA
        self.layout.addWidget(self.processar_button3)

        # Botão para processar planilhas
        self.processar_button = QPushButton("Atualizar Perimetro")
        self.processar_button.setStyleSheet(""" 
            background-color: #002060; 
            color: white; 
            padding: 10px 20px; 
            font-size: 12px; 
            font-weight: bold; 
            border-radius: 6px;
        """)
        self.processar_button.clicked.connect(self.processar_planilha)
        
        
        self.layout.addWidget(self.processar_button)

 # Botão para processar SHAPEFILE
        self.processar_button2 = QPushButton("Atualizar Talhao")
        self.processar_button2.setStyleSheet(""" 
            background-color: #002060; 
            color: white; 
            padding: 10px 20px; 
            font-size: 12px; 
            font-weight: bold; 
            border-radius: 6px;
        """)
        self.processar_button2.clicked.connect(self.att_bd) #LEMBRAR DE DAR UM JEITO NESSA ENTRADA E SAIDA
        self.layout.addWidget(self.processar_button2)


        # Label de status
        self.status_label = QLabel('')
        self.status_label.setStyleSheet("color: #FF5722; font-weight: bold;")
        self.layout.addWidget(self.status_label)

        self.setLayout(self.layout)

        self.banco_bd = None
        self.caminho_diretorio = None
        self.banco_fazenda = None
        self.caminho_planilha = None  # Inicializar o caminho da planilha como None

    def atualizar_lista(self):
        """Atualizar a lista de IDs e nomes a partir do banco de dados."""
        self.list_widget.clear()
        ids_nomes = obter_ids_nomes()
        for cliente_id, nome in ids_nomes:
            self.list_widget.addItem(f"{cliente_id} - {nome}")

    def adicionar_nome_id(self):
        """Adicionar novo cliente_id e nome ao banco."""
        cliente_id = self.cliente_id_input.text()
        nome = self.nome_input.text()
        
        if cliente_id and nome:
            adicionar_nome_id(cliente_id, nome)
            self.atualizar_lista()
            self.cliente_id_input.clear()
            self.nome_input.clear()

    def selecionar_diretorio(self):
        """Abrir um diálogo para selecionar um diretório."""
        caminho = QFileDialog.getExistingDirectory(self, "Selecionar Diretório", "")
        if caminho:
            self.caminho_diretorio = caminho
         # Exibe o caminho do diretório selecionado em um campo de texto, se houver um
            #self.campo_caminho.setText(caminho)  # substitua 'campo_caminho' pelo nome do seu campo

    def shp_para_geojason(self):
        pasta_entrada = self.caminho_diretorio +'/shp'
        pasta_saida = self.caminho_diretorio +'/planilhas'
        converter_shp_para_geojson(pasta_entrada, pasta_saida)
        cruza_shp_planilha_perimetro(pasta_saida)
        #cruza_shp_planilha_bd(pasta_saida)


    def processar_planilha(self):
        for planilha in os.listdir(self.caminho_diretorio +'/planilhas'):
            if planilha.startswith('FAZENDA'):
                self.banco_fazenda = self.caminho_diretorio+'/planilhas/'+planilha
        if self.banco_fazenda:
            resultado = processar_planilha(self.banco_fazenda)
            self.status_label.setText(resultado)
        else:
            self.status_label.setText("Selecione uma planilha fazenda ou bd_agro.")


    def att_bd(self):
        for planilha in os.listdir(self.caminho_diretorio +'/planilhas'):
            if planilha.startswith('BD_AGRO'):
                self.banco_bd = self.caminho_diretorio+'/planilhas/'+planilha
                self.banco_bd_saida = self.caminho_diretorio+'/planilhas/'
        if self.banco_bd:
            resultado2 = att_bd_agro(self.banco_bd, self.banco_bd_saida)
            self.status_label.setText(resultado2)
        else:
            self.status_label.setText("Selecione uma planilha fazenda ou bd_agro.")
         
if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = App()
    janela.show()
    sys.exit(app.exec_())
