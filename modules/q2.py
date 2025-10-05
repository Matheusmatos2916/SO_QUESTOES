import threading
import time
import random

# Recursos compartilhados
compilador = threading.Semaphore(1)  # Apenas 1 programador pode usar o compilador
banco_dados = threading.Semaphore(2)  # Máximo 2 programadores no banco de dados


def programador(id):
    """
    Simula um programador que precisa de acesso exclusivo ao compilador
    e acesso compartilhado ao banco de dados (máximo 2 simultâneos).
    Os recursos são independentes - programadores podem acessar o banco
    mesmo quando o compilador estiver ocupado.
    """
    while True:
        print(f"[Programador {id}] Quer compilar - aguardando recursos...")
        
        # Pega acesso ao banco de dados (acesso compartilhado, max 2)
        with banco_dados:
            print(f"[Programador {id}] ✅ Acessando banco de dados (compartilhado)")
            
            # Agora pega o compilador (acesso exclusivo)
            with compilador:
                print(f"[Programador {id}] ✅ Pegou o compilador (acesso exclusivo)")
                print(f"[Programador {id}] 🔄 Compilando módulo...")
                
                # Simula tempo de compilação
                tempo_compilacao = random.uniform(0.5, 1.5)
                time.sleep(tempo_compilacao)
                
                print(f"[Programador {id}] ✅ Compilação concluída!")
            
            print(f"[Programador {id}] 🔓 Liberou compilador")
        
        print(f"[Programador {id}] 🔓 Liberou banco de dados")
        
        # Simula tempo de descanso/pensamento antes da próxima compilação
        tempo_descanso = random.uniform(1, 3)
        print(f"[Programador {id}] 😴 Descansando por {tempo_descanso:.1f}s...")
        time.sleep(tempo_descanso)


def q2():
    """
    Executa a simulação da Questão 2:
    - 5 programadores
    - 1 compilador (acesso exclusivo)
    - 1 banco de dados (máximo 2 programadores simultâneos)
    - Recursos independentes: banco de dados pode ser acessado mesmo com compilador ocupado
    - Execução em loop infinito para apresentação
    """
    print("=== Questão 2: Laboratório de Programadores ===")
    print("Recursos:")
    print("- 1 Compilador (acesso exclusivo)")
    print("- 1 Banco de dados (máximo 2 programadores simultâneos)")
    print("- 5 Programadores trabalhando")
    print("- Recursos independentes: banco pode ser acessado mesmo com compilador ocupado")
    print("\nIniciando simulação...\n")
    
    threads = []
    
    # Cria e inicia 5 programadores
    for i in range(5):
        programador_id = i + 1
        t = threading.Thread(
            target=programador, 
            args=(programador_id,),
            name=f"Programador-{programador_id}"
        )
        t.daemon = True 
        t.start()
        threads.append(t)
    
    try:
        # Loop infinito para apresentação em sala
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nSimulação interrompida pelo usuário.")
        print("=== Fim da simulação ===")
