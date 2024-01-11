# Importação das bibliotecas necessárias
import sqlite3
from datetime import datetime

# Definição das 3 classes que usaremos no sistema
class Paciente:
    def __init__(self, paciente_id, nome, telefone):
        self.paciente_id = paciente_id
        self.nome = nome
        self.telefone = telefone

class Consulta:
    def __init__(self, consulta_id, paciente_id, dia, hora, especialidade):
        self.consulta_id = consulta_id
        self.paciente_id = paciente_id
        self.dia = dia
        self.hora = hora
        self.especialidade = especialidade

class SistemaClinica:
    def __init__(self, db_path="clinica.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.criar_tabelas()
        self.carregar_dados()

    # Método para criar as tabelas no banco de dados
    def criar_tabelas(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS paciente (
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
                    FOREIGN KEY (paciente_id) REFERENCES paciente (id)
                )
            ''')

    # Método para cadastrar um novo paciente
    def cadastrar_paciente(self, nome, telefone):
        with self.conn:
            try:
                self.conn.execute("INSERT INTO paciente (nome, telefone) VALUES (?, ?)", (nome, telefone))
                paciente_id = self.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                paciente = Paciente(paciente_id, nome, telefone)
                self.pacientes_cadastrados.append(paciente)
                print("Paciente cadastrado com sucesso.")
            except sqlite3.IntegrityError:
                print("ERRO! Telefone já cadastrado no sistema.")

    # Método para carregar os dados do banco de dados
    def carregar_dados(self):
        self.pacientes_cadastrados = self.carregar_pacientes()
        self.agendamentos = self.carregar_agendamentos()

    # Método para carregar os pacientes cadastrados no banco de dados
    def carregar_pacientes(self):
        with self.conn:
            cursor = self.conn.execute("SELECT id, nome, telefone FROM paciente")
            return [Paciente(*row) for row in cursor.fetchall()]

    # Método para listar os pacientes cadastrados
    def listar_pacientes(self):
        print("\nLista de Pacientes:")
        for i, paciente in enumerate(self.pacientes_cadastrados, 1):
            print(f"{i}. {paciente.nome} - Telefone: {paciente.telefone}")

    # Método para marcar uma consulta
    def marcar_consulta(self):
        if not self.pacientes_cadastrados:
            print("\nNão há pacientes cadastrados...")
            return

        self.listar_pacientes()

        try:
            escolha = int(input("\nEscolha o número do paciente para marcar a consulta: "))
            paciente = self.pacientes_cadastrados[escolha - 1]

            dia, mes, ano = map(int, input("Digite a data da consulta (DD MM AAAA): ").split())
            hora = input("Digite o horário da consulta (formato HH:MM): ")

            for consulta in self.agendamentos:
                if consulta.dia == f"{dia:02d}-{mes:02d}-{ano}" and consulta.hora == hora:
                    print("\nJá existe uma consulta marcada para esse dia e horário.")
                    return

            data_consulta = datetime(ano, mes, dia, *map(int, hora.split(":")))
            data_atual = datetime.now()

            if data_consulta <= data_atual:
                print("\nA consulta deve ser marcada para uma data futura.")
                return

            especialidade = input("Digite a especialidade da consulta: ")

            with self.conn:
                self.conn.execute("INSERT INTO consultas (paciente_id, dia, hora, especialidade) VALUES (?, ?, ?, ?)",
                                  (paciente.paciente_id, f"{dia:02d}-{mes:02d}-{ano}", hora, especialidade))
                consulta_id = self.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                consulta = Consulta(consulta_id, paciente.paciente_id, f"{dia:02d}-{mes:02d}-{ano}", hora, especialidade)
                self.agendamentos.append(consulta)
                print("\nConsulta marcada com sucesso.")
        except (ValueError, IndexError):
            print("\nEscolha inválida. Tente novamente.")

    # Método para carregar os agendamentos do banco de dados
    def carregar_agendamentos(self):
        with self.conn:
            cursor = self.conn.execute("SELECT id, paciente_id, dia, hora, especialidade FROM consultas")
            return [Consulta(*row) for row in cursor.fetchall()]

    # Método para listar os agendamentos
    def listar_agendamentos(self):
        print("\nLista de Agendamentos:")
        for i, consulta in enumerate(self.agendamentos, 1):
            paciente = next((paciente for paciente in self.pacientes_cadastrados if paciente.paciente_id == consulta.paciente_id), None)
            if paciente:
                print(f"{i}. {paciente.nome} - Data: {consulta.dia}, Horário: {consulta.hora}, Especialidade: {consulta.especialidade}")
            else:
                print(f"{i}. Paciente não encontrado - Dia: {consulta.dia}, Hora: {consulta.hora}, Especialidade: {consulta.especialidade}")

    # Método para cancelar uma consulta
    def cancelar_consulta(self):
        if not self.agendamentos:
            print("\nNão há consultas agendadas.")
            return

        self.listar_agendamentos()

        try:
            escolha = int(input("\nEscolha o número do agendamento para cancelar: "))
            consulta = self.agendamentos[escolha - 1]

            paciente = next((paciente for paciente in self.pacientes_cadastrados if paciente.paciente_id == consulta.paciente_id), None)

            if paciente:
                print(f"\nConsulta agendada para {paciente.nome} - Data: {consulta.dia}, Horário: {consulta.hora}, Especialidade: {consulta.especialidade}")
                confirmacao = input("Deseja cancelar esta consulta? (s/n): ")

                if confirmacao.lower() == "s":
                    with self.conn:
                        self.conn.execute("DELETE FROM consultas WHERE id=?", (consulta.consulta_id,))
                    self.agendamentos.remove(consulta)
                    print("\nConsulta cancelada com sucesso.")
            else:
                print(f"\nPaciente não encontrado para a consulta.")
        except (ValueError, IndexError):
            print("\nEscolha inválida. Tente novamente.")

    # Método para fechar a conexão com o banco de dados
    def fechar_conexao(self):
        self.conn.close()

# Execução do programa
if __name__ == "__main__":
    sistema = SistemaClinica()

    # Loop para o menu
    while True:
        print("\nMenu:")
        print("1. Cadastrar Paciente")
        print("2. Marcar Consulta")
        print("3. Cancelar Consulta")
        print("4. Listar Pacientes")
        print("5. Listar Consultas Agendadas")
        print("6. Sair")

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            nome = input("Digite o nome do paciente: ")
            telefone = input("Digite o telefone do paciente: ")
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
            print("\nOpção inválida. Tente novamente.")
