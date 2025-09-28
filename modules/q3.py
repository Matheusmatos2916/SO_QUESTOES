import threading
import time
import random
import json

sala_lock = threading.Lock()
estado_sala = "EMPTY"
cachorros = 0
gatos = 0


def animal(id, especie, descanso, arrival_time=0):
    global estado_sala, cachorros, gatos
    
    # Aguarda o tempo de chegada
    time.sleep(arrival_time)
    
    with sala_lock:
        if estado_sala == "EMPTY":
            estado_sala = "DOGS" if especie == "DOG" else "CATS"
        if (estado_sala == "DOGS"
                and especie == "DOG") or (estado_sala == "CATS"
                                          and especie == "CAT"):
            if especie == "DOG":
                cachorros += 1
            else:
                gatos += 1
            print(
                f"{especie} {id} entrou. Estado: {estado_sala} (Dogs={cachorros}, Cats={gatos})"
            )
    
    # Tempo de descanso
    time.sleep(descanso)
    
    with sala_lock:
        if especie == "DOG":
            cachorros -= 1
            if cachorros == 0:
                estado_sala = "EMPTY"
        else:
            gatos -= 1
            if gatos == 0:
                estado_sala = "EMPTY"
        print(
            f"{especie} {id} saiu. Estado: {estado_sala} (Dogs={cachorros}, Cats={gatos})"
        )


def process_vet_room_protocol(input_data):
    """
    Processa o protocolo da sala veterinária conforme especificação JSON.
    
    Args:
        input_data (dict): Dicionário contendo a estrutura JSON padronizada
    """
    global estado_sala, cachorros, gatos
    
    # Reset estado global
    estado_sala = input_data["room"]["initial_sign_state"]
    cachorros = 0
    gatos = 0
    
    print(f"=== Protocolo da Sala Veterinária ===")
    print(f"Versão: {input_data['spec_version']}")
    print(f"ID do desafio: {input_data['challenge_id']}")
    print(f"Estado inicial da sala: {estado_sala}")
    print(f"Política da fila: {input_data['metadata']['queue_policy']}")
    print(f"Latência de mudança de sinal: {input_data['metadata']['sign.change.latency']}")
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
    # Exemplo de entrada JSON conforme especificação da questão
    input_json = {
    "spec_version": "1.0",
    "challenge_id": "vet.room.protocol.demo",
    "metadata": {
        "room_count": 1,
        "allowed_states": ["EMPTY", "DOGS", "CATS"],
        "queue_policy": "FIFO",
        "sign.change.latency": 0,
        "tie_breaker": ["arrival.time", "id"]
    },
    "room": {
        "initial_sign_state": "EMPTY"
    },
    "workload": {
        "time_unit": "ticks",
        "animals": [
        { "id": "D01", "species": "DOG", "arrival_time": 0, "rest_duration": 5 },
        { "id": "D02", "species": "DOG", "arrival_time": 1, "rest_duration": 4 },
        { "id": "D03", "species": "DOG", "arrival_time": 2, "rest_duration": 3 },

        { "id": "C01", "species": "CAT", "arrival_time": 10, "rest_duration": 4 },
        { "id": "C02", "species": "CAT", "arrival_time": 11, "rest_duration": 2 }
        ]
    }
    }

    
    process_vet_room_protocol(input_json)