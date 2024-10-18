import socket
import os

# Função para carregar a lista de usuários permitidos
def carregar_usuarios(caminho_arquivo):
    with open(caminho_arquivo, 'r') as arquivo:
        return [linha.strip() for linha in arquivo]

# Função principal do servidor
def iniciar_servidor():
    # Definir o endereço e porta do servidor
    SERVER_IP = '127.0.0.1'
    SERVER_PORT = 11550
    # Criar socket e associar ao endereço e porta
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((SERVER_IP, SERVER_PORT))
    # Colocar o servidor em modo de escuta (máximo de 1 cliente por vez)
    server_sock.listen(1)
    print(f"Servidor iniciado em {SERVER_IP}:{SERVER_PORT}. Aguardando conexões...")
    

    # Caminho dos arquivos disponíveis no servidor
    file_directory = 'pta-server/files'
    available_files = os.listdir(file_directory)

    # Carregar os usuários permitidos
    clientes_autorizados = carregar_usuarios('pta-server/users.txt')

    conexao_ativa = False
    # Loop principal
    while True:
        try:
            if not conexao_ativa:
                # Aceitar conexão de um cliente
                cliente_socket, cliente_endereco = server_sock.accept()

            # Receber a mensagem do cliente
            mensagem = cliente_socket.recv(2048).decode().split()

            if conexao_ativa:
                # Comando 'PEGA' para pegar arquivos do servidor
                if mensagem[1] == 'PEGA':
                    nome_arquivo = mensagem[2]
                    if nome_arquivo in available_files:
                        caminho_arquivo = os.path.join(file_directory, nome_arquivo).replace("\\", "/")
                        tamanho_arquivo = os.stat(caminho_arquivo).st_size
                        resposta = f'{mensagem[0]} ARQ {tamanho_arquivo} {tamanho_arquivo}'
                    else:
                        resposta = f'{mensagem[0]} NOK'

                # Comando 'LIST' para listar os arquivos disponíveis
                elif mensagem[1] == 'LIST':
                    try:
                        quantidade_arquivos = len(available_files)
                        lista_arquivos = ','.join(available_files)
                        resposta = f'{mensagem[0]} ARQS {quantidade_arquivos} {lista_arquivos}'
                    except Exception:
                        resposta = f'{mensagem[0]} NOK'

                # Comando 'TERM' para encerrar a conexão
                elif mensagem[1] == 'TERM':
                    resposta = f'{mensagem[0]} OK'
                    conexao_ativa = False

            else:
                # Autenticação inicial: comando 'CUMP' e validação do cliente
                if mensagem[1] == 'CUMP' and mensagem[2] in clientes_autorizados:
                    resposta = f'{mensagem[0]} OK'
                    conexao_ativa = True
                else:
                    resposta = f'{mensagem[0]} NOK'

            # Enviar resposta ao cliente
            cliente_socket.send(resposta.encode('ascii'))

        except KeyboardInterrupt:
            break

    # Finalizar conexão
    cliente_socket.shutdown(socket.SHUT_RDWR)
    cliente_socket.close()

# Iniciar o servidor
iniciar_servidor()
