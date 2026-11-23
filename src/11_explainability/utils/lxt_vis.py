import html

import matplotlib.pyplot as plt
import numpy as np
from IPython.display import HTML, display


def visualize_lxt_tokens(tokens, relevance, top_k=10, predicted_token=None):
    """Render an inline HTML token heatmap and a top-k bar chart for LXT relevance."""
    rel = np.asarray(relevance, dtype=float)
    if rel.size == 0 or len(tokens) != len(rel):
        raise ValueError("tokens and relevance must be non-empty and have the same length.")

    max_abs = np.max(np.abs(rel)) + 1e-8
    norm = rel / max_abs
    k = min(top_k, len(rel))
    top_indices = set(np.argsort(-np.abs(rel))[:k].tolist())

    # 1. Inline HTML token heatmap
    spans = []
    for i, (tok, score, n_score) in enumerate(zip(tokens, rel, norm)):
        alpha = min(0.85, max(0.06, abs(n_score) * 0.85))
        bg = f"rgba(220, 53, 69, {alpha:.2f})" if n_score >= 0 else f"rgba(13, 110, 253, {alpha:.2f})"
        fg = "#fff" if alpha > 0.55 else "#111"
        border = "2px solid #111" if i in top_indices else "1px solid rgba(0,0,0,0.08)"
        escaped = html.escape(tok).replace(" ", "&nbsp;")
        spans.append(
            f'<span title="idx {i}: {score:+.4f}" '
            f'style="display:inline-block;margin:2px;padding:2px 5px;border-radius:4px;'
            f'background:{bg};color:{fg};border:{border};font-family:monospace;font-size:13px;">'
            f"{escaped}</span>"
        )

    header = f"LXT Token Relevance (red = positive, blue = negative, bold border = top-{k})"
    if predicted_token is not None:
        header += f" | Predicted next token: <code>{html.escape(repr(predicted_token))}</code>"

    display(
        HTML(
            '<div style="font-family:sans-serif;line-height:1.9;padding:10px;'
            'border:1px solid #ddd;border-radius:6px;background:#fafafa;">'
            f'<div style="font-size:13px;font-weight:600;margin-bottom:6px;color:#333;">{header}</div>'
            f'<div>{"".join(spans)}</div></div>'
        )
    )

    # 2. Top-k most important tokens bar chart
    order = np.argsort(-np.abs(rel))[:k][::-1]
    labels = [f"{i}: {tokens[i]!r}" for i in order]
    vals = rel[order]
    colors = ["#dc3545" if v >= 0 else "#0d6efd" for v in vals]

    fig, ax = plt.subplots(figsize=(8, max(3, 0.4 * len(order))))
    bars = ax.barh(labels, vals, color=colors)
    ax.axvline(0, color="#333", linewidth=0.8)
    ax.set_xlabel("Normalized LXT Relevance")
    ax.set_title(f"Top {len(order)} Most Important Tokens (by |relevance|)")
    ax.bar_label(bars, fmt="%+.3f", padding=4, fontsize=9)
    ax.margins(x=0.18)
    plt.tight_layout()
    plt.show()
