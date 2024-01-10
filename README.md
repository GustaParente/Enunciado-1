Enunciado 1 - Exercício de Programação - 2023/2

Essa aplicação funciona como um sistema de cadastro de uma clínica médica, rodando exclusivamente no terminal. Entre as funcionalidades desse sistema estão o cadastro de pacientes, marcação de consultas, cancelamento de consultas, verificação da lista de pacientes
cadastrados no sistema e verificação da lista de consultas marcadas.

Para esse projeto, optei por utilizar a linguagem Python, pois, como o enunciado pediu, o sistema realmente roda no terminal de forma bem simples, o que é facilmente feito através do Python. Os erros foram tratados de forma adequada, ou seja, não é possível registrar 
mais de um paciente com o mesmo número de telefone, não é possível marcar uma consulta para uma data que já passou, além de não ser possível marcar mais de uma consulta para o mesmo dia e horário.

Como tarefa extra, o enunciado "pediu" para criarmos uma forma dessas informações ficarem salvas mesmo após o usuário sair do sistema. Por isso, utilizando a biblioteca sqlite3 do Python, eu implementei a funcionalidade do sistema criar um banco de dados simples 
localmente para armazenar as informações que estão sendo inseridas pelo sistema, o sistema cria esse banco de dados automaticamente na primeira vez em que o usuário executa o código.

TUTORIAL:
- Faça o download do código aqui pelo GitHub;
- Extraia a pasta em um local escolhido;
- Abra o código em uma IDE de sua escolha;
- Execute o código e o sistema abrirá no terminal da IDE;
- Pronto!
