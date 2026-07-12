"""Research-grade evaluation utilities for English-Twi translation.

Reports the standard low-resource MT metric triad:
    - sacreBLEU (corpus-level, with reproducibility signature)
    - chrF++ (character n-gram F-score with word_order=2)
    - COMET-22 (Unbabel/wmt22-comet-da; reference-based neural metric)

Plus paired bootstrap resampling for statistical significance — the WMT
convention reviewers expect for low-resource MT papers.
"""

import random
from typing import Iterable

import numpy as np
import sacrebleu
import torch
from comet import download_model, load_from_checkpoint
from transformers import PreTrainedModel, PreTrainedTokenizerBase


COMET_MODEL_ID = "Unbabel/wmt22-comet-da"


def _strip_pads(tokens: list[int], pad_id: int) -> list[int]:
    return [t for t in tokens if t != pad_id and t != -100]


def compute_chrf_bleu(eval_pred, tokenizer: PreTrainedTokenizerBase) -> dict:
    """Trainer ``compute_metrics`` callback.

    Decodes predictions and labels with the tokenizer, then returns corpus-level
    chrF++ and BLEU. COMET is intentionally omitted here because it requires a
    GPU-resident model and is too slow to run on every evaluation step; full
    COMET scoring happens once at the end via :func:`evaluate_translation`.
    """
    preds, labels = eval_pred
    if isinstance(preds, tuple):
        preds = preds[0]

    pad_id = tokenizer.pad_token_id
    labels = np.where(labels != -100, labels, pad_id)

    decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

    decoded_preds = [p.strip() for p in decoded_preds]
    decoded_labels = [[l.strip()] for l in decoded_labels]  # sacrebleu wants list-of-refs

    bleu = sacrebleu.corpus_bleu(decoded_preds, list(zip(*decoded_labels)))
    chrf = sacrebleu.corpus_chrf(decoded_preds, list(zip(*decoded_labels)), word_order=2)

    return {"bleu": bleu.score, "chrf": chrf.score}


@torch.no_grad()
def _generate_batched(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizerBase,
    src_texts: list[str],
    *,
    device: str,
    src_lang: str,
    tgt_lang: str,
    batch_size: int,
    max_length: int,
    num_beams: int,
) -> list[str]:
    tokenizer.src_lang = src_lang
    forced_bos = tokenizer.convert_tokens_to_ids(tgt_lang)

    model.eval()
    hyps: list[str] = []
    for start in range(0, len(src_texts), batch_size):
        batch = src_texts[start : start + batch_size]
        enc = tokenizer(
            batch,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=max_length,
        ).to(device)
        out = model.generate(
            **enc,
            forced_bos_token_id=forced_bos,
            max_length=max_length,
            num_beams=num_beams,
        )
        hyps.extend(tokenizer.batch_decode(out, skip_special_tokens=True))
    return [h.strip() for h in hyps]


def evaluate_translation(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizerBase,
    src_texts: list[str],
    ref_texts: list[str],
    *,
    device: str,
    src_lang: str = "eng_Latn",
    tgt_lang: str = "twi_Latn",
    batch_size: int = 16,
    max_length: int = 128,
    num_beams: int = 4,
    compute_comet: bool = True,
) -> dict:
    """Generate translations and score them with BLEU, chrF++, and COMET-22.

    Returns a dict with corpus scores, sacreBLEU/chrF signature strings (for
    the paper's methods section), per-sentence chrF scores (used by the paired
    bootstrap), and the raw predictions.
    """
    if len(src_texts) != len(ref_texts):
        raise ValueError("src_texts and ref_texts must be the same length")

    hyps = _generate_batched(
        model,
        tokenizer,
        src_texts,
        device=device,
        src_lang=src_lang,
        tgt_lang=tgt_lang,
        batch_size=batch_size,
        max_length=max_length,
        num_beams=num_beams,
    )

    bleu_metric = sacrebleu.BLEU()
    chrf_metric = sacrebleu.CHRF(word_order=2)
    bleu = bleu_metric.corpus_score(hyps, [ref_texts])
    chrf = chrf_metric.corpus_score(hyps, [ref_texts])
    per_sentence_chrf = [
        sacrebleu.sentence_chrf(h, [r], word_order=2).score for h, r in zip(hyps, ref_texts)
    ]

    result = {
        "bleu": bleu.score,
        "bleu_signature": str(bleu_metric.get_signature()),
        "chrf": chrf.score,
        "chrf_signature": str(chrf_metric.get_signature()),
        "per_sentence_chrf": per_sentence_chrf,
        "predictions": hyps,
        "references": ref_texts,
        "sources": src_texts,
        "n_examples": len(src_texts),
    }

    if compute_comet:
        comet_path = download_model(COMET_MODEL_ID)
        comet = load_from_checkpoint(comet_path)
        comet_data = [
            {"src": s, "mt": h, "ref": r} for s, h, r in zip(src_texts, hyps, ref_texts)
        ]
        comet_out = comet.predict(comet_data, batch_size=batch_size, gpus=1 if device == "cuda" else 0)
        result["comet"] = float(comet_out.system_score)
        result["per_sentence_comet"] = [float(x) for x in comet_out.scores]
        result["comet_model"] = COMET_MODEL_ID

    return result


def paired_bootstrap(
    refs: list[str],
    hyps_a: list[str],
    hyps_b: list[str],
    *,
    metric: str = "chrf",
    n_samples: int = 1000,
    seed: int = 42,
) -> dict:
    """Paired bootstrap resampling significance test.

    Tests whether system A's mean per-sentence ``metric`` differs significantly
    from system B's, given the same source sentences. Returns the observed
    delta (A - B), a two-sided p-value, and a 95% confidence interval.

    This is the standard significance test for MT papers (Koehn 2004).
    """
    if not (len(refs) == len(hyps_a) == len(hyps_b)):
        raise ValueError("refs, hyps_a, hyps_b must all be the same length")
    if metric != "chrf":
        raise ValueError(f"only metric='chrf' is implemented (got {metric!r})")

    n = len(refs)
    scores_a = np.array(
        [sacrebleu.sentence_chrf(h, [r], word_order=2).score for h, r in zip(hyps_a, refs)]
    )
    scores_b = np.array(
        [sacrebleu.sentence_chrf(h, [r], word_order=2).score for h, r in zip(hyps_b, refs)]
    )
    observed_delta = float(scores_a.mean() - scores_b.mean())

    rng = random.Random(seed)
    deltas = np.empty(n_samples, dtype=np.float64)
    for i in range(n_samples):
        idx = [rng.randrange(n) for _ in range(n)]
        deltas[i] = scores_a[idx].mean() - scores_b[idx].mean()

    # Two-sided p-value: fraction of bootstrap deltas with the opposite sign.
    if observed_delta >= 0:
        p_value = float((deltas <= 0).mean())
    else:
        p_value = float((deltas >= 0).mean())
    p_value = 2 * min(p_value, 1 - p_value)

    ci_low, ci_high = np.quantile(deltas, [0.025, 0.975])

    return {
        "metric": metric,
        "observed_delta": observed_delta,
        "p_value": p_value,
        "ci_low": float(ci_low),
        "ci_high": float(ci_high),
        "n_samples": n_samples,
        "system_a_mean": float(scores_a.mean()),
        "system_b_mean": float(scores_b.mean()),
    }


def print_sample_table(
    sources: Iterable[str],
    references: Iterable[str],
    hypotheses: Iterable[str],
    n: int = 20,
) -> str:
    """Build a markdown table of source/reference/hypothesis triples for the appendix."""
    rows = list(zip(sources, references, hypotheses))[:n]

    def _escape(s: str) -> str:
        return s.replace("|", "\\|").replace("\n", " ")

    out = ["| # | English (source) | Twi (reference) | Twi (model) |", "|---|---|---|---|"]
    for i, (s, r, h) in enumerate(rows, 1):
        out.append(f"| {i} | {_escape(s)} | {_escape(r)} | {_escape(h)} |")
    return "\n".join(out)
