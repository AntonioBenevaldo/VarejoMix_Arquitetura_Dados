"""Gera os diagramas do relatório em diagramas/*.png.

    python3 scripts/gerar_diagramas.py

Sem dependências além de matplotlib. Layout com margens explícitas para que
nenhum texto se sobreponha às caixas.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "diagramas"
OUT.mkdir(exist_ok=True)

NAVY = "#14385f"
BLUE = "#1f6fb2"
LIGHT = "#e8f1fa"
GREEN = "#1f7a5a"
GOLD = "#b8860b"
GREY = "#5c6b7a"
PANEL = "#f4f7fb"


def box(ax, x, y, w, h, text, *, face, edge, color, size=11, weight="bold", radius=0.9):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle=f"round,pad=0,rounding_size={radius}",
                                facecolor=face, edgecolor=edge, linewidth=1.6))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=size, fontweight=weight, color=color, linespacing=1.45)


def arrow(ax, p1, p2, color=BLUE, lw=1.8):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=16,
                                 linewidth=lw, color=color,
                                 shrinkA=2, shrinkB=2))


def canvas(w, h):
    fig, ax = plt.subplots(figsize=(w, h), dpi=150)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    return fig, ax


# ---------------------------------------------------------------- diagrama 1
fig, ax = canvas(12, 6.1333)
ax.text(4, 94, "Arquitetura proposta e fluxo de dados", fontsize=19,
        fontweight="bold", color=NAVY, va="center")
ax.text(4, 87.5, "ingestão → transformação → consumo analítico",
        fontsize=12, color=GREY, va="center")

# painéis
for x, w, titulo in [(4, 19, "FONTES"), (28, 19, "INGESTÃO"),
                     (52, 21, "LAKEHOUSE"), (78, 18, "CONSUMO")]:
    ax.add_patch(FancyBboxPatch((x, 20), w, 60,
                                boxstyle="round,pad=0,rounding_size=1.2",
                                facecolor=PANEL, edgecolor="#dbe4ee", linewidth=1.2))
    ax.text(x + 1.6, 76.5, titulo, fontsize=11.5, fontweight="bold", color=NAVY,
            ha="left", va="center")

box(ax, 6, 58, 15, 12, "PostgreSQL\nOLTP", face=NAVY, edge=NAVY, color="white")
box(ax, 6, 28, 15, 12, "MongoDB\neventos JSON", face=GREEN, edge=GREEN, color="white")

box(ax, 30, 58, 15, 12, "CDC / carga\nincremental diária",
    face=BLUE, edge=BLUE, color="white", size=10)
box(ax, 30, 28, 15, 12, "Batch de eventos\n+ validação",
    face=BLUE, edge=BLUE, color="white", size=10)

box(ax, 54, 64, 17, 10, "BRONZE\nbruto + metadados", face="#6b7b8c", edge="#6b7b8c",
    color="white", size=10)
box(ax, 54, 48, 17, 10, "SILVER\nlimpo + deduplicado", face=BLUE, edge=BLUE,
    color="white", size=10)
box(ax, 54, 32, 17, 10, "GOLD\nfatos, dimensões e ML", face=GREEN, edge=GREEN,
    color="white", size=10)
box(ax, 53, 22, 19, 7, "Parquet + Delta Lake\npartição por data • time travel",
    face="#fdf6e3", edge=GOLD, color="#6b5200", size=8, weight="bold")

box(ax, 80, 58, 14, 12, "BI\npainéis", face=GOLD, edge=GOLD, color="white")
box(ax, 80, 28, 14, 12, "Python / R\nmodelos", face=NAVY, edge=NAVY, color="white")

arrow(ax, (21, 64), (30, 64))
arrow(ax, (21, 34), (30, 34))
arrow(ax, (45, 64), (54, 69))
arrow(ax, (45, 34), (54, 66))
arrow(ax, (62.5, 64), (62.5, 58.4))
arrow(ax, (62.5, 48), (62.5, 42.4))
arrow(ax, (71, 40), (80, 62))
arrow(ax, (71, 36), (80, 34))

# faixa de auditoria, isolada na base
ax.add_patch(FancyBboxPatch((4, 6), 92, 8,
                            boxstyle="round,pad=0,rounding_size=1.2",
                            facecolor="#eef2f7", edgecolor="#d5dee8", linewidth=1.2))
ax.text(50, 10, "Auditoria transversal:  run_id  •  versão do código  •  período processado  "
                "•  contagens de entrada/saída  •  versão do dataset",
        ha="center", va="center", fontsize=10.5, fontweight="bold", color=NAVY)

fig.savefig(OUT / "arquitetura_logica.png", facecolor="white")
plt.close(fig)

# ---------------------------------------------------------------- diagrama 2
fig, ax = canvas(12, 6.1333)
ax.text(4, 94, "Modelo dimensional Gold — estrela de vendas", fontsize=19,
        fontweight="bold", color=NAVY, va="center")

box(ax, 36, 34, 28, 24,
    "FACT_SALES\n\ngrão: 1 item do pedido\nquantidade • receita líquida\ncusto • margem • desconto",
    face=NAVY, edge=NAVY, color="white", size=11)

dims = [
    (6, 58, "DIM_DATE\ndata • mês • trimestre • ano"),
    (6, 20, "DIM_CUSTOMER\ncliente • UF • cohort"),
    (72, 58, "DIM_PRODUCT\nSKU • produto • categoria"),
    (72, 20, "DIM_STORE\nloja • cidade • UF"),
]
for x, y, texto in dims:
    box(ax, x, y, 22, 13, texto, face=LIGHT, edge=BLUE, color=NAVY, size=9.5)

box(ax, 40, 70, 20, 11, "DIM_CHANNEL\ne-commerce • loja física",
    face=LIGHT, edge=BLUE, color=NAVY, size=9.5)

arrow(ax, (28, 63), (35.4, 55), color=NAVY)
arrow(ax, (28, 29), (35.4, 39), color=NAVY)
arrow(ax, (72, 63), (64.6, 55), color=NAVY)
arrow(ax, (72, 29), (64.6, 39), color=NAVY)
arrow(ax, (50, 70), (50, 58.4), color=NAVY)

ax.text(50, 10,
        "Dimensões desnormalizadas simplificam filtros e agrupamentos; a fato guarda apenas medidas aditivas no mesmo grão.",
        ha="center", va="center", fontsize=10, color=GREY)

fig.savefig(OUT / "modelo_estrela.png", facecolor="white")
plt.close(fig)

print("diagramas gerados em", OUT)
