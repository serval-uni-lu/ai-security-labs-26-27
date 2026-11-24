"""
Visualization helpers for Token Activation Map (TAM) VLM explanations.
Extracted from Part 6 of xai_lab.ipynb for easy inspection and reuse.
"""

import html
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import torch
import torch.nn.functional as F
from PIL import Image
from IPython.display import HTML, display


def decode_tam_tokens(tokens_or_ids, processor=None):
    """
    Normalize TAM token outputs into a flat list of readable strings.
    Handles nested lists like [[id1, id2, ...]] returned by `TAM(..., return_components=True)`,
    flat lists of token IDs, or already-decoded token strings.
    """
    if tokens_or_ids is None:
        return []
    # Unwrap outer batch list if present (e.g. [[101, 102, ...]])
    if isinstance(tokens_or_ids, (list, tuple)) and len(tokens_or_ids) > 0 and isinstance(tokens_or_ids[0], (list, tuple)):
        tokens_or_ids = tokens_or_ids[0]

    decoded = []
    for tok in tokens_or_ids:
        if isinstance(tok, str):
            s = tok
        elif processor is not None:
            tok_fn = getattr(processor, "tokenizer", processor)
            s = tok_fn.decode([int(tok)])
        else:
            s = str(tok)
        # Clean common subword space markers (SentencePiece / BPE)
        s = s.replace("▁", " ").replace("Ġ", " ")
        decoded.append(s)
    return decoded


def _prepare_rgb_image(image):
    """Convert a PIL Image or NumPy array into a float32 RGB array in [0, 1]."""
    if isinstance(image, Image.Image):
        return np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
    arr = np.asarray(image, dtype=np.float32)
    if arr.max() > 1.0:
        arr = arr / 255.0
    return np.clip(arr, 0.0, 1.0)


def _upsample_tam_map(img_map, target_hw):
    """
    Resize a 2D (H_g, W_g) or 3D (num_tiles, H_g, W_g) TAM activation map
    to (target_H, target_W) using bilinear interpolation, normalized to [0, 1].
    """
    arr = np.asarray(img_map, dtype=np.float32)
    if arr.ndim == 3:
        # For multi-tile VLMs (e.g., InternVL), use the last (global thumbnail) tile
        arr = arr[-1]
    if arr.ndim != 2:
        raise ValueError(f"Expected 2D or 3D img_map, got shape {arr.shape}")

    tensor_2d = torch.from_numpy(arr).unsqueeze(0).unsqueeze(0)  # (1, 1, H_g, W_g)
    upsampled = F.interpolate(
        tensor_2d, size=target_hw, mode="bilinear", align_corners=False
    ).squeeze().numpy()

    min_v, max_v = upsampled.min(), upsampled.max()
    if max_v > min_v:
        upsampled = (upsampled - min_v) / (max_v - min_v)
    else:
        upsampled = np.zeros_like(upsampled)
    return upsampled


def plot_tam_image_heatmap(
    img_map,
    image,
    title="TAM Visual Attribution",
    alpha=0.5,
    cmap="jet",
    ax=None,
):
    """
    Plot TAM spatial attribution over the input image.
    If `ax` is None, creates a 3-panel figure: Original | Heatmap | Overlay.
    If `ax` is provided, draws the blended overlay directly onto `ax`.
    """
    rgb = _prepare_rgb_image(image)
    h, w = rgb.shape[:2]
    heatmap = _upsample_tam_map(img_map, (h, w))

    if ax is not None:
        ax.imshow(rgb)
        im = ax.imshow(heatmap, cmap=cmap, alpha=alpha, vmin=0.0, vmax=1.0)
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.axis("off")
        return im

    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    axes[0].imshow(rgb)
    axes[0].set_title("Original Image", fontsize=11)
    axes[0].axis("off")

    im1 = axes[1].imshow(heatmap, cmap=cmap, vmin=0.0, vmax=1.0)
    axes[1].set_title("TAM Activation Map", fontsize=11)
    axes[1].axis("off")
    fig.colorbar(im1, ax=axes[1], fraction=0.046, pad=0.04)

    axes[2].imshow(rgb)
    axes[2].imshow(heatmap, cmap=cmap, alpha=alpha, vmin=0.0, vmax=1.0)
    axes[2].set_title(title, fontsize=11, fontweight="bold")
    axes[2].axis("off")

    fig.tight_layout()
    plt.show()
    return fig


DEFAULT_EXCLUDED_TEXT_TOKENS = {
    "<|image_pad|>",
    "<|im_start|>",
    "<|im_end|>",
    "<think>",
    "</think>",
    "<|vision_pad|>",
    "<|video_pad|>",
    "<|vision_start|>",
    "<|vision_end|>",
    "<image>",
    "<IMG_CONTEXT>",
    "<img>",
    "</img>",
    "<|img|>",
}


def filter_tam_text_tokens(tokens, scores, prompt_len=None, exclude_tokens=None):
    """
    Remove vision/image placeholder tokens (e.g., `<|image_pad|>`) from TAM text
    tokens and scores while keeping `prompt_len` aligned.
    """
    scores = np.asarray(scores, dtype=np.float32).flatten()
    n = min(len(tokens), len(scores))
    extra = set(exclude_tokens) if exclude_tokens else set()
    blocked = DEFAULT_EXCLUDED_TEXT_TOKENS | extra

    kept_tokens, kept_scores = [], []
    new_prompt_len = 0 if prompt_len is not None else None

    for i in range(n):
        tok = tokens[i]
        stripped = tok.strip()
        if (
            stripped in blocked
            or "image_pad" in stripped
            or "vision_pad" in stripped
        ):
            continue
        kept_tokens.append(tok)
        kept_scores.append(scores[i])
        if prompt_len is not None and i < prompt_len:
            new_prompt_len += 1

    return kept_tokens, np.asarray(kept_scores, dtype=np.float32), new_prompt_len


def plot_tam_text_relevance(
    tokens,
    scores,
    prompt_len=None,
    title="TAM Text Token Relevance",
    top_k=None,
    exclude_tokens=None,
    ax=None,
):
    """
    Plot a bar chart of TAM text token relevance scores (excluding image pad tokens).
    Distinguishes prompt tokens (steel blue) from previously generated answer tokens (orange).
    """
    tokens, scores, prompt_len = filter_tam_text_tokens(
        tokens, scores, prompt_len=prompt_len, exclude_tokens=exclude_tokens
    )
    n = len(tokens)

    if n == 0:
        if ax is not None:
            ax.text(0.5, 0.5, "No text tokens to display", ha="center", va="center")
            ax.axis("off")
        return None

    # Optionally keep only top_k most relevant tokens while preserving order
    indices = np.arange(n)
    if top_k is not None and n > top_k:
        top_idx = np.sort(np.argsort(-np.abs(scores))[:top_k])
        indices = top_idx
        tokens = [tokens[i] for i in indices]
        scores = scores[indices]

    colors = []
    for orig_i in indices:
        if prompt_len is not None and orig_i >= prompt_len:
            colors.append("#e67e22")  # Answer context token
        else:
            colors.append("#2980b9")  # Prompt token

    standalone = ax is None
    if standalone:
        fig, ax = plt.subplots(figsize=(max(6, len(tokens) * 0.55), 3.2))

    x = np.arange(len(tokens))
    ax.bar(x, scores, color=colors, edgecolor="black", linewidth=0.5, alpha=0.88)
    ax.set_xticks(x)
    ax.set_xticklabels([repr(t)[1:-1] for t in tokens], rotation=40, ha="right", fontsize=9)
    ax.set_ylabel("Normalized Relevance")
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_ylim(0, max(1.05, float(scores.max()) * 1.12))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.35)

    if prompt_len is not None:
        from matplotlib.patches import Patch
        legend_handles = [
            Patch(facecolor="#2980b9", edgecolor="black", label="Prompt token"),
            Patch(facecolor="#e67e22", edgecolor="black", label="Previously generated answer"),
        ]
        ax.legend(handles=legend_handles, loc="upper right", fontsize=8, frameon=True)

    if standalone:
        fig.tight_layout()
        plt.show()
        return fig
    return ax


def display_tam_text_html(
    tokens, scores, explained_token=None, prompt_len=None, exclude_tokens=None, cmap_name="YlOrRd"
):
    """
    Render inline color-highlighted tokens in Jupyter using HTML (no LaTeX required),
    excluding image placeholder tokens such as `<|image_pad|>`.
    """
    tokens, scores, prompt_len = filter_tam_text_tokens(
        tokens, scores, prompt_len=prompt_len, exclude_tokens=exclude_tokens
    )
    n = len(tokens)

    max_s = float(scores.max()) if n > 0 and scores.max() > 0 else 1.0
    norm_scores = np.clip(scores / max_s, 0.0, 1.0)
    cmap = plt.get_cmap(cmap_name)

    spans = []
    for i, (tok, s) in enumerate(zip(tokens, norm_scores)):
        if prompt_len is not None and i == prompt_len:
            spans.append(
                "<span style='margin:0 6px; padding:2px 6px; background:#eee; "
                "border-radius:4px; font-weight:bold; color:#333;'>| Answer:</span>"
            )
        r, g, b, _ = cmap(float(s))
        bg = f"rgb({int(r*255)}, {int(g*255)}, {int(b*255)})"
        fg = "#ffffff" if s > 0.65 else "#111111"
        safe_tok = html.escape(tok).replace(" ", "&nbsp;")
        spans.append(
            f"<span title='score={scores[i]:.3f}' style='background:{bg}; color:{fg}; "
            f"padding:2px 4px; margin:2px; border-radius:4px; display:inline-block; "
            f"font-family:monospace; font-size:13px;'>{safe_tok}</span>"
        )

    if explained_token is not None:
        safe_exp = html.escape(str(explained_token)).replace(" ", "&nbsp;")
        spans.append(
            f"<span style='background:#111111; color:#ffffff; padding:2px 6px; margin:2px 4px; "
            f"border-radius:4px; display:inline-block; font-family:monospace; font-size:13px; "
            f"font-weight:bold;'>[Explained: {safe_exp}]</span>"
        )

    html_block = (
        "<div style='border:1px solid #ddd; border-radius:8px; padding:10px; "
        "background:#fafafa; line-height:1.9;'>"
        "<div style='font-size:12px; color:#555; margin-bottom:6px;'>"
        "<b>TAM Text Relevance</b> (darker = higher attribution; hover for exact score):</div>"
        + "".join(spans)
        + "</div>"
    )
    display(HTML(html_block))


def visualize_tam_explanation(
    tam_out,
    image,
    processor=None,
    explained_token=None,
    alpha=0.5,
    cmap="jet",
    top_k_tokens=20,
    exclude_tokens=None,
    show_html=True,
):
    """
    Unified visualization for a `TAM(..., return_components=True)` output dictionary.
    Displays:
      1. Side-by-side Original Image, TAM Spatial Overlay, and Token Relevance Bar Chart.
      2. Inline HTML token highlighting in the notebook output.
    """
    prompt_toks = decode_tam_tokens(tam_out.get("prompt_tokens"), processor)
    answer_toks = decode_tam_tokens(tam_out.get("answer_tokens"), processor)
    all_toks = prompt_toks + answer_toks
    txt_scores = tam_out.get("txt_scores_norm", np.array([]))

    fig = plt.figure(figsize=(14, 4.8))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.0, 1.4])

    ax_orig = fig.add_subplot(gs[0, 0])
    ax_orig.imshow(_prepare_rgb_image(image))
    ax_orig.set_title("Input Image", fontsize=11)
    ax_orig.axis("off")

    ax_img = fig.add_subplot(gs[0, 1])
    img_title = f"TAM Visual Map ({explained_token})" if explained_token else "TAM Visual Map"
    im = plot_tam_image_heatmap(tam_out["img_map_norm"], image, title=img_title, alpha=alpha, cmap=cmap, ax=ax_img)
    fig.colorbar(im, ax=ax_img, fraction=0.046, pad=0.04)

    ax_txt = fig.add_subplot(gs[0, 2])
    plot_tam_text_relevance(
        all_toks,
        txt_scores,
        prompt_len=len(prompt_toks),
        title="Context Token Relevance",
        top_k=top_k_tokens,
        exclude_tokens=exclude_tokens,
        ax=ax_txt,
    )

    fig.tight_layout()
    plt.show()

    if show_html and len(all_toks) > 0 and len(txt_scores) > 0:
        display_tam_text_html(
            all_toks,
            txt_scores,
            explained_token=explained_token,
            prompt_len=len(prompt_toks),
            exclude_tokens=exclude_tokens,
        )
    return fig


def compare_tam_across_tokens(tam_outputs, image, token_labels, alpha=0.5, cmap="jet"):
    """
    Compare TAM visual heatmaps across multiple generated answer tokens in a single row.
    """
    n = len(tam_outputs)
    fig, axes = plt.subplots(1, n + 1, figsize=(3.6 * (n + 1), 3.6))
    axes[0].imshow(_prepare_rgb_image(image))
    axes[0].set_title("Original Image", fontsize=11)
    axes[0].axis("off")

    for i, (tam_out, label) in enumerate(zip(tam_outputs, token_labels)):
        plot_tam_image_heatmap(
            tam_out["img_map_norm"],
            image,
            title=f"Token: {label!r}",
            alpha=alpha,
            cmap=cmap,
            ax=axes[i + 1],
        )

    fig.suptitle("Token-by-Token Visual Grounding (TAM)", fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    plt.show()
    return fig


# --- Template: Running TAM on a real Hugging Face VLM (GPU) ---
# Uncomment and adapt `model_id` / `special_ids` for your VLM (e.g., Qwen2-VL or LLaVA).
"""
from transformers import AutoProcessor, AutoModelForVision2Seq
from tam import TAM

model_id = "Qwen/Qwen2-VL-2B-Instruct"  # or your local/cached VLM
processor = AutoProcessor.from_pretrained(model_id)
vlm = AutoModelForVision2Seq.from_pretrained(model_id, torch_dtype=torch.bfloat16, device_map="auto")

# 1. Prepare multimodal inputs and generate with `output_logits=True, return_dict_in_generate=True`
#    (Refer to `tam.TAM` docstring for `special_ids` and `logit_list` formatting.)
# 2. Call TAM with `return_components=True` (no xelatex needed):
img_scores_list = []
tam_out = TAM(
    tokens=full_token_ids,
    vision_shape=(grid_h, grid_w),
    logit_list=logit_list,
    special_ids=special_ids,
    vision_input=raw_image,
    processor=processor,
    save_fn="",
    target_token=round_idx,
    img_scores_list=img_scores_list,
    eval_only=False,
    return_components=True,
)

# 3. Visualize in the notebook:
visualize_tam_explanation(
    tam_out,
    image=raw_image,
    processor=processor,
    explained_token=processor.tokenizer.decode([full_token_ids[-1]]),
)
"""


if __name__ == "__main__":
    # --- Runnable Demo (works on CPU/GPU without downloading a 7B VLM) ---
    # Simulates the exact dictionary structure returned by `tam.TAM(..., return_components=True)`
    rng = np.random.default_rng(42)
    demo_img = Image.new("RGB", (224, 224), color=(235, 240, 245))
    # Draw two simple colored regions (e.g., a "red car" on left, "blue sign" on right)
    demo_arr = np.array(demo_img)
    demo_arr[110:180, 30:110] = [200, 50, 50]    # red box (left-bottom)
    demo_arr[40:100, 140:200] = [40, 90, 200]    # blue box (right-top)
    demo_img = Image.fromarray(demo_arr)

    grid_h, grid_w = 16, 16
    yy, xx = np.mgrid[0:grid_h, 0:grid_w]

    # Simulated TAM map focusing on the red box for token "red"
    map_red = np.exp(-((yy - 10.5) ** 2 + (xx - 5.0) ** 2) / 6.0)
    map_red = (map_red / map_red.max() * 255).astype(np.uint8)

    # Simulated TAM map focusing on the blue box for token "sign"
    map_sign = np.exp(-((yy - 5.0) ** 2 + (xx - 12.0) ** 2) / 5.5)
    map_sign = (map_sign / map_sign.max() * 255).astype(np.uint8)

    tam_out_red = {
        "img_map_norm": map_red,
        "prompt_tokens": [["What", " color", " is", " the", " object", " on", " the", " left", "?"]],
        "answer_tokens": [["The", " object", " is"]],
        "txt_scores_norm": np.array([0.12, 0.85, 0.15, 0.10, 0.42, 0.18, 0.08, 0.78, 0.05, 0.14, 0.35, 0.22]),
    }

    tam_out_sign = {
        "img_map_norm": map_sign,
        "prompt_tokens": [["What", " color", " is", " the", " object", " on", " the", " left", "?"]],
        "answer_tokens": [["The", " object", " is", " red", ",", " next", " to", " a", " blue"]],
        "txt_scores_norm": np.array([0.10, 0.25, 0.10, 0.08, 0.30, 0.12, 0.05, 0.15, 0.04, 0.10, 0.28, 0.15, 0.20, 0.05, 0.35, 0.18, 0.12, 0.82]),
    }

    print("1) Single-token unified TAM explanation:")
    visualize_tam_explanation(tam_out_red, demo_img, explained_token="red")

    print("2) Multi-token comparison across generated answer tokens:")
    compare_tam_across_tokens([tam_out_red, tam_out_sign], demo_img, token_labels=["red", "sign"])
