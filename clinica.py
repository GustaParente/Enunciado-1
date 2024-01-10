import sqlite3
from datetime import datetime

# Classe Paciente com os atributos paciente_id, nome e telefone
class Paciente:
    def __init__(self, paciente_id, nome, telefone):
        self.paciente_id = paciente_id
        self.nome = nome
        self.telefone = telefone

# Classe Consulta com os atributos consulta_id, paciente_id, dia, hora e especialidade
class Consulta:
    def __init__(self, consulta_id, paciente_id, dia, hora, especialidade):
        self.consulta_id = consulta_id
        self.paciente_id = paciente_id
        self.dia = dia
        self.hora = hora
        self.especialidade = especialidade

# Classe SistemaClinica com seus atributos e fazendo a conexão com o banco de dados
class SistemaClinica:
    def __init__(self, db_path="clinica.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.criar_tabelas()
        self.pacientes_cadastrados = self.carregar_pacientes()
        self.agendamentos = self.carregar_agendamentos()

    # Criação das tabelas no banco de dados
    def criar_tabelas(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS pacientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    telefone TEXT NOT NULL UNIQUE
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS consultas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paciente_id INTEGER NOT NULL,
                    dia TEXT NOT NULL,
                    hora TEXT NOT NULL,
                    especialidade TEXT NOT NULL,
                    FOREIGN KEY (paciente_id) REFERENCES pacientes (id)
                )
            ''')
    # Cadastro dos pacientes
    def cadastrar_paciente(self, nome, telefone):
        with self.conn:
            try:
                self.conn.execute("INSERT INTO pacientes (nome, telefone) VALUES (?, ?)", (nome, telefone))
                paciente_id = self.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                paciente = Paciente(paciente_id, nome, telefone)
                self.pacientes_cadastrados.append(paciente)
                print()
                print("Paciente cadastrado com sucesso.")
                print()
            except sqlite3.IntegrityError:
                print()
                print("Já existe um paciente cadastrado com esse número de telefone.")
                print()

    def carregar_pacientes(self):
        with self.conn:
            cursor = self.conn.execute("SELECT id, nome, telefone FROM pacientes")
            return [Paciente(*row) for row in cursor.fetchall()]

    def listar_pacientes(self):
        print()
        print("Lista de Pacientes:")
        print()
        for i, paciente in enumerate(self.pacientes_cadastrados, 1):
            print(f"{i}. {paciente.nome} - Telefone: {paciente.telefone}")
            print()

    def marcar_consulta(self):
        if not self.pacientes_cadastrados:
            print()
            print("Não há pacientes cadastrados...")
            print()
            return

        self.listar_pacientes()

        try:
            print()
            escolha = int(input("Escolha o número do paciente para marcar a consulta: "))
            print()
            paciente = self.pacientes_cadastrados[escolha - 1]

            dia = input("Digite o DIA da consulta: ")
            mes = input("Digite o MÊS da consulta: ")
            ano = input("Digite o ANO da consulta: ")
            hora = input("Digite o HORÁRIO da consulta (formato HH:MM): ")
            print()

            # Verifica se já existe uma consulta marcada para o mesmo dia e horário
            for consulta in self.agendamentos:
                if consulta.dia == f"{dia}-{mes}-{ano}" and consulta.hora == hora:
                    print()
                    print("Já existe uma consulta marcada para esse dia e horário.")
                    print()
                    return

            # Verifica se a data da consulta é uma data futura
            data_consulta = datetime.strptime(f"{dia}-{mes}-{ano} {hora}", "%d-%m-%Y %H:%M")
            data_atual = datetime.now()
            if data_consulta <= data_atual:
                print()
                print("A consulta deve ser marcada para uma data futura.")
                print()
                return

            especialidade = input("Digite a especialidade da consulta: ")
            print()

            with self.conn:
                self.conn.execute("INSERT INTO consultas (paciente_id, dia, hora, especialidade) VALUES (?, ?, ?, ?)",
                                  (paciente.paciente_id, f"{dia}-{mes}-{ano}", hora, especialidade))
                consulta_id = self.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                consulta = Consulta(consulta_id, paciente.paciente_id, f"{dia}-{mes}-{ano}", hora, especialidade)
                self.agendamentos.append(consulta)
                print()
                print("Consulta marcada com sucesso.")
                print()
        except (ValueError, IndexError):
            print("Escolha inválida. Tente novamente.")
            print()

    # Carrega os agendamentos do banco de dados
    def carregar_agendamentos(self):
        with self.conn:
            cursor = self.conn.execute("SELECT id, paciente_id, dia, hora, especialidade FROM consultas")
            return [Consulta(*row) for row in cursor.fetchall()]

    # Lista os agendamentos
    def listar_agendamentos(self):
        print("Lista de Agendamentos:")
        print()
        for i, consulta in enumerate(self.agendamentos, 1):
            paciente = next((paciente for paciente in self.pacientes_cadastrados if paciente.paciente_id == consulta.paciente_id), None)
            if paciente:
                print(f"{i}. {paciente.nome} - Data: {consulta.dia}, Horário: {consulta.hora}, Especialidade: {consulta.especialidade}")
                print()
                
            else:
                print()
                print(f"{i}. Paciente não encontrado - Dia: {consulta.dia}, Hora: {consulta.hora}, Especialidade: {consulta.especialidade}")

    # Função para cancelar a consulta
    def cancelar_consulta(self):
        if not self.agendamentos:
            print()
            print("Não há consultas agendadas.")
            print()
            return

        self.listar_agendamentos()

        try:
            print()
            escolha = int(input("Escolha o número do agendamento para cancelar: "))
            print()
            consulta = self.agendamentos[escolha - 1]

            paciente = next((paciente for paciente in self.pacientes_cadastrados if paciente.paciente_id == consulta.paciente_id), None)

            if paciente:
                print()
                print(f"Consulta agendada para {paciente.nome} - Data: {consulta.dia}, Horário: {consulta.hora}, Especialidade: {consulta.especialidade}")
                print()
                confirmacao = input("Deseja cancelar esta consulta? (s/n): ")
                print()

                if confirmacao.lower() == "s":
                    with self.conn:
                        self.conn.execute("DELETE FROM consultas WHERE id=?", (consulta.consulta_id,))
                    self.agendamentos.remove(consulta)
                    print()
                    print("Consulta cancelada com sucesso.")
                    print()
            else:
                print()
                print(f"Paciente não encontrado para a consulta.")
                print()
        except (ValueError, IndexError):
            print()
            print("Escolha inválida. Tente novamente.")
            print()

    # Função para fechar a conexão com o banco de dados
    def fechar_conexao(self):
        self.conn.close()

# Função principal que inicia o sistema como um todo
if __name__ == "__main__":
    sistema = SistemaClinica()

    # Loop para o menu
    while True:
        print("\nMenu:")
        print()
        print("1. Cadastrar Paciente")
        print("2. Marcar Consulta")
        print("3. Cancelar Consulta")
        print("4. Listar Pacientes")
        print("5. Listar Consultas Agendadas")
        print("6. Sair")
        print()

        opcao = input("Escolha uma opção: ")
        print()

        if opcao == "1":
            nome = input("Digite o nome do paciente: ")
            print()
            telefone = input("Digite o telefone do paciente: ")
            print()
            sistema.cadastrar_paciente(nome, telefone)

        elif opcao == "2":
            sistema.marcar_consulta()

        elif opcao == "3":
            sistema.cancelar_consulta()

        elif opcao == "4":
            sistema.listar_pacientes()

        elif opcao == "5":
            sistema.listar_agendamentos()

        elif opcao == "6":
            print("Saindo do programa.")
            sistema.fechar_conexao()
            break

        else:
            print()
            print("Opção inválida. Tente novamente.")
            print()
