import threading
import time
import random
import json

sala_lock = threading.Lock()
estado_sala = "EMPTY"
cachorros = 0
gatos = 0
fila_espera = []


def animal(id, especie, descanso, arrival_time=0):
    global estado_sala, cachorros, gatos, fila_espera
    
    # Aguarda o tempo de chegada
    time.sleep(arrival_time)
    
    with sala_lock:
        # Verifica se pode entrar imediatamente
        pode_entrar = False
        
        if estado_sala == "EMPTY":
            # Sala vazia - qualquer animal pode entrar
            pode_entrar = True
            estado_sala = "DOGS" if especie == "DOG" else "CATS"
        elif estado_sala == "DOGS" and especie == "DOG":
            # Sala de cães - apenas cães podem entrar
            pode_entrar = True
        elif estado_sala == "CATS" and especie == "CAT":
            # Sala de gatos - apenas gatos podem entrar
            pode_entrar = True
        
        if pode_entrar:
            if especie == "DOG":
                cachorros += 1
            else:
                gatos += 1
            print(
                f"{especie} {id} entrou. Estado: {estado_sala} (Dogs={cachorros}, Cats={gatos})"
            )
        else:
            # Não pode entrar - adiciona à fila de espera
            fila_espera.append((id, especie, descanso, arrival_time))
            print(f"{especie} {id} não pode entrar - sala ocupada por {estado_sala}")
            return
    
    # Tempo de descanso
    time.sleep(descanso)
    
    with sala_lock:
        if especie == "DOG":
            cachorros -= 1
        else:
            gatos -= 1
            
        # Se não há mais animais da mesma espécie, sala fica vazia
        if (estado_sala == "DOGS" and cachorros == 0) or (estado_sala == "CATS" and gatos == 0):
            estado_sala = "EMPTY"
            
        print(
            f"{especie} {id} saiu. Estado: {estado_sala} (Dogs={cachorros}, Cats={gatos})"
        )
        
        # Verifica se há animais esperando e pode atender
        if estado_sala == "EMPTY" and fila_espera:
            # Processa animais da fila que podem entrar
            animais_para_remover = []
            for i, (wait_id, wait_especie, wait_descanso, wait_arrival) in enumerate(fila_espera):
                # Primeiro animal da fila pode entrar
                if wait_especie == "DOG":
                    estado_sala = "DOGS"
                    cachorros += 1
                else:
                    estado_sala = "CATS"
                    gatos += 1
                    
                print(f"{wait_especie} {wait_id} entrou da fila. Estado: {estado_sala} (Dogs={cachorros}, Cats={gatos})")
                animais_para_remover.append(i)
                
                # Inicia thread para este animal
                t = threading.Thread(
                    target=animal_saida,
                    args=(wait_id, wait_especie, wait_descanso)
                )
                t.start()
                break  # Apenas um animal entra por vez
            
            # Remove animais processados da fila
            for i in reversed(animais_para_remover):
                fila_espera.pop(i)


def animal_saida(id, especie, descanso):
    """Função auxiliar para gerenciar a saída de animais que entraram da fila"""
    global estado_sala, cachorros, gatos
    
    # Tempo de descanso
    time.sleep(descanso)
    
    with sala_lock:
        if especie == "DOG":
            cachorros -= 1
        else:
            gatos -= 1
            
        # Se não há mais animais da mesma espécie, sala fica vazia
        if (estado_sala == "DOGS" and cachorros == 0) or (estado_sala == "CATS" and gatos == 0):
            estado_sala = "EMPTY"
            
        print(
            f"{especie} {id} saiu. Estado: {estado_sala} (Dogs={cachorros}, Cats={gatos})"
        )
        
        # Verifica se há animais esperando e pode atender
        if estado_sala == "EMPTY" and fila_espera:
            # Processa animais da fila que podem entrar
            animais_para_remover = []
            for i, (wait_id, wait_especie, wait_descanso, wait_arrival) in enumerate(fila_espera):
                # Primeiro animal da fila pode entrar
                if wait_especie == "DOG":
                    estado_sala = "DOGS"
                    cachorros += 1
                else:
                    estado_sala = "CATS"
                    gatos += 1
                    
                print(f"{wait_especie} {wait_id} entrou da fila. Estado: {estado_sala} (Dogs={cachorros}, Cats={gatos})")
                animais_para_remover.append(i)
                
                # Inicia thread para este animal
                t = threading.Thread(
                    target=animal_saida,
                    args=(wait_id, wait_especie, wait_descanso)
                )
                t.start()
                break  # Apenas um animal entra por vez
            
            # Remove animais processados da fila
            for i in reversed(animais_para_remover):
                fila_espera.pop(i)


def process_vet_room_protocol(input_data):
    """
    Processa o protocolo da sala veterinária conforme especificação JSON.
    
    Args:
        input_data (dict): Dicionário contendo a estrutura JSON padronizada
    """
    global estado_sala, cachorros, gatos, fila_espera

    estado_sala = input_data["room"]["initial_sign_state"]
    cachorros = 0
    gatos = 0
    fila_espera = []
    
    print(f"=== Protocolo da Sala Veterinária ===")
    print(f"Versão: {input_data['spec_version']}")
    print(f"ID do desafio: {input_data['challenge_id']}")
    print(f"Estado inicial da sala: {estado_sala}")
    print(f"Política da fila: {input_data['metadata']['queue_policy']}")
    print(f"Latência de mudança de sinal: {input_data['metadata']['sign_change_latency']}")
    print(f"Critérios de desempate: {input_data['metadata']['tie_breaker']}")
    print()
    
    # Processa os animais
    animals = input_data["workload"]["animals"]
    threads = []
    
    for animal_data in animals:
        t = threading.Thread(
            target=animal, 
            args=(
                animal_data["id"], 
                animal_data["species"], 
                animal_data["rest_duration"],
                animal_data["arrival_time"]
            )
        )
        t.start()
        threads.append(t)
    
    # Aguarda todas as threads terminarem
    for t in threads:
        t.join()
    
    print(f"\n=== Protocolo Finalizado ===")
    print(f"Estado final da sala: {estado_sala}")


def q3():
    """
    Executa o protocolo usando a estrutura JSON padronizada conforme a Questão 3.
    """
    input_json = json.load(open('modules/q3_3.json'))

    
    process_vet_room_protocol(input_json)
