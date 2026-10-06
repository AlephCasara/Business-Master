from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from uuid import uuid4

import pytest

from business_master.media.ffmpeg_cards import (
    CardVideoSpec,
    FfmpegCardRenderer,
    MediaQCError,
)


requires_ffmpeg = pytest.mark.skipif(
    shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None,
    reason="ffmpeg/ffprobe are required for deterministic media tests",
)


@requires_ffmpeg
def test_renderer_produces_vertical_asset_sidecar_and_reuses_canonical_output(
    tmp_path: Path,
) -> None:
    renderer = FfmpegCardRenderer(tmp_path)
    spec = CardVideoSpec(
        experiment_id=uuid4(),
        hook="Por que faturamento não é lucro?",
        points=[
            "A receita ainda precisa pagar produto, taxas, frete e aquisição.",
            "Compare experimentos pela contribuição e pelo capital que fica travado.",
        ],
        cta="Meça a economia antes de escalar.",
        source_note="Micro-explicador de teste do Business Master.",
        duration_seconds=4.0,
        width=360,
        height=640,
        fps=24,
    )

    first = renderer.render(spec)
    second = renderer.render(spec)

    assert first.video_path.exists()
    assert first.sidecar_path.exists()
    assert first.qc.width == 360
    assert first.qc.height == 640
    assert first.qc.duration_seconds > 3.0
    assert first.qc.black_fraction < 0.80
    assert first.sha256 == second.sha256
    assert first.video_path == second.video_path
    assert not first.reused
    assert second.reused

    sidecar = json.loads(first.sidecar_path.read_text(encoding="utf-8"))
    assert sidecar["experiment_id"] == str(spec.experiment_id)
    assert sidecar["content_key"] == first.content_key
    assert sidecar["sha256"] == first.sha256


@requires_ffmpeg
def test_qc_rejects_corrupt_asset(tmp_path: Path) -> None:
    renderer = FfmpegCardRenderer(tmp_path)
    corrupt = tmp_path / "corrupt.mp4"
    corrupt.write_bytes(b"not a video")

    with pytest.raises(MediaQCError):
        renderer.inspect(corrupt)


@requires_ffmpeg
def test_qc_rejects_effectively_black_asset(tmp_path: Path) -> None:
    renderer = FfmpegCardRenderer(tmp_path)
    black = tmp_path / "black.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=black:s=360x640:d=2:r=24",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(black),
        ],
        check=True,
        timeout=60,
    )

    with pytest.raises(MediaQCError, match="effectively black"):
        renderer.inspect(black)
