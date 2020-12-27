# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import re
import sqlite3
import tkinter as tk
import tkinter.ttk as tkk
from tkinter import messagebox


class ConectarBD:
    # construtor
    def __init__(self):
        self.con = sqlite3.connect('db.crudPython')
        self.cur = self.con.cursor()
        self.criarTabela()

    # metodo para criar tabela
    def criarTabela(self):
        try:
            self.cur.execute('''CREATE TABLE IF NOT EXISTS cartas(
            n_documento TEXT,
            assunto TEXT,
            data TEXT)''')
        except Exception as ex:
            print('[x] Falha ao criar a tabela: %s [x]' % ex)
        else:
            print('\n[!] Tabela criada com sucesso [!]\n')

    # metodo para inserir dados
    def insertData(self, ndocumento, assunto, data):

        try:
            self.cur.execute('''INSERT INTO cartas VALUES (?,?,?)''', (ndocumento, assunto, data))
        except Exception as ex:
            print('\n[x] Falha ao inserir registo [x]\n')
            print('[x] Revertendo operação (rollback) %s [x]\n' % ex)
        else:
            self.con.commit()
            print('\n[!] Registo inserido com sucesso [!]\n')

        # metodo para inserir dados

    def updateData(self, ndocumento, assunto, data, rowid):

        try:
            self.cur.execute('''UPDATE cartas SET n_documento=?,assunto=?,data=? WHERE rowid=?''',
                             (ndocumento, assunto, data, rowid))
        except Exception as ex:
            print('\n[x] Falha ao actualizar registo [x]\n')
            print('[x] Revertendo operação (rollback) %s [x]\n' % ex)
        else:
            self.con.commit()
            print('\n[!] Registo actualizado com sucesso [!]\n')

    # consultar dados na bd
    def consultarRegistos(self):
        return self.cur.execute('SELECT rowid, * FROM cartas').fetchall()

    # consultar o ultimo id
    def consultarUltimoId(self):
        return self.cur.execute('SELECT MAX(rowid) FROM cartas').fetchone()

    # consultar informacoes baseando no id
    def consultarPeloId(self, rowid):
        return self.cur.execute('SELECT * FROM cartas WHERE rowid=?', (rowid)).fetchone()

    # remover um registo da bd
    def removerRegisto(self, rowid):
        try:
            self.cur.execute("DELETE FROM cartas WHERE rowid=?", (rowid))
        except Exception as ex:
            print('\n[x] Falha ao excluir registo [x]\n')
            print('[x] Revertendo operação (rollback) %s [x]\n' % ex)
        else:
            self.con.commit()
            print('\n[!] Registo excluído com sucesso [!]\n')


# interface grafica
class Janela(tk.Frame):
    """Janela Principal"""

    # contrutor
    def __init__(self, master=None):
        """Construtor"""
        super().__init__(master)
        # colectando informacoes do monitor
        largura = round(self.winfo_screenwidth() / 2)
        altura = round(self.winfo_screenheight() / 2)
        tamanho = ('%sx%s' % (largura, altura))

        # Titulo da Janela principal
        master.title('CRUD com SQLite + Tkinter')

        # tamanho da janela principal
        master.geometry(tamanho)

        # instanciando a conexao com a BD
        self.banco = ConectarBD()

        # gerenciador de layout da janela principal
        self.pack()

        # criando os widgets(elementos, como botao) da interface
        self.criarWidgets()

    # metodo para criar os elementos que pertencem a janela principal
    def criarWidgets(self):
        # containers
        frame1 = tk.Frame(self)
        frame1.pack(side=tk.TOP, fill=tk.BOTH, padx=5, pady=5)

        frame2 = tk.Frame(self)
        frame2.pack(fill=tk.BOTH, expand=True)

        frame3 = tk.Frame(self)
        frame3.pack(side=tk.BOTTOM, padx=5)

        # Labels.
        labelDocumento = tk.Label(frame1, text='Nº Documento')
        labelDocumento.grid(row=0, column=0)

        labelAssunto = tk.Label(frame1, text='Assunto')
        labelAssunto.grid(row=0, column=1)

        labelRecebido = tk.Label(frame1, text='Data recebimento')
        labelRecebido.grid(row=0, column=2)

        # Caixas de Texto
        self.entryDocumento = tk.Entry(frame1)
        self.entryDocumento.grid(row=1, column=0)

        self.entryAssunto = tk.Entry(frame1)
        self.entryAssunto.grid(row=1, column=1, padx=10)

        self.entryData = tk.Entry(frame1)
        self.entryData.grid(row=1, column=2)

        # Botao para adicionar um novo registo
        btnAdicionar = tk.Button(frame1, text='Adicionar', bg='blue', fg='white')
        # metodo que é chamado quando clico no botão
        btnAdicionar['command'] = self.addRegisto
        btnAdicionar.grid(row=0, column=3, rowspan=2, padx=50)

        # botao para limpar os campos
        btnLimpar = tk.Button(frame1, text='Limpar', bg='green', fg='white')
        btnLimpar['command'] = self.limparCampos
        btnLimpar.grid(row=0, column=4, rowspan=2, padx=10)

        # TreeView
        self.treeView = tkk.Treeview(frame2, columns=('Nº Documento', 'Assunto', 'Data'))
        self.treeView.heading('#0', text='ROWID')
        self.treeView.heading('#1', text='Nº Documento')
        self.treeView.heading('#2', text='Assunto')
        self.treeView.heading('#3', text='Data')

        # inserindo os dados do bd no treview.
        for row in self.banco.consultarRegistos():
            self.treeView.insert('', 'end', text=row[0], values=(row[1], row[2], row[3]))

        self.treeView.pack(fill=tk.BOTH, expand=True)

        # Botao para remover um item
        btnExcluir = tk.Button(frame3, text="Excluir", bg='red', fg='white')
        # metodo que é chamado quando clico no botão
        btnExcluir['command'] = self.excluirRegisto
        btnExcluir.pack(pady=10)

    # metodo quando clica no botao add
    def addRegisto(self):
        # colectando os valores
        documento = self.entryDocumento.get()
        assunto = self.entryAssunto.get()
        data = self.entryData.get()

        # validacao simples (utilizar datetime deve ser melhor para validar).
        validarData = re.search(r'(..)/(..)/(....)', data)

        # se a data digitada pasaar na validacao
        if validarData:
            # dados digitados sao inseridos na bd
            self.banco.insertData(ndocumento=documento, assunto=assunto, data=data)

            # colectando a ultima rowid no treeview.
            rowid = self.banco.consultarUltimoId()[0]

            # adicionando os novos dados no treeview
            self.treeView.insert('', 'end', text=rowid, values=(documento, assunto, data))
        else:
            # caso a data não passe na validação é exibido um alerta.
            messagebox.showerror('Erro', 'Padrão de data incorrecto, utilize dd/mm/aaaa')

    # metodo quando clica no botao add
    def excluirRegisto(self):
        # verficando se algum item está selecionado.
        if not self.treeView.focus():
            messagebox.showerror('Erro', 'Nenhum item foi selecionado')
        else:
            # colectando qual item está selecionado.
            itemSelecionado = self.treeView.focus()

            # colectando os dados do item selecionado (dicionário).
            rowid = self.treeView.item(itemSelecionado)

            # Removendo o item com base no valor do rowid(argumento text do treeview).
            # Removendo valor da tabela.
            self.banco.removerRegisto(rowid['text'])

            # Removendo valor do treeview .
            self.treeView.delete(itemSelecionado)

    # limpar campos
    def limparCampos(self):
        self.entryDocumento.delete(0, 'end')
        self.entryAssunto.delete(0, 'end')
        self.entryData.delete(0, 'end')

    # actualizar dados quando clica no botao actualizar
    def upadateRegisto(self):
        # colectando os valores
        documento = self.entryDocumento.get()
        assunto = self.entryAssunto.get()
        data = self.entryData.get()

        # validacao simples (utilizar datetime deve ser melhor para validar).
        validarData = re.search(r'(..)/(..)/(....)', data)

        # se a data digitada pasaar na validacao
        if validarData:
            # colectando qual item está selecionado.
            itemSelecionado = self.treeView.focus()

            # colectando os dados do item selecionado (dicionário).
            rowid = self.treeView.item(itemSelecionado)

            # dados digitados sao inseridos na bd
            self.banco.updateData(ndocumento=documento, assunto=assunto, data=data, rowid=rowid)

            # colectando a ultima rowid no treeview.
            rowid = self.banco.consultarUltimoId()[0]

            # adicionando os novos dados no treeview
            self.treeView.insert('', 'end', text=rowid, values=(documento, assunto, data))
        else:
            # caso a data não passe na validação é exibido um alerta.
            messagebox.showerror('Erro', 'Padrão de data incorrecto, utilize dd/mm/aaaa')

    # trazer dados quando clica na tabela
    def mostrarDadosLinhaTabela(self, event):
        # colectando qual item está selecionado.
        item = self.treeView.selection()

        for i in item:
            # colectando os dados do item selecionado (dicionário).
            print("vc clicou em", self.treeView.item(i, "values")[0])


root = tk.Tk()
app = Janela(master=root)
# clicar na treeview
app.treeView.bind("<Double-1>", app.mostrarDadosLinhaTabela)
app.mainloop()
