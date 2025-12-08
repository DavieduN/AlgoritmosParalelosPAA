# ai generated code

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from shared import read_input, testcases, output_folder

# Configuração
CSV_FILES = {
    "Sequencial": "sequencial.csv",
    "Paralelo": "paralelo.csv",
    "Distribuido": "distribuido.csv"
}

def carregar_dados():
    """
    Lê os inputs originais para mapear 'Qual teste é qual N'
    e junta com os tempos dos CSVs.
    """
    # 1. Mapear Teste ID -> Tamanho N
    map_id_to_n = []
    print("Lendo dataset original para mapear N...")
    for i in range(testcases):
        try:
            n, _, _ = read_input(i)
            map_id_to_n.append(n)
        except:
            break
            
    # 2. Ler os CSVs de resultados
    data_frames = []
    
    for nome_versao, arquivo in CSV_FILES.items():
        path = os.path.join(output_folder, arquivo)
        if not os.path.exists(path):
            print(f"[AVISO] Arquivo {arquivo} não encontrado. Pulando.")
            continue
            
        # O CSV tem apenas uma coluna 'duration'. 
        # Assumimos que a ordem das linhas bate com a ordem do testcases (0, 1, 2...)
        df = pd.read_csv(path)

        # Ensure 'duration' parsed as float and round to 6 decimal places
        if 'duration' in df.columns:
            df['duration'] = pd.to_numeric(df['duration'], errors='coerce').round(6)
        
        # Adiciona a coluna N baseada no índice
        # Cortamos o map_id_to_n caso o CSV tenha menos linhas (ex: crashou no meio)
        limit = min(len(df), len(map_id_to_n))
        df = df.iloc[:limit]
        df['N'] = map_id_to_n[:limit]
        df['Versao'] = nome_versao
        
        data_frames.append(df)
    
    if not data_frames:
        print("Nenhum dado encontrado.")
        return None

    full_df = pd.concat(data_frames)
    return full_df

def gerar_graficos_por_tamanho(df_agrupado):
    """
    Gera um gráfico separado para cada tamanho de N encontrado.
    """
    tamanhos = sorted(df_agrupado['N'].unique())
    
    os.makedirs("graficos", exist_ok=True)
    
    for n in tamanhos:
        subset = df_agrupado[df_agrupado['N'] == n]
        
        # Dados para o gráfico
        versoes = subset['Versao'].tolist()
        tempos = subset['duration'].tolist() # Média de tempo
        speedups = subset['Speedup'].tolist()
        
        # Configuração do Plot (2 eixos: Tempo e Speedup)
        fig, ax1 = plt.subplots(figsize=(8, 6))
        
        # Bar Chart para Tempo
        bars = ax1.bar(versoes, tempos, color=['#1f77b4', '#ff7f0e', '#2ca02c'], alpha=0.7)
        ax1.set_ylabel('Tempo Médio (s)', color='black', fontsize=12)
        ax1.set_title(f'Desempenho para Matriz N={n}', fontsize=14)
        ax1.tick_params(axis='y', labelcolor='black')
        
        # Adicionar valores nas barras
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                     f'{height:.4f}s',
                     ha='center', va='bottom')

        # Eixo secundário para Speedup (Linha)
        ax2 = ax1.twinx()
        ax2.plot(versoes, speedups, color='red', marker='o', linestyle='-', linewidth=2, label='Speedup')
        ax2.set_ylabel('Speedup (x)', color='red', fontsize=12)
        ax2.tick_params(axis='y', labelcolor='red')
        
        # Adicionar valores nos pontos de speedup
        for i, txt in enumerate(speedups):
            ax2.annotate(f"{txt:.2f}x", (versoes[i], speedups[i]), 
                         textcoords="offset points", xytext=(0,10), ha='center', color='red', weight='bold')

        plt.tight_layout()
        filename = f"graficos/resultado_N_{n}.png"
        plt.savefig(filename)
        plt.close()
        print(f"Gráfico salvo: {filename}")

def main():
    df = carregar_dados()
    if df is None: return

    # Agrupar por Versão e N, tirando a média do tempo
    df_mean = df.groupby(['Versao', 'N'])['duration'].mean().reset_index()
    
    # Calcular Speedup
    # Precisamos pegar o tempo sequencial de cada N para usar como base
    seq_times = df_mean[df_mean['Versao'] == 'Sequencial'].set_index('N')['duration']
    
    def calc_speedup(row):
        if row['N'] in seq_times.index:
            base_time = seq_times[row['N']]
            return base_time / row['duration']
        return 0.0

    df_mean['Speedup'] = df_mean.apply(calc_speedup, axis=1)
    
    # Calcular Eficiência (Speedup / 4 processadores)
    df_mean['Eficiencia'] = df_mean['Speedup'] / 4.0
    
    # Salvar tabela final
    # Round numeric columns to 6 decimal places for consistent output
    numeric_cols = df_mean.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        df_mean[numeric_cols] = df_mean[numeric_cols].round(6)

    print("\n--- Tabela de Resultados (Média) ---")
    print(df_mean)
    df_mean.to_csv("tabela_final_relatorio.csv", index=False)
    
    # Gerar Gráficos
    gerar_graficos_por_tamanho(df_mean)

if __name__ == "__main__":
    main()