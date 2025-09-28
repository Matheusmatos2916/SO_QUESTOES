import statistics
from collections import deque
import random
import matplotlib.pyplot as plt


class Processo:

    def __init__(self, pid, arrival, burst):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.start = None
        self.finish = None


def calcular_metricas(processos, seq_execucao, T):
    tempos_espera = []
    tempos_retorno = []
    concluidos = 0

    for p in processos:
        turnaround = p.finish - p.arrival
        waiting = turnaround - p.burst
        tempos_espera.append(waiting)
        tempos_retorno.append(turnaround)
        if p.finish <= T:
            concluidos += 1

    return {
        "tempo_espera_medio": round(statistics.mean(tempos_espera), 2),
        "tempo_espera_std": round(statistics.stdev(tempos_espera), 2) if len(tempos_espera) > 1 else 0,
        "tempo_retorno_medio": round(statistics.mean(tempos_retorno), 2),
        "tempo_retorno_std": round(statistics.stdev(tempos_retorno), 2) if len(tempos_retorno) > 1 else 0,
        "vazao": concluidos,
        "seq_execucao": seq_execucao
    }


# ---------------- Algoritmos ----------------
def fcfs(processos, ctx_cost, T):
    tempo = 0
    seq = []
    for p in sorted(processos, key=lambda x: x.arrival):
        if tempo < p.arrival:
            tempo = p.arrival
        p.start = tempo
        tempo += p.burst + ctx_cost
        p.finish = tempo
        seq.extend([p.pid] * p.burst)
    return calcular_metricas(processos, seq, T)


def sjf(processos, ctx_cost, T):
    tempo = 0
    seq = []
    concluidos = []
    processos = sorted(processos, key=lambda x: x.arrival)

    while len(concluidos) < len(processos):
        prontos = [
            p for p in processos if p.arrival <= tempo and p not in concluidos
        ]
        if prontos:
            p = min(prontos, key=lambda x: x.burst)
            p.start = tempo
            tempo += p.burst + ctx_cost
            p.finish = tempo
            concluidos.append(p)
            seq.extend([p.pid] * p.burst)
        else:
            prox = min([p.arrival for p in processos if p not in concluidos])
            tempo = prox
    return calcular_metricas(processos, seq, T)


def rr(processos, quantum, ctx_cost, T):
    tempo = 0
    fila = deque()
    seq = []
    concluidos = []
    processos = sorted(processos, key=lambda x: x.arrival)
    i = 0

    while len(concluidos) < len(processos):
        while i < len(processos) and processos[i].arrival <= tempo:
            fila.append(processos[i])
            i += 1

        if fila:
            p = fila.popleft()
            exec_time = min(quantum, p.remaining)
            p.remaining -= exec_time
            seq.extend([p.pid] * exec_time)
            tempo += exec_time + ctx_cost
            if p.remaining == 0:
                p.finish = tempo
                concluidos.append(p)
            else:
                while i < len(processos) and processos[i].arrival <= tempo:
                    fila.append(processos[i])
                    i += 1
                fila.append(p)
        else:
            if i < len(processos):
                tempo = processos[i].arrival
            else:
                break
    return calcular_metricas(processos, seq, T)


# ---------------- Gerador de workload ----------------
def gerar_processos(n, t1, t2, t3, t4, arrival_max=50):
    processos = []
    for i in range(n):
        pid = f"P{i+1:02d}"
        arrival = random.randint(0, arrival_max)
        if i < n // 2:
            burst = random.randint(t1, t2)
        else:
            burst = random.randint(t3, t4)
        processos.append(Processo(pid, arrival, burst))
    processos.sort(key=lambda x: x.arrival)
    return processos


# ---------------- Execução ----------------
def q1():
    ctx_cost = 1
    T = 100
    rr_quantums = [1, 2, 4, 8, 16]

    # gerar processos (exemplo: 10 processos, bursts curtos 1–5, longos 15–30)
    processos = gerar_processos(n=10, t1=1, t2=5, t3=15, t4=30, arrival_max=40)

    print("Processos gerados:")
    for p in processos:
        print(f"{p.pid}: chegada={p.arrival}, burst={p.burst}")

    resultados = {}

    resultados["FCFS"] = fcfs(
        [Processo(p.pid, p.arrival, p.burst) for p in processos], ctx_cost, T)
    resultados["SJF"] = sjf(
        [Processo(p.pid, p.arrival, p.burst) for p in processos], ctx_cost, T)

    for q in rr_quantums:
        resultados[f"RR-{q}"] = rr(
            [Processo(p.pid, p.arrival, p.burst) for p in processos], q,
            ctx_cost, T)

    # Mostrar no terminal
    for alg, res in resultados.items():
        print(f"\n=== {alg} ===")
        print(res)

    # ---------------- Gráficos ----------------
    algs = list(resultados.keys())
    espera = [res["tempo_espera_medio"] for res in resultados.values()]
    retorno = [res["tempo_retorno_medio"] for res in resultados.values()]
    vazao = [res["vazao"] for res in resultados.values()]

    plt.figure(figsize=(12, 4))

    plt.subplot(1, 3, 1)
    plt.bar(algs, espera)
    plt.xticks(rotation=45)
    plt.title("Tempo médio de espera")

    plt.subplot(1, 3, 2)
    plt.bar(algs, retorno)
    plt.xticks(rotation=45)
    plt.title("Tempo médio de retorno")

    plt.subplot(1, 3, 3)
    plt.bar(algs, vazao)
    plt.xticks(rotation=45)
    plt.title("Vazão (T=100)")

    plt.tight_layout()
    plt.show()


def process_scheduling_algorithms(input_data):
    """
    Processa algoritmos de escalonamento conforme especificação JSON.
    
    Args:
        input_data (dict): Dicionário contendo a estrutura JSON padronizada
    """
    print("=== Questão 1: Comparação de Algoritmos de Escalonamento ===")
    print(f"Versão: {input_data['spec_version']}")
    print(f"ID do desafio: {input_data['challenge_id']}")
    print(f"Custo de troca de contexto: {input_data['metadata']['context_switch_cost']}")
    print(f"Janela de vazão T: {input_data['metadata']['throughput_window_T']}")
    print(f"Algoritmos: {input_data['metadata']['algorithms']}")
    print(f"Quanta RR: {input_data['metadata']['rr_quantums']}")
    print()
    
    # Extrai parâmetros
    ctx_cost = input_data['metadata']['context_switch_cost']
    T = input_data['metadata']['throughput_window_T']
    rr_quantums = input_data['metadata']['rr_quantums']
    
    # Converte processos do JSON para objetos Processo
    processos_json = input_data['workload']['processes']
    processos = []
    for p_data in processos_json:
        processos.append(Processo(
            pid=p_data['pid'],
            arrival=p_data['arrival_time'],
            burst=p_data['burst_time']
        ))
    
    print("Processos do workload:")
    for p in processos:
        print(f"  {p.pid}: chegada={p.arrival}, burst={p.burst}")
    print()
    
    resultados = {}
    
    # Executa FCFS
    if "FCFS" in input_data['metadata']['algorithms']:
        print("=== Executando FCFS ===")
        resultados["FCFS"] = fcfs(
            [Processo(p.pid, p.arrival, p.burst) for p in processos], 
            ctx_cost, T
        )
    
    # Executa SJF
    if "SJF" in input_data['metadata']['algorithms']:
        print("=== Executando SJF ===")
        resultados["SJF"] = sjf(
            [Processo(p.pid, p.arrival, p.burst) for p in processos], 
            ctx_cost, T
        )
    
    # Executa RR para diferentes quanta
    if "RR" in input_data['metadata']['algorithms']:
        for q in rr_quantums:
            print(f"=== Executando RR (quantum={q}) ===")
            resultados[f"RR-{q}"] = rr(
                [Processo(p.pid, p.arrival, p.burst) for p in processos], 
                q, ctx_cost, T
            )
    
    # Mostra resultados
    print("\n" + "="*60)
    print("RESULTADOS COMPARATIVOS")
    print("="*60)
    
    for alg, res in resultados.items():
        print(f"\n{alg}:")
        print(f"  Tempo de espera médio: {res['tempo_espera_medio']} ± {res['tempo_espera_std']}")
        print(f"  Tempo de retorno médio: {res['tempo_retorno_medio']} ± {res['tempo_retorno_std']}")
        print(f"  Vazão (T={T}): {res['vazao']} processos")
        print(f"  Sequência de execução: {res['seq_execucao'][:20]}{'...' if len(res['seq_execucao']) > 20 else ''}")
    
    return resultados


def q1_json():
    """
    Executa a comparação de algoritmos usando a estrutura JSON padronizada.
    """
    # Exemplo de entrada JSON conforme especificação da Questão 1
    input_json = {
        "spec_version": "1.0",
        "challenge_id": "rr_fefs_sjf_demo",
        "metadata": {
            "context_switch_cost": 1,
            "throughput_window_T": 100,
            "algorithms": ["FCFS", "SJF", "RR"],
            "rr_quantums": [1, 2, 4, 8, 16]
        },
        "workload": {
            "time_unit": "ticks",
            "processes": [
                { "pid": "P01", "arrival_time": 0, "burst_time": 5 },
                { "pid": "P02", "arrival_time": 1, "burst_time": 17 },
                { "pid": "P03", "arrival_time": 2, "burst_time": 3 },
                { "pid": "P04", "arrival_time": 4, "burst_time": 22 },
                { "pid": "P05", "arrival_time": 6, "burst_time": 7 }
            ]
        }
    }
    
    return process_scheduling_algorithms(input_json)
