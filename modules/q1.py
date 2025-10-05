import json
import matplotlib.pyplot as plt

# -------------------------------
# Leitura do JSON
# -------------------------------
def ler_processos_json(path="processos.json"):
    with open(path, "r") as f:
        return json.load(f)

# -------------------------------
# Algoritmos de Escalonamento
# -------------------------------
def fcfs(processos, ctx_cost, T):
    tempo = 0
    tempos_espera = []
    tempos_retorno = []
    concluidos = 0

    for p in sorted(processos, key=lambda x: x["arrival_time"]):
        if tempo < p["arrival_time"]:
            tempo = p["arrival_time"]
        espera = tempo - p["arrival_time"]
        tempos_espera.append(espera)
        tempo += p["burst_time"]
        retorno = tempo - p["arrival_time"]
        tempos_retorno.append(retorno)
        concluidos += 1
        tempo += ctx_cost

    vazao = concluidos / (T / tempo) if tempo > 0 else 0
    return sum(tempos_espera)/len(processos), sum(tempos_retorno)/len(processos), vazao

def sjf(processos, ctx_cost, T):
    tempo = 0
    fila = []
    processos_ordenados = sorted(processos, key=lambda p: p["arrival_time"])
    tempos_espera = []
    tempos_retorno = []
    concluidos = 0
    i = 0
    n = len(processos)

    while fila or i < n:
        while i < n and processos_ordenados[i]["arrival_time"] <= tempo:
            fila.append(processos_ordenados[i])
            i += 1

        if fila:
            fila.sort(key=lambda p: p["burst_time"])
            p = fila.pop(0)
            espera = tempo - p["arrival_time"]
            tempos_espera.append(espera)
            tempo += p["burst_time"]
            retorno = tempo - p["arrival_time"]
            tempos_retorno.append(retorno)
            concluidos += 1
            tempo += ctx_cost
        else:
            tempo = processos_ordenados[i]["arrival_time"]

    vazao = concluidos / (T / tempo) if tempo > 0 else 0
    return sum(tempos_espera)/n, sum(tempos_retorno)/n, vazao

def rr(processos, quantum, ctx_cost, T):
    # 🚨 Correção: se quantum >= maior burst, RR vira FCFS
    max_burst = max(p["burst_time"] for p in processos)
    if quantum >= max_burst:
        return fcfs(processos, ctx_cost, T)

    tempo = 0
    fila = []
    processos_ordenados = sorted(processos, key=lambda p: p["arrival_time"])
    tempos_espera = []
    tempos_retorno = []
    concluidos = 0
    i = 0
    n = len(processos)
    tempo_restante = [p["burst_time"] for p in processos]

    while fila or i < n:
        while i < n and processos_ordenados[i]["arrival_time"] <= tempo:
            fila.append(i)
            i += 1

        if fila:
            idx = fila.pop(0)
            exec_time = min(quantum, tempo_restante[idx])
            tempo += exec_time
            tempo_restante[idx] -= exec_time

            if tempo_restante[idx] == 0:
                tempos_espera.append(tempo - processos_ordenados[idx]["arrival_time"] - processos_ordenados[idx]["burst_time"])
                tempos_retorno.append(tempo - processos_ordenados[idx]["arrival_time"])
                concluidos += 1
            else:
                while i < n and processos_ordenados[i]["arrival_time"] <= tempo:
                    fila.append(i)
                    i += 1
                fila.append(idx)

            tempo += ctx_cost
        else:
            tempo = processos_ordenados[i]["arrival_time"]

    vazao = concluidos / (T / tempo) if tempo > 0 else 0
    return sum(tempos_espera)/n, sum(tempos_retorno)/n, vazao

# -------------------------------
# Função principal (q1)
# -------------------------------
def q1():
    dados = ler_processos_json("modules/q1_2.json")
    processos = dados["workload"]["processes"]
    ctx_cost = dados["metadata"]["context_switch_cost"]
    T = dados["metadata"]["throughput_window_T"]

    resultados = {}
    resultados["FCFS"] = fcfs(processos, ctx_cost, T)
    resultados["SJF"] = sjf(processos, ctx_cost, T)
    for q in dados["metadata"]["rr_quantums"]:
        resultados[f"RR-{q}"] = rr(processos, q, ctx_cost, T)
    # Adicionar RR-16 para comparação
    resultados["RR-16"] = rr(processos, 16, ctx_cost, T)

    # Impressão dos resultados no terminal
    print("=" * 60)
    print("RESULTADOS DOS ALGORITMOS DE ESCALONAMENTO")
    print("=" * 60)
    print(f"Context Switch Cost: {ctx_cost}")
    print(f"Throughput Window (T): {T}")
    print(f"Número de processos: {len(processos)}")
    print("-" * 60)
    
    for algoritmo, (espera_media, retorno_medio, vazao) in resultados.items():
        print(f"\n{algoritmo}:")
        print(f"  Tempo médio de espera: {espera_media:.2f}")
        print(f"  Tempo médio de retorno: {retorno_medio:.2f}")
        print(f"  Vazão: {vazao:.4f}")
    
    print("\n" + "=" * 60)

    # Plotagem dos resultados
    labels = list(resultados.keys())
    espera = [resultados[a][0] for a in labels]
    retorno = [resultados[a][1] for a in labels]
    vazao = [resultados[a][2] for a in labels]

    fig, axs = plt.subplots(1, 3, figsize=(14, 5))
    axs[0].bar(labels, espera)
    axs[0].set_title("Tempo médio de espera")
    axs[0].tick_params(axis='x', rotation=45)

    axs[1].bar(labels, retorno)
    axs[1].set_title("Tempo médio de retorno")
    axs[1].tick_params(axis='x', rotation=45)

    axs[2].bar(labels, vazao)
    axs[2].set_title("Vazão (T=100)")
    axs[2].tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    q1()
