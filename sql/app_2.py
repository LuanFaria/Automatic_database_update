import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QLineEdit, QPushButton, QLabel, QFileDialog, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from input_fazenda import adicionar_nome_id, processar_planilha
from input_polo import obter_ids_nomes
from input_talhao import att_bd_agro, consultar_estagio, remover_linhas_sem_geometria, cruza_planilhas, insere_talhao
from shapefile import converter_shp_para_geojson, cruza_shp_planilha_perimetro, cruza_shp_planilha_bd, talhao_fazenda
import os

class ProcessingThread(QThread):
    status = pyqtSignal(str)

    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args

    def run(self):
        try:
            result = self.func(*self.args)
            self.status.emit(result if result else "Processamento concluído com sucesso!")
        except Exception as e:
            self.status.emit(f"Erro: {str(e)}")

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ATIVOS")
        self.setGeometry(200, 200, 400, 600)
        self.setFont(QFont("Helvetica", 10))

        self.layout = QVBoxLayout()
        top_layout = QHBoxLayout()

        # Botão Selecionar Diretório
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
        
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        top_layout.addItem(spacer)
        top_layout.addWidget(self.selecionar_button)
        self.layout.addLayout(top_layout)

        # Lista de IDs e Nomes
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("background-color: #f5f5f5; border: none; padding: 8px;")
        self.layout.addWidget(QLabel("IDs e Nomes:"), alignment=Qt.AlignLeft)
        self.layout.addWidget(self.list_widget)
        self.atualizar_lista()
        
        # Layout para Entrada
        input_layout = QHBoxLayout()
        self.cliente_id_input = QLineEdit()
        self.cliente_id_input.setPlaceholderText("Novo Cliente ID")
        self.cliente_id_input.setStyleSheet("padding: 6px; border: 1px solid #ddd; border-radius: 4px;")
        input_layout.addWidget(self.cliente_id_input)
        
        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Novo Nome")
        self.nome_input.setStyleSheet("padding: 6px; border: 1px solid #ddd; border-radius: 4px;")
        input_layout.addWidget(self.nome_input)
        
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

        # Botão para Atualizar Shapefile
        self.processar_button3 = QPushButton("Atualizar Shapefile")
        self.processar_button3.setStyleSheet("""
            background-color: #002060; 
            color: white; 
            padding: 10px 20px; 
            font-size: 12px; 
            font-weight: bold; 
            border-radius: 6px;
        """)
        self.processar_button3.clicked.connect(lambda: self.start_process(self.shp_para_geojason))
        self.layout.addWidget(self.processar_button3)

        # Botão para Atualizar Perímetro
        self.processar_button = QPushButton("Atualizar Perímetro")
        self.processar_button.setStyleSheet("""
            background-color: #002060; 
            color: white; 
            padding: 10px 20px; 
            font-size: 12px; 
            font-weight: bold; 
            border-radius: 6px;
        """)
        self.processar_button.clicked.connect(lambda: self.start_process(self.processar_planilha))
        self.layout.addWidget(self.processar_button)

        # Botão para Atualizar Talhão
        self.processar_button2 = QPushButton("Atualizar Talhão")
        self.processar_button2.setStyleSheet("""
            background-color: #002060; 
            color: white; 
            padding: 10px 20px; 
            font-size: 12px; 
            font-weight: bold; 
            border-radius: 6px;
        """)
        self.processar_button2.clicked.connect(lambda: self.start_process(self.formatar_bd))
        self.layout.addWidget(self.processar_button2)


        # Label de Status
        self.status_label = QLabel('')
        self.status_label.setStyleSheet("color: #FF5722; font-weight: bold;")
        self.layout.addWidget(self.status_label)
        self.setLayout(self.layout)

        self.banco_bd = None
        self.caminho_diretorio = None
        self.banco_fazenda = None

    def atualizar_lista(self):
        self.list_widget.clear()
        ids_nomes = obter_ids_nomes()
        for cliente_id, nome in ids_nomes:
            self.list_widget.addItem(f"{cliente_id} - {nome}")

    def adicionar_nome_id(self):
        cliente_id = self.cliente_id_input.text()
        nome = self.nome_input.text()
        if cliente_id and nome:
            adicionar_nome_id(cliente_id, nome)
            self.atualizar_lista()
            self.cliente_id_input.clear()
            self.nome_input.clear()

    def selecionar_diretorio(self):
        caminho = QFileDialog.getExistingDirectory(self, "Selecionar Diretório", "")
        if caminho:
            self.caminho_diretorio = caminho

    def start_process(self, func):
        self.status_label.setText("Processando...")
        self.thread = ProcessingThread(func)
        self.thread.status.connect(self.status_label.setText)
        self.thread.start()

    def shp_para_geojason(self):
        pasta_entrada = self.caminho_diretorio + '/shp'
        pasta_saida = self.caminho_diretorio + '/planilhas'
        talhao_fazenda(pasta_entrada) 
        converter_shp_para_geojson(pasta_entrada, pasta_saida)
        cruza_shp_planilha_perimetro(pasta_saida)
        cruza_shp_planilha_bd(pasta_saida)


    def processar_planilha(self):
        for planilha in os.listdir(self.caminho_diretorio + '/planilhas'):
            if planilha.startswith('FAZENDA'):
                self.banco_fazenda = self.caminho_diretorio + '/planilhas/' + planilha
        if self.banco_fazenda:
            return processar_planilha(self.banco_fazenda)
        else:
            return "Selecione uma planilha fazenda ou bd_agro."

    def formatar_bd(self):
        for planilha in os.listdir(self.caminho_diretorio + '/planilhas'):
            if planilha.startswith('TALHAO'): 
                if planilha.endswith('xlsx'):
                    self.banco_bd = self.caminho_diretorio + '/planilhas/' + planilha
            if planilha.startswith('FAZENDA') and planilha.endswith('xlsx'):
                if planilha.endswith('xlsx'):
                    self.banco_fazenda = self.caminho_diretorio + '/planilhas/' + planilha
                    
        if self.banco_bd:
            print((self.banco_bd, self.banco_fazenda))
            remover_linhas_sem_geometria(self.banco_bd)
            cruza_planilhas(self.banco_bd, self.banco_fazenda)
            att_bd_agro(self.banco_bd, self.caminho_diretorio + '/planilhas/')  
            insere_talhao(self.caminho_diretorio + '/planilhas/saida_talhao.xlsx')
            return 
        else:
            return "Selecione uma planilha fazenda ou bd_agro."

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = App()
    janela.show()
    sys.exit(app.exec_())
