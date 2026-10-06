from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import textwrap
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel, Field, model_validator


class MediaExecutionError(RuntimeError):
    """The deterministic media executor could not complete its task."""


class MediaQCError(MediaExecutionError):
    """A rendered file exists but does not satisfy canonical media constraints."""


class CardVideoSpec(BaseModel):
    """Smallest useful local-first short-form content specification."""

    experiment_id: UUID
    hook: str = Field(min_length=3, max_length=180)
    points: list[str] = Field(min_length=1, max_length=6)
    cta: str | None = Field(default=None, max_length=180)
    source_note: str | None = Field(default=None, max_length=240)
    duration_seconds: float = Field(default=12.0, ge=4.0, le=45.0)
    width: int = Field(default=1080, ge=360, le=2160)
    height: int = Field(default=1920, ge=640, le=3840)
    fps: int = Field(default=30, ge=12, le=60)

    @model_validator(mode="after")
    def require_vertical_nine_sixteen(self) -> CardVideoSpec:
        if self.width * 16 != self.height * 9:
            raise ValueError("bootstrap card renderer requires an exact 9:16 canvas")
        return self


class VideoQC(BaseModel):
    width: int
    height: int
    duration_seconds: float
    video_codec: str
    has_video: bool
    has_audio: bool
    black_fraction: float = Field(ge=0.0, le=1.0)
    file_bytes: int


class RenderedCardVideo(BaseModel):
    video_path: Path
    sidecar_path: Path
    sha256: str
    content_key: str
    reused: bool
    qc: VideoQC


class FfmpegCardRenderer:
    """Deterministic zero-cash vertical renderer.

    The renderer intentionally produces a coherent, legible micro-explainer rather
    than a placeholder color clip. It is a bootstrap executor: richer media models
    can later replace the visual adapter without changing the experiment contract.
    """

    version = "0.1"

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir

    def render(self, spec: CardVideoSpec) -> RenderedCardVideo:
        self._require_binary("ffmpeg")
        self._require_binary("ffprobe")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        content_key = self._content_key(spec)
        stem = f"{spec.experiment_id}-{content_key[:16]}"
        video_path = self.output_dir / f"{stem}.mp4"
        sidecar_path = self.output_dir / f"{stem}.json"

        if video_path.exists() and sidecar_path.exists():
            qc = self.inspect(video_path, expected=spec)
            return RenderedCardVideo(
                video_path=video_path,
                sidecar_path=sidecar_path,
                sha256=self._sha256(video_path),
                content_key=content_key,
                reused=True,
                qc=qc,
            )

        with tempfile.TemporaryDirectory(prefix="bm-card-", dir=self.output_dir) as tmp_name:
            tmp_dir = Path(tmp_name)
            cards = self._cards(spec)
            image_paths = [
                self._render_card(spec, card, index, len(cards), tmp_dir)
                for index, card in enumerate(cards)
            ]
            manifest_path = self._write_concat_manifest(
                image_paths,
                total_duration=spec.duration_seconds,
                directory=tmp_dir,
            )
            temporary_video = tmp_dir / "render.mp4"
            self._encode(
                manifest_path,
                temporary_video,
                duration=spec.duration_seconds,
                fps=spec.fps,
            )
            qc = self.inspect(temporary_video, expected=spec)
            os.replace(temporary_video, video_path)

        digest = self._sha256(video_path)
        metadata: dict[str, Any] = {
            "renderer": "ffmpeg_cards",
            "renderer_version": self.version,
            "experiment_id": str(spec.experiment_id),
            "content_key": content_key,
            "sha256": digest,
            "created_at": datetime.now(UTC).isoformat(),
            "spec": spec.model_dump(mode="json"),
            "qc": qc.model_dump(mode="json"),
        }
        temporary_sidecar = sidecar_path.with_suffix(".json.part")
        temporary_sidecar.write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        os.replace(temporary_sidecar, sidecar_path)

        return RenderedCardVideo(
            video_path=video_path,
            sidecar_path=sidecar_path,
            sha256=digest,
            content_key=content_key,
            reused=False,
            qc=qc,
        )

    def inspect(self, video_path: Path, *, expected: CardVideoSpec | None = None) -> VideoQC:
        if not video_path.exists() or video_path.stat().st_size < 1024:
            raise MediaQCError("media file is missing or too small to be a valid canonical asset")

        probe = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_streams",
                "-show_format",
                "-of",
                "json",
                str(video_path),
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if probe.returncode != 0:
            raise MediaQCError(f"ffprobe could not decode media: {probe.stderr.strip()[:300]}")

        try:
            payload = json.loads(probe.stdout)
        except json.JSONDecodeError as exc:
            raise MediaQCError("ffprobe returned invalid JSON") from exc

        streams = payload.get("streams", [])
        video_streams = [stream for stream in streams if stream.get("codec_type") == "video"]
        audio_streams = [stream for stream in streams if stream.get("codec_type") == "audio"]
        if not video_streams:
            raise MediaQCError("canonical content asset has no video stream")

        stream = video_streams[0]
        width = int(stream.get("width", 0))
        height = int(stream.get("height", 0))
        duration = self._duration(payload, stream)
        if duration <= 0:
            raise MediaQCError("canonical content asset has no measurable duration")

        if expected is not None:
            if (width, height) != (expected.width, expected.height):
                raise MediaQCError(
                    f"unexpected dimensions {width}x{height}; "
                    f"expected {expected.width}x{expected.height}"
                )
            if abs(duration - expected.duration_seconds) > 1.0:
                raise MediaQCError(
                    f"unexpected duration {duration:.2f}s; "
                    f"expected about {expected.duration_seconds:.2f}s"
                )

        black_fraction = self._black_fraction(video_path, duration)
        if black_fraction >= 0.80:
            raise MediaQCError(
                f"asset is effectively black ({black_fraction:.1%} of duration detected)"
            )

        return VideoQC(
            width=width,
            height=height,
            duration_seconds=duration,
            video_codec=str(stream.get("codec_name", "unknown")),
            has_video=True,
            has_audio=bool(audio_streams),
            black_fraction=black_fraction,
            file_bytes=video_path.stat().st_size,
        )

    @staticmethod
    def _duration(payload: dict[str, Any], stream: dict[str, Any]) -> float:
        candidates = [
            payload.get("format", {}).get("duration"),
            stream.get("duration"),
        ]
        for value in candidates:
            if value is None:
                continue
            try:
                return float(value)
            except (TypeError, ValueError):
                continue
        return 0.0

    @staticmethod
    def _black_fraction(video_path: Path, duration: float) -> float:
        result = subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-nostats",
                "-i",
                str(video_path),
                "-vf",
                "blackdetect=d=0.4:pix_th=0.10:pic_th=0.98",
                "-an",
                "-f",
                "null",
                "-",
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )
        matches = re.findall(r"black_duration:([0-9]+(?:\.[0-9]+)?)", result.stderr)
        black_seconds = sum(float(value) for value in matches)
        return min(max(black_seconds / duration, 0.0), 1.0)

    @staticmethod
    def _cards(spec: CardVideoSpec) -> list[tuple[str, str]]:
        cards: list[tuple[str, str]] = [(spec.hook, "")]
        cards.extend((f"Ponto {index}", point) for index, point in enumerate(spec.points, start=1))
        if spec.cta:
            cards.append((spec.cta, spec.source_note or ""))
        elif spec.source_note:
            cards.append(("Fonte / contexto", spec.source_note))
        return cards

    @staticmethod
    def _font(size: int, *, bold: bool) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        filename = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
        candidates = [
            Path("/usr/share/fonts/truetype/dejavu") / filename,
            Path("/usr/share/fonts/dejavu") / filename,
        ]
        for candidate in candidates:
            if candidate.exists():
                return ImageFont.truetype(str(candidate), size=size)
        try:
            return ImageFont.truetype(filename, size=size)
        except OSError:
            return ImageFont.load_default(size=size)

    def _render_card(
        self,
        spec: CardVideoSpec,
        card: tuple[str, str],
        index: int,
        total: int,
        directory: Path,
    ) -> Path:
        backgrounds = [
            (35, 55, 90),
            (67, 45, 90),
            (35, 82, 78),
            (92, 57, 38),
        ]
        image = Image.new("RGB", (spec.width, spec.height), backgrounds[index % len(backgrounds)])
        draw = ImageDraw.Draw(image)
        margin = int(spec.width * 0.08)
        heading_font = self._font(max(42, spec.width // 13), bold=True)
        body_font = self._font(max(30, spec.width // 23), bold=False)
        small_font = self._font(max(22, spec.width // 34), bold=False)

        progress_width = int((spec.width - 2 * margin) * ((index + 1) / total))
        draw.rounded_rectangle(
            (margin, margin, margin + progress_width, margin + 14),
            radius=7,
            fill=(245, 245, 245),
        )

        heading, body = card
        y = int(spec.height * 0.24)
        for line in textwrap.wrap(heading, width=24) or [heading]:
            draw.text((margin, y), line, font=heading_font, fill=(255, 255, 255))
            y += int(spec.height * 0.055)

        if body:
            y += int(spec.height * 0.045)
            for line in textwrap.wrap(body, width=38) or [body]:
                draw.text((margin, y), line, font=body_font, fill=(238, 242, 247))
                y += int(spec.height * 0.035)

        footer = f"Business Master probe · {index + 1}/{total}"
        draw.text(
            (margin, int(spec.height * 0.90)),
            footer,
            font=small_font,
            fill=(220, 226, 234),
        )

        path = directory / f"slide-{index:03d}.png"
        image.save(path, format="PNG", optimize=True)
        return path

    @staticmethod
    def _write_concat_manifest(
        image_paths: list[Path],
        *,
        total_duration: float,
        directory: Path,
    ) -> Path:
        duration = total_duration / len(image_paths)
        lines: list[str] = []
        for path in image_paths:
            escaped = str(path.resolve()).replace("'", "'\\''")
            lines.append(f"file '{escaped}'")
            lines.append(f"duration {duration:.6f}")
        final_path = str(image_paths[-1].resolve()).replace("'", "'\\''")
        lines.append(f"file '{final_path}'")
        manifest = directory / "slides.ffconcat"
        manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return manifest

    @staticmethod
    def _encode(manifest: Path, output: Path, *, duration: float, fps: int) -> None:
        command = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(manifest),
            "-vf",
            f"fps={fps},format=yuv420p",
            "-t",
            f"{duration:.6f}",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "22",
            "-movflags",
            "+faststart",
            str(output),
        ]
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=180,
        )
        if result.returncode != 0:
            raise MediaExecutionError(f"ffmpeg render failed: {result.stderr.strip()[:500]}")

    @staticmethod
    def _content_key(spec: CardVideoSpec) -> str:
        serialized = json.dumps(
            spec.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        return hashlib.sha256(serialized).hexdigest()

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest()

    @staticmethod
    def _require_binary(name: str) -> None:
        if shutil.which(name) is None:
            raise MediaExecutionError(f"required executable is not available: {name}")
