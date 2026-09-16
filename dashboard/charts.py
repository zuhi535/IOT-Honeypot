"""
Matplotlib grafikonok a sötét témájú Flask dashboardhoz.

Minden függvény egy PNG képet ad vissza bytes formában (io.BytesIO),
amit a Flask route-ok közvetlenül a válaszba tudnak tenni.
"""

import io

import matplotlib
matplotlib.use("Agg")  # nincs szükség kijelzőre, csak fájlba/memóriába renderelünk

import matplotlib.pyplot as plt

from honeypot.database import get_topic_counts, get_events_over_time


# --- Sötét téma színei (illeszkedik a dashboard CSS-éhez) -----------------
BG_COLOR = "#12141c"        # a card/panel háttere
FG_COLOR = "#e5e7eb"        # szöveg
GRID_COLOR = "#2a2e3d"      # rácsvonalak
ACCENT_COLORS = [
    "#8b5cf6",  # lila
    "#22d3ee",  # cián
    "#f472b6",  # pink
    "#facc15",  # sárga
    "#34d399",  # zöld
    "#fb923c",  # narancs
    "#60a5fa",  # kék
    "#f87171",  # piros
]


def _dark_figure(figsize=(6, 4)):
    """Létrehoz egy Figure/Axes párt, ami már be van állítva sötét témára."""
    fig, ax = plt.subplots(figsize=figsize, dpi=120)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    ax.tick_params(colors=FG_COLOR, labelsize=9)
    ax.xaxis.label.set_color(FG_COLOR)
    ax.yaxis.label.set_color(FG_COLOR)
    ax.title.set_color(FG_COLOR)

    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)

    return fig, ax


def _fig_to_png_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


def bar_chart_topics():
    """Oszlopdiagram: mely topicokra érkezett a legtöbb üzenet."""
    data = get_topic_counts()

    fig, ax = _dark_figure()

    if not data:
        ax.text(0.5, 0.5, "Nincs adat", color=FG_COLOR, ha="center", va="center")
        ax.axis("off")
        return _fig_to_png_bytes(fig)

    topics = [row[0] for row in data]
    counts = [row[1] for row in data]

    bars = ax.bar(
        topics,
        counts,
        color=[ACCENT_COLORS[i % len(ACCENT_COLORS)] for i in range(len(topics))],
        edgecolor=BG_COLOR,
    )

    ax.set_title("Üzenetek topiconként")
    ax.set_ylabel("Üzenetek száma")
    ax.grid(axis="y", color=GRID_COLOR, linewidth=0.6, alpha=0.6)
    ax.set_axisbelow(True)
    plt.setp(ax.get_xticklabels(), rotation=25, ha="right")

    for bar, count in zip(bars, counts):
        ax.annotate(
            str(count),
            xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            color=FG_COLOR,
            fontsize=8,
        )

    fig.tight_layout()
    return _fig_to_png_bytes(fig)


def pie_chart_topics():
    """Kördiagram: topicok megoszlása."""
    data = get_topic_counts()

    fig, ax = _dark_figure(figsize=(5, 5))

    if not data:
        ax.text(0.5, 0.5, "Nincs adat", color=FG_COLOR, ha="center", va="center")
        ax.axis("off")
        return _fig_to_png_bytes(fig)

    topics = [row[0] for row in data]
    counts = [row[1] for row in data]

    wedges, _texts, autotexts = ax.pie(
        counts,
        labels=topics,
        autopct="%1.0f%%",
        colors=[ACCENT_COLORS[i % len(ACCENT_COLORS)] for i in range(len(topics))],
        textprops={"color": FG_COLOR, "fontsize": 9},
        wedgeprops={"edgecolor": BG_COLOR, "linewidth": 1.5},
    )
    for autotext in autotexts:
        autotext.set_color(BG_COLOR)
        autotext.set_fontweight("bold")

    ax.set_title("Topicok megoszlása")
    ax.axis("equal")

    fig.tight_layout()
    return _fig_to_png_bytes(fig)


def line_chart_events():
    """Vonaldiagram: események időbeli alakulása (naponta)."""
    data = get_events_over_time()

    fig, ax = _dark_figure()

    if not data:
        ax.text(0.5, 0.5, "Nincs adat", color=FG_COLOR, ha="center", va="center")
        ax.axis("off")
        return _fig_to_png_bytes(fig)

    days = [row[0] for row in data]
    counts = [row[1] for row in data]

    ax.plot(
        days,
        counts,
        marker="o",
        color=ACCENT_COLORS[1],
        linewidth=2,
        markerfacecolor=ACCENT_COLORS[0],
        markeredgecolor=BG_COLOR,
    )
    ax.fill_between(days, counts, color=ACCENT_COLORS[1], alpha=0.15)

    ax.set_title("Események időbeli alakulása")
    ax.set_ylabel("Üzenetek száma")
    ax.grid(color=GRID_COLOR, linewidth=0.6, alpha=0.6)
    ax.set_axisbelow(True)
    plt.setp(ax.get_xticklabels(), rotation=25, ha="right")

    fig.tight_layout()
    return _fig_to_png_bytes(fig)
