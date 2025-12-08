# ai generated code

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os
from shared import read_input, testcases, output_folder

# Configuração Visual
sns.set_theme(style="whitegrid")

# Mapeamento dos Arquivos
FILES_MAP = {
    "Sequencial": "sequencial.csv",
    "Paralelo (2 Cores)": "paralelo2.csv",
    "Paralelo (4 Cores)": "paralelo4.csv",
    "Paralelo (8 Cores)": "paralelo8.csv",
    "Distribuido (2 Nós)": "distribuido2.csv",
    "Distribuido (4 Nós)": "distribuido4.csv",
    "Distribuido (8 Nós)": "distribuido8.csv"
}

def carregar_dados():
    # 1. Mapear Teste ID -> Tamanho N
    map_id_to_n = []
    for i in range(testcases):
        try:
            n, _, _ = read_input(i)
            map_id_to_n.append(n)
        except:
            break
            
    data_frames = []
    
    for label, filename in FILES_MAP.items():
        path = os.path.join(output_folder, filename)
        if not os.path.exists(path):
            print(f"[AVISO] {filename} não encontrado. Ignorando.")
            continue
            
        df = pd.read_csv(path)
        limit = min(len(df), len(map_id_to_n))
        df = df.iloc[:limit]
        df['N'] = map_id_to_n[:limit]
        df['Algoritmo'] = label.split()[0] 
        
        if "Sequencial" in label:
            df['Cores'] = 1
        else:
            import re
            nums = re.findall(r'\d+', label)
            df['Cores'] = int(nums[0]) if nums else 1
            
        df['NomeCompleto'] = label
        data_frames.append(df)
    
    if not data_frames: return None
    return pd.concat(data_frames)

def calcular_metricas(df):
    # Agrupa por NomeCompleto e N -> Média de Tempo
    df_mean = df.groupby(['Algoritmo', 'Cores', 'NomeCompleto', 'N'])['duration'].mean().reset_index()
    
    seq_df = df_mean[df_mean['Algoritmo'] == 'Sequencial'][['N', 'duration']]
    seq_df = seq_df.rename(columns={'duration': 'time_seq'})
    
    df_final = pd.merge(df_mean, seq_df, on='N', how='left')
    df_final['Speedup'] = df_final['time_seq'] / df_final['duration']
    df_final['Eficiencia'] = df_final['Speedup'] / df_final['Cores']
    
    # ARREDONDAMENTO PARA 6 CASAS DECIMAIS
    cols_to_round = ['duration', 'time_seq', 'Speedup', 'Eficiencia']
    df_final[cols_to_round] = df_final[cols_to_round].round(6)
    
    return df_final

def plot_escalabilidade(df, algoritmo, filename):
    subset = df[df['Algoritmo'] == algoritmo]
    if subset.empty: return

    plt.figure(figsize=(10, 6))
    
    sns.lineplot(data=subset, x='N', y='Speedup', hue='Cores', palette="viridis", marker="o", linewidth=2.5)
    
    plt.title(f"Escalabilidade - {algoritmo} (Speedup)", fontsize=16)
    plt.ylabel("Speedup (x vezes mais rápido)")
    plt.xlabel("Tamanho da Matriz (N)")
    plt.xticks(subset['N'].unique())
    plt.legend(title="Núcleos")
    
    plt.savefig(f"graficos/{filename}")
    plt.close()
    print(f"Gerado: graficos/{filename}")

def plot_comparacao_barras(df, log_scale=False, log_base=10):
    """
    Gera gráfico de barras.
    log_base: pode ser 10, 2 ou np.e
    """
    subset = df[(df['Cores'] == 1) | (df['Cores'] == 8)].copy()
    
    plt.figure(figsize=(12, 6))
    
    ax = sns.barplot(data=subset, x='N', y='duration', hue='Algoritmo', palette="muted")
    
    # Define o texto do título dependendo da base
    if log_scale:
        if log_base == np.e:
            tipo_escala = "Log Natural (ln)"
        else:
            tipo_escala = f"Logarítmica (Base {log_base})"
    else:
        tipo_escala = "Linear"

    plt.title(f"Comparação Final ({tipo_escala}): Seq vs Par(8) vs Dist(8)", fontsize=16)
    plt.ylabel("Tempo de Execução (s)")
    plt.xlabel("Tamanho da Matriz (N)")
    
    if log_scale:
        # AQUI ESTÁ O TRUQUE:
        plt.yscale("log", base=log_base)
        
        # Ajuste o nome do arquivo para não sobrescrever
        base_name = "e" if log_base == np.e else str(log_base)
        nome_arq = f"comparacao_global_log{base_name}.png"
        
        # Opcional: Ajustar o formatador do eixo Y para não ficar em notação científica estranha
        from matplotlib.ticker import ScalarFormatter
        ax.yaxis.set_major_formatter(ScalarFormatter())
    else:
        for container in ax.containers:
            ax.bar_label(container, fmt='%.2f', padding=3, rotation=90, fontsize=9)
        nome_arq = "comparacao_global_linear.png"
        plt.ylim(0, subset['duration'].max() * 1.15) 
    
    plt.savefig(f"graficos/{nome_arq}")
    plt.close()
    print(f"Gerado: graficos/{nome_arq}")

def plot_detalhe_por_n(df):
    """
    Gera 5 gráficos independentes (um para cada N),
    comparando apenas Sequencial vs Paralelo(8) vs Distribuído(8).
    """
    # Filtra: Queremos Sequencial (Cores=1) OU os de 8 Cores
    # Se quiser comparar o de 4 cores, mude o 8 para 4 abaixo
    mask = (df['Cores'] == 1) | (df['Cores'] == 8)
    df_filtered = df[mask].copy()
    
    # Garante que temos a lista de tamanhos ordenada
    tamanhos = sorted(df_filtered['N'].unique())
    
    print(f"Gerando gráficos individuais para N: {tamanhos}...")

    for n in tamanhos:
        subset = df_filtered[df_filtered['N'] == n]
        
        plt.figure(figsize=(8, 6))
        
        # Plot
        ax = sns.barplot(
            data=subset, 
            x='Algoritmo', 
            y='duration', 
            hue='Algoritmo', 
            palette="viridis", 
            dodge=False
        )
        
        plt.title(f"Tempo de Execução - Matriz N={n} (8 Cores)", fontsize=14)
        plt.ylabel("Tempo (segundos)")
        plt.xlabel("") # O rótulo do eixo X já diz o algoritmo
        
        # Adiciona os valores exatos em cima das barras (6 casas decimais)
        for container in ax.containers:
            ax.bar_label(container, fmt='%.6f', padding=3, fontsize=11)
            
        # Margem superior para o texto não cortar
        plt.ylim(0, subset['duration'].max() * 1.15)
        
        # Salva
        filename = f"graficos/comparacao_N_{n}.png"
        plt.savefig(filename)
        plt.close()
        print(f" -> Salvo: {filename}")

def main():
    os.makedirs("graficos", exist_ok=True)
    
    raw_df = carregar_dados()
    if raw_df is None: return
    
    stats_df = calcular_metricas(raw_df)
    
    # Salva tabela arredondada
    stats_df.to_csv("tabela_completa.csv", index=False)
    print("Tabela salva em 'tabela_completa.csv'")

    plot_detalhe_por_n(stats_df)
    
    # 1. Gráficos de Escalabilidade
    plot_escalabilidade(stats_df, "Paralelo", "escalabilidade_paralelo.png")
    plot_escalabilidade(stats_df, "Distribuido", "escalabilidade_distribuido.png")
    
   # 1. Escala Linear (Normal)
    plot_comparacao_barras(stats_df, log_scale=False)
    
    # 2. Escala Log Base 10 (Padrão)
    plot_comparacao_barras(stats_df, log_scale=True, log_base=10)
    
    # 3. Escala Log Base 2 (Recomendada para Ciência da Computação)
    plot_comparacao_barras(stats_df, log_scale=True, log_base=2)
    
    # 4. Escala Log Natural (Base e)
    plot_comparacao_barras(stats_df, log_scale=True, log_base=np.e)
    
    # 3. Comparação Global (LINEAR) - Bom para choque visual (Seq muito maior que Par)
    plot_comparacao_barras(stats_df, log_scale=False)

if __name__ == "__main__":
    main()