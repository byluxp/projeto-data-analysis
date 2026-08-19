"""
=============================================================================
Análise Exploratória de Dados — Catálogo Netflix
=============================================================================
Autor      : Analista de Dados
Dataset    : netflix_titles.csv  (~8.800 títulos)
Bibliotecas: numpy, pandas, matplotlib, seaborn
Descrição  : Script que responde 5 perguntas analíticas sobre o catálogo
             da Netflix, gerando visualizações salvas em docs/images/.
=============================================================================
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os
import warnings

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Configurações globais de estilo
# ---------------------------------------------------------------------------
# Paleta principal: tons que remetem à identidade visual da Netflix
NETFLIX_RED    = "#E50914"
NETFLIX_DARK   = "#141414"
NETFLIX_GRAY   = "#564d4d"
PALETTE_MAIN   = ["#E50914", "#B20710", "#FF6B6B", "#FF9A9A", "#FFC1C1"]
PALETTE_COOL   = sns.color_palette("magma", 10)

sns.set_theme(style="darkgrid", font_scale=1.1)
plt.rcParams.update({
    "figure.facecolor": "#1a1a2e",   # fundo escuro
    "axes.facecolor":   "#16213e",
    "axes.edgecolor":   "#e94560",
    "axes.labelcolor":  "white",
    "xtick.color":      "white",
    "ytick.color":      "white",
    "text.color":       "white",
    "grid.color":       "#2a2a4a",
    "grid.linestyle":   "--",
    "grid.alpha":       0.5,
    "font.family":      "DejaVu Sans",
})

# Diretório de saída das imagens
OUTPUT_DIR = os.path.join("docs", "images")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Utilitário: salvar figura com padding consistente
# ---------------------------------------------------------------------------
def salvar_figura(fig: plt.Figure, nome_arquivo: str) -> None:
    """
    Salva a figura gerada em PNG no diretório docs/images/.

    Parâmetros
    ----------
    fig          : objeto Figure do matplotlib
    nome_arquivo : nome do arquivo (ex: '01_tipo_conteudo.png')
    """
    caminho = os.path.join(OUTPUT_DIR, nome_arquivo)
    fig.savefig(caminho, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    print(f"  ✔  Gráfico salvo em: {caminho}")


# ---------------------------------------------------------------------------
# Carregamento e limpeza do dataset
# ---------------------------------------------------------------------------
def carregar_dados(caminho_csv: str = "netflix_titles.csv") -> pd.DataFrame:
    """
    Carrega o CSV do catálogo Netflix e aplica limpeza básica:
    - Remove registros sem coluna 'type' (essencial para todas as análises)
    - Converte 'date_added' para datetime
    - Extrai o ano de adição como coluna separada ('year_added')

    Parâmetros
    ----------
    caminho_csv : caminho para o arquivo CSV

    Retorna
    -------
    pd.DataFrame com os dados limpos
    """
    df = pd.read_csv(caminho_csv)

    print(f"\n{'='*60}")
    print(f" Dataset carregado: {df.shape[0]} registros | {df.shape[1]} colunas")
    print(f"{'='*60}")
    print(f" Valores nulos por coluna:\n{df.isnull().sum()}\n")

    # Remove linhas sem tipo definido (Movie / TV Show)
    df = df.dropna(subset=["type"])

    # Converte e extrai o ano de adição ao catálogo
    df["date_added"] = pd.to_datetime(df["date_added"].str.strip(),
                                      format="mixed", errors="coerce")
    df["year_added"] = df["date_added"].dt.year

    return df


# ---------------------------------------------------------------------------
# ANÁLISE 1 — Filmes vs. Séries
# ---------------------------------------------------------------------------
def analise_tipo_conteudo(df: pd.DataFrame) -> dict:
    """
    Pergunta: A Netflix é dominada por filmes ou séries no catálogo?

    Estratégia:
    - Conta a distribuição da coluna 'type' (Movie / TV Show)
    - Gera um gráfico de pizza (pie chart) com percentuais

    Retorna dict com os contadores para reuso no README.
    """
    print("\n[1/5] Analisando distribuição de tipo de conteúdo...")

    contagem = df["type"].value_counts()
    labels   = contagem.index.tolist()
    valores  = contagem.values.tolist()
    total    = sum(valores)
    pcts     = [v / total * 100 for v in valores]

    # --- Figura ---
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#1a1a2e")

    wedges, texts, autotexts = ax.pie(
        valores,
        labels=labels,
        autopct="%1.1f%%",
        startangle=140,
        colors=[NETFLIX_RED, "#0f3460"],
        wedgeprops={"edgecolor": "#1a1a2e", "linewidth": 2.5},
        textprops={"fontsize": 13, "color": "white"},
        pctdistance=0.75,
    )
    for at in autotexts:
        at.set_fontsize(14)
        at.set_fontweight("bold")

    ax.set_title("Distribuição do Catálogo Netflix\nFilmes vs. Séries",
                 fontsize=15, fontweight="bold", color="white", pad=20)

    # Anotação central com total
    ax.text(0, 0, f"{total:,}\ntítulos", ha="center", va="center",
            fontsize=12, fontweight="bold", color="white")

    salvar_figura(fig, "01_tipo_conteudo.png")
    plt.close(fig)

    resultado = dict(zip(labels, zip(valores, pcts)))
    for tipo, (qtd, pct) in resultado.items():
        print(f"   {tipo}: {qtd:,} ({pct:.1f}%)")

    return resultado


# ---------------------------------------------------------------------------
# ANÁLISE 2 — Ano de pico de adições ao catálogo
# ---------------------------------------------------------------------------
def analise_ano_pico(df: pd.DataFrame) -> pd.Series:
    """
    Pergunta: Qual foi o ano de pico em que a plataforma adicionou
              mais títulos ao catálogo?

    Estratégia:
    - Agrupa por 'year_added' e conta títulos
    - Filtra anos com dados completos (remove NaN e anos fora do range)
    - Plota bar chart com destaque no ano de pico

    Retorna a Series de contagem por ano.
    """
    print("\n[2/5] Analisando ano de pico de adições...")

    por_ano = (
        df.dropna(subset=["year_added"])
        .query("year_added >= 2008 and year_added <= 2021")
        .groupby("year_added")
        .size()
        .reset_index(name="total")
        .sort_values("year_added")
    )

    ano_pico = por_ano.loc[por_ano["total"].idxmax(), "year_added"]
    max_val  = por_ano["total"].max()

    # Paleta: destaca o ano de pico em vermelho Netflix
    cores = [
        NETFLIX_RED if int(a) == int(ano_pico) else "#0f3460"
        for a in por_ano["year_added"]
    ]

    fig, ax = plt.subplots(figsize=(12, 6))

    bars = ax.bar(
        por_ano["year_added"].astype(int),
        por_ano["total"],
        color=cores,
        edgecolor="#1a1a2e",
        linewidth=0.8,
    )

    # Rótulos sobre as barras
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 15,
                f"{int(h)}", ha="center", va="bottom",
                fontsize=8.5, color="white", fontweight="bold")

    # Anotação do pico
    ax.annotate(
        f"Pico: {int(ano_pico)}\n({int(max_val)} títulos)",
        xy=(int(ano_pico), max_val),
        xytext=(int(ano_pico) - 2, max_val * 0.85),
        arrowprops=dict(arrowstyle="->", color=NETFLIX_RED, lw=1.8),
        fontsize=11, color=NETFLIX_RED, fontweight="bold",
    )

    ax.set_title("Títulos Adicionados ao Catálogo Netflix por Ano",
                 fontsize=15, fontweight="bold", color="white", pad=15)
    ax.set_xlabel("Ano de Adição", fontsize=12)
    ax.set_ylabel("Número de Títulos", fontsize=12)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
    plt.xticks(rotation=45)

    salvar_figura(fig, "02_ano_pico.png")
    plt.close(fig)

    print(f"   Ano de pico: {int(ano_pico)} com {int(max_val)} títulos adicionados")
    return por_ano


# ---------------------------------------------------------------------------
# ANÁLISE 3 — Top 5 países produtores de conteúdo
# ---------------------------------------------------------------------------
def analise_paises_produtores(df: pd.DataFrame) -> pd.Series:
    """
    Pergunta: Quais são os 5 países que mais produzem conteúdo?

    Estratégia:
    - A coluna 'country' pode conter múltiplos países separados por vírgula
    - Faz o explode de co-produções para contar cada país individualmente
    - Exibe horizontal bar chart com gradiente de cor

    Retorna a Series com os top 5 países.
    """
    print("\n[3/5] Analisando países produtores de conteúdo...")

    # Separa co-produções e conta cada país individualmente
    paises = (
        df["country"]
        .dropna()
        .str.split(",")
        .explode()
        .str.strip()
        .value_counts()
        .head(5)
        .sort_values()          # ordem crescente para barh ficar bonito
    )

    fig, ax = plt.subplots(figsize=(10, 6))

    cores_grad = sns.color_palette("YlOrRd", len(paises))
    bars = ax.barh(
        paises.index,
        paises.values,
        color=cores_grad,
        edgecolor="#1a1a2e",
        height=0.6,
    )

    # Rótulo com valor dentro/fora de cada barra
    for bar, val in zip(bars, paises.values):
        ax.text(
            val - val * 0.02, bar.get_y() + bar.get_height() / 2,
            f"{val:,}", va="center", ha="right",
            fontsize=12, fontweight="bold", color="#1a1a2e",
        )

    ax.set_title("Top 5 Países Produtores de Conteúdo na Netflix",
                 fontsize=15, fontweight="bold", color="white", pad=15)
    ax.set_xlabel("Número de Títulos", fontsize=12)
    ax.set_ylabel("País", fontsize=12)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(
        lambda x, _: f"{int(x):,}"))

    salvar_figura(fig, "03_paises_produtores.png")
    plt.close(fig)

    for pais, qtd in paises.sort_values(ascending=False).items():
        print(f"   {pais}: {qtd:,} títulos")

    return paises


# ---------------------------------------------------------------------------
# ANÁLISE 4 — Longevidade das séries (temporadas)
# ---------------------------------------------------------------------------
def analise_temporadas_series(df: pd.DataFrame) -> pd.Series:
    """
    Pergunta: A maioria das séries termina na 1ª temporada ou consegue
              se expandir?

    Estratégia:
    - Filtra apenas 'TV Show'
    - A coluna 'duration' contém '1 Season', '2 Seasons' etc.
    - Extrai o número de temporadas e agrupa em faixas:
        1 temp / 2 temp / 3 temp / 4-5 temp / 6+ temp
    - Plota bar chart com proporções

    Retorna a Series de contagem por faixa.
    """
    print("\n[4/5] Analisando longevidade das séries...")

    series = df[df["type"] == "TV Show"].copy()
    series["n_seasons"] = (
        series["duration"]
        .str.extract(r"(\d+)")
        .astype(float)
    )

    # Agrupamento em faixas de temporadas
    def categorizar(n):
        if pd.isna(n):
            return "Desconhecido"
        n = int(n)
        if n == 1:   return "1 temporada"
        if n == 2:   return "2 temporadas"
        if n == 3:   return "3 temporadas"
        if n <= 5:   return "4–5 temporadas"
        return "6+ temporadas"

    series["faixa"] = series["n_seasons"].apply(categorizar)

    ordem = ["1 temporada", "2 temporadas", "3 temporadas",
             "4–5 temporadas", "6+ temporadas", "Desconhecido"]
    contagem = series["faixa"].value_counts().reindex(ordem, fill_value=0)

    # Remove 'Desconhecido' se zerado
    contagem = contagem[contagem > 0]

    total_series = len(series)
    pct_1s = contagem.get("1 temporada", 0) / total_series * 100

    cores_seq = sns.color_palette("magma_r", len(contagem))

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(
        contagem.index,
        contagem.values,
        color=cores_seq,
        edgecolor="#1a1a2e",
        linewidth=0.8,
        width=0.6,
    )

    for bar in bars:
        h = bar.get_height()
        pct = h / total_series * 100
        ax.text(bar.get_x() + bar.get_width() / 2, h + 8,
                f"{int(h)}\n({pct:.1f}%)",
                ha="center", va="bottom",
                fontsize=9.5, color="white", fontweight="bold")

    ax.set_title("Distribuição de Temporadas nas Séries da Netflix",
                 fontsize=15, fontweight="bold", color="white", pad=15)
    ax.set_xlabel("Número de Temporadas", fontsize=12)
    ax.set_ylabel("Quantidade de Séries", fontsize=12)

    salvar_figura(fig, "04_temporadas_series.png")
    plt.close(fig)

    print(f"   Total de séries: {total_series:,}")
    print(f"   Séries com 1 temporada: {contagem.get('1 temporada', 0):,} ({pct_1s:.1f}%)")
    return contagem


# ---------------------------------------------------------------------------
# ANÁLISE 5 — Top diretores e atores
# ---------------------------------------------------------------------------
def analise_top_diretores_atores(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """
    Pergunta: Quais são os diretores e atores que mais aparecem na plataforma?

    Estratégia Diretores:
    - Coluna 'director' pode ter múltiplos diretores separados por vírgula
    - Explode, conta e pega top 10

    Estratégia Atores:
    - Coluna 'cast' tem elenco separado por vírgula
    - Explode, conta e pega top 10

    Gera dois gráficos de barras horizontais.
    Retorna tupla (top_diretores, top_atores).
    """
    print("\n[5/5] Analisando top diretores e atores...")

    # --- Diretores ---
    top_diretores = (
        df["director"]
        .dropna()
        .str.split(",")
        .explode()
        .str.strip()
        .value_counts()
        .head(10)
        .sort_values()
    )

    fig, ax = plt.subplots(figsize=(11, 7))
    cores_dir = sns.color_palette("flare", len(top_diretores))
    bars = ax.barh(top_diretores.index, top_diretores.values,
                   color=cores_dir, edgecolor="#1a1a2e", height=0.65)

    for bar, val in zip(bars, top_diretores.values):
        ax.text(val + 0.2, bar.get_y() + bar.get_height() / 2,
                f"  {val}", va="center", ha="left",
                fontsize=11, color="white", fontweight="bold")

    ax.set_title("Top 10 Diretores com Mais Títulos na Netflix",
                 fontsize=15, fontweight="bold", color="white", pad=15)
    ax.set_xlabel("Número de Títulos", fontsize=12)
    ax.set_ylabel("Diretor", fontsize=12)
    ax.set_xlim(0, top_diretores.max() + 5)

    salvar_figura(fig, "05_top_diretores.png")
    plt.close(fig)

    # --- Atores ---
    top_atores = (
        df["cast"]
        .dropna()
        .str.split(",")
        .explode()
        .str.strip()
        .value_counts()
        .head(10)
        .sort_values()
    )

    fig, ax = plt.subplots(figsize=(11, 7))
    cores_at = sns.color_palette("crest", len(top_atores))
    bars = ax.barh(top_atores.index, top_atores.values,
                   color=cores_at, edgecolor="#1a1a2e", height=0.65)

    for bar, val in zip(bars, top_atores.values):
        ax.text(val + 0.2, bar.get_y() + bar.get_height() / 2,
                f"  {val}", va="center", ha="left",
                fontsize=11, color="white", fontweight="bold")

    ax.set_title("Top 10 Atores com Mais Títulos na Netflix",
                 fontsize=15, fontweight="bold", color="white", pad=15)
    ax.set_xlabel("Número de Títulos", fontsize=12)
    ax.set_ylabel("Ator / Atriz", fontsize=12)
    ax.set_xlim(0, top_atores.max() + 5)

    salvar_figura(fig, "05_top_atores.png")
    plt.close(fig)

    print(f"   Diretor #1: {top_diretores.index[-1]} ({top_diretores.iloc[-1]} títulos)")
    print(f"   Ator/Atriz #1: {top_atores.index[-1]} ({top_atores.iloc[-1]} títulos)")

    return top_diretores, top_atores


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------
def main():
    """
    Orquestra a execução de todas as análises na sequência correta.
    Cada função é independente e pode ser chamada isoladamente se necessário.
    """
    print("\n" + "="*60)
    print("  ANÁLISE EXPLORATÓRIA — CATÁLOGO NETFLIX")
    print("="*60)

    # 1. Carregamento
    df = carregar_dados("netflix_titles.csv")

    # 2. Análises
    res_tipo      = analise_tipo_conteudo(df)
    res_ano       = analise_ano_pico(df)
    res_paises    = analise_paises_produtores(df)
    res_temporada = analise_temporadas_series(df)
    res_dir, res_at = analise_top_diretores_atores(df)

    print("\n" + "="*60)
    print("  ✔  Todas as análises concluídas!")
    print(f"  ✔  Imagens salvas em: {os.path.abspath(OUTPUT_DIR)}")
    print("="*60 + "\n")

    return {
        "tipo":       res_tipo,
        "ano":        res_ano,
        "paises":     res_paises,
        "temporadas": res_temporada,
        "diretores":  res_dir,
        "atores":     res_at,
    }


if __name__ == "__main__":
    main()
