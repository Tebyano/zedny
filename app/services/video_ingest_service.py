import os
import tempfile
import subprocess
from typing import Optional, Tuple

import yt_dlp
from faster_whisper import WhisperModel
from sqlalchemy.orm import Session

from app.client.llm_client.cohere_client import embed_text
from app.client.llm_client.storage_client import StorageClient
from app.models.video_model import Video, VideoChunk


EMBED_MODEL = "embed-english-v3.0"
EMBED_DIMS = 1024

WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL", "small")
_whisper = WhisperModel(WHISPER_MODEL_NAME, device="cpu", compute_type="int8")


def normalize_youtube_url(url: str) -> str:
    url = (url or "").strip()

    for key in ["&list=", "?list=", "&start_radio=", "&index=", "&pp="]:
        if key in url:
            url = url.split(key)[0]

    if "youtu.be/" in url:
        vid = url.split("youtu.be/")[1].split("?")[0].split("&")[0]
        url = f"https://www.youtube.com/watch?v={vid}"

    if "/shorts/" in url:
        vid = url.split("/shorts/")[1].split("?")[0].split("&")[0].split("/")[0]
        url = f"https://www.youtube.com/watch?v={vid}"

    return url


def ydl_base_opts() -> dict:
    opts = {
        "quiet": True,
        "noplaylist": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        },
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"],
            }
        },
    }

    cookies_file = os.getenv("YTDLP_COOKIES_FILE")
    if cookies_file:
        opts["cookiefile"] = cookies_file

    proxy = os.getenv("YTDLP_PROXY")
    if proxy:
        opts["proxy"] = proxy

    return opts


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 150) -> list[str]:
    text = (text or "").strip()
    chunks = []
    i = 0
    while i < len(text):
        j = min(len(text), i + chunk_size)
        chunks.append(text[i:j])
        i = max(j - overlap, j)
    return [c.strip() for c in chunks if c.strip()]


def youtube_metadata(url: str) -> dict:
    url = normalize_youtube_url(url)
    ydl_opts = ydl_base_opts() | {"skip_download": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return {
        "title": info.get("title"),
        "description": info.get("description"),
        "duration": info.get("duration"),
    }


def download_youtube_audio(url: str) -> str:
    url = normalize_youtube_url(url)

    tmpdir = tempfile.mkdtemp(prefix="yt_audio_")
    outtmpl = os.path.join(tmpdir, "audio.%(ext)s")

    ydl_opts = ydl_base_opts() | {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(url, download=True)

    mp3_path = os.path.join(tmpdir, "audio.mp3")
    if not os.path.exists(mp3_path):
        raise RuntimeError("yt-dlp did not produce audio.mp3 (check ffmpeg installation)")
    return mp3_path


def extract_audio_from_video(video_path: str) -> str:
    tmpdir = tempfile.mkdtemp(prefix="vid_audio_")
    audio_path = os.path.join(tmpdir, "audio.mp3")
    subprocess.run(
        ["ffmpeg", "-y", "-i", video_path, "-vn", "-ac", "1", "-ar", "16000", audio_path],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return audio_path


def probe_duration_seconds(video_path: str) -> int | None:
    try:
        out = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                video_path,
            ],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        if not out:
            return None
        return int(float(out))
    except Exception:
        return None


def transcribe(audio_path: str) -> str:
    segments, _info = _whisper.transcribe(audio_path)
    return "\n".join(s.text.strip() for s in segments if getattr(s, "text", "").strip())


def process_video_ingest(
    db: Session,
    video_id,
    user_id,
    source_type: str,
    youtube_url: Optional[str],
    uploaded_video_path: Optional[str],
    uploaded_filename: Optional[str],
) -> Tuple[Video, int]:
    video: Video = db.query(Video).filter(Video.id == video_id, Video.user_id == user_id).first()
    if not video:
        raise RuntimeError("Video row not found")

    try:
        title = None
        description = None
        duration = None
        transcript = None
        storage_url = None
        storage_path = None

        if source_type == "youtube":
            if not youtube_url:
                raise RuntimeError("youtube_url is required for source_type=youtube")

            youtube_url = normalize_youtube_url(youtube_url)

            meta = youtube_metadata(youtube_url)
            title = meta.get("title")
            description = meta.get("description")
            duration = meta.get("duration")

            audio_path = download_youtube_audio(youtube_url)
            transcript = transcribe(audio_path)

        else:
            if not uploaded_video_path:
                raise RuntimeError("uploaded_video_path is required for source_type=upload")

            storage = StorageClient(use_service_role=True)

            fname = uploaded_filename or "video.mp4"
            path = f"user_{user_id}/videos/{video_id}_{fname}"

            with open(uploaded_video_path, "rb") as f:
                data = f.read()

            upload_result = storage.upload_bytes(
                path=path,
                content=data,
                content_type="video/mp4",
                upsert=True,
            )
            safe_path = upload_result.get("_path") or path
            storage_path = safe_path
            storage_url = storage.get_public_url(safe_path)

            title = fname
            duration = probe_duration_seconds(uploaded_video_path)

            audio_path = extract_audio_from_video(uploaded_video_path)
            transcript = transcribe(audio_path)

        video.source_type = source_type
        video.source_url = youtube_url if source_type == "youtube" else None
        video.storage_url = storage_url
        video.storage_path = storage_path
        video.title = title
        video.description = description
        video.duration_seconds = duration
        video.transcript = transcript

        db.query(VideoChunk).filter(VideoChunk.video_id == video.id).delete()

        chunks = chunk_text(transcript)
        for idx, chunk in enumerate(chunks):
            vec = embed_text(
                text=chunk,
                model=EMBED_MODEL,
                input_type="search_document",
                truncate="END",
            )
            if len(vec) != EMBED_DIMS:
                raise RuntimeError(f"Embedding dims mismatch: got {len(vec)} expected {EMBED_DIMS}")

            db.add(
                VideoChunk(
                    video_id=video.id,
                    user_id=user_id,
                    chunk_index=idx,
                    content=chunk,
                    embedding=vec,
                )
            )

        video.status = "ready"
        video.error = None
        db.add(video)
        db.commit()
        db.refresh(video)

        return video, len(chunks)

    except Exception as e:
        video.status = "failed"
        video.error = str(e)
        db.add(video)
        db.commit()
        db.refresh(video)
        return video, 0