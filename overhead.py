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
    
    # --- MÉTRICA 1: Tempo Ideal e Overhead Absoluto (Segundos) ---
    df_final['time_ideal'] = df_final['time_seq'] / df_final['Cores']
    # Overhead_Time = Tempo Real - Tempo Ideal
    df_final['Overhead_Time'] = (df_final['duration'] - df_final['time_ideal']).clip(lower=0)
    
    # --- MÉTRICA 2: Overhead Percentual (%) ---
    df_final['Overhead_Pct'] = (df_final['Overhead_Time'] / df_final['duration']) * 100
    
    # --- MÉTRICA 3: Sua Fórmula (Overhead Relativo ao Sequencial) ---
    # Formula: O = (Tn * n - T1) / T1
    # Tn = duration, n = Cores, T1 = time_seq
    df_final['Wasted_Work'] = (df_final['duration'] * df_final['Cores']) - df_final['time_seq']
    df_final['Overhead_Formula'] = df_final['Wasted_Work'] / df_final['time_seq']
    
    # Limpeza de valores negativos (casos super-lineares)
    df_final['Overhead_Formula'] = df_final['Overhead_Formula'].clip(lower=0)
    
    return df_final

def plot_generico(df, algoritmo, y_col, titulo, y_label, filename, paleta="viridis"):
    """Função genérica para plotar qualquer métrica"""
    subset = df[(df['Algoritmo'] == algoritmo) & (df['Cores'] > 1)]
    if subset.empty: return

    plt.figure(figsize=(10, 6))
    sns.lineplot(data=subset, x='N', y=y_col, hue='Cores', palette=paleta, marker="o", linewidth=2.5)
    
    plt.title(f"{titulo} - {algoritmo}", fontsize=16)
    plt.ylabel(y_label)
    plt.xlabel("Tamanho da Matriz (N)")
    plt.xticks(subset['N'].unique())
    plt.legend(title="Núcleos")
    
    path = f"graficos/{filename}"
    plt.savefig(path)
    plt.close()
    print(f"Gerado: {path}")

def main():
    os.makedirs("graficos", exist_ok=True)
    
    raw_df = carregar_dados()
    if raw_df is None: return
    
    stats_df = calcular_metricas(raw_df)
    
    # Salva CSV com todas as métricas para você conferir
    stats_df.to_csv("metricas_completas.csv", index=False)
    print("Dados salvos em 'metricas_completas.csv'")
    
    minhas_cores = {
        2: "red",
        4: "green",
        8: "blue"
    }
    
    for algo in ["Paralelo", "Distribuido"]:
        # 1. Gráfico da SUA FÓRMULA (Tn*n - T1)/T1
        plot_generico(stats_df, algo, 'Overhead_Formula', 
                     "Overhead Relativo", "Overhead (Fração de T1)", 
                     f"overhead_formula_{algo}.png", minhas_cores)
        
        # 2. Gráfico de Tempo Absoluto (Segundos gastos à toa)
        plot_generico(stats_df, algo, 'Overhead_Time', 
                     "Custo de Overhead (Tempo)", "Segundos", 
                     f"overhead_tempo_{algo}.png", minhas_cores)

        # 3. Gráfico de Porcentagem (% do tempo total que é lixo)
        plot_generico(stats_df, algo, 'Overhead_Pct', 
                     "Impacto do Overhead (%)", "% do Tempo Total", 
                     f"overhead_pct_{algo}.png", minhas_cores)

if __name__ == "__main__":
    main()