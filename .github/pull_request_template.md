curl -X POST "http://127.0.0.1:8000/llm/ingest-video" \
  -H "Authorization: Bearer <TOKEN>" \
  -F "youtube_url=https://www.youtube.com/watch?v=<VIDEO_ID>"curl -X POST "http://127.0.0.1:8000/llm/ingest-video" \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@/path/to/video.mp4"# Summary
<!-- What does this PR add/change in 1–3 sentences? -->
curl -X POST "http://127.0.0.1:8000/llm/videos/search" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"video_id":"<VIDEO_UUID>","query":"your query","top_k":5}'
# Changes
<!-- Bullet list of key changes. Keep it concise. -->
- 
select id, status, source_type, source_url, title, duration_seconds
from videos
where id = '<VIDEO_UUID>';

select video_id, chunk_index, left(content, 120) as preview
from video_chunks
where video_id = '<VIDEO_UUID>'
order by chunk_index;
# API Endpoints (if applicable)
<!-- List new/updated endpoints with a short description. -->
- `POST /llm/ingest-video` — Accepts `youtube_url` (form) OR `file` (upload) and ingests a video (metadata + transcript + chunks + embeddings).
- `POST /llm/videos/search` — Semantic search over `video_chunks` using vector similarity.

# Data / DB
<!-- What tables/columns are written/read? Mention pgvector usage if relevant. -->
- `videos`: stores `source_type`, `source_url`, `title`, `description`, `duration_seconds`, `transcript`, `status`, `error`, (and `storage_url/storage_path` for uploads).
- `video_chunks`: stores `content`, `chunk_index`, and `embedding` (`Vector(1024)` via pgvector).

# How to Test
## Setup
```bash
uvicorn app.main:app --reload --env-file .env
Requirements / Notes
Requires ffmpeg and ffprobe installed and available in PATH
Uses yt-dlp for YouTube ingestion and faster-whisper for transcription
Embeddings model: Cohere embed-english-v3.0 (1024 dims)
Optional env vars:
WHISPER_MODEL (default: small)
YTDLP_COOKIES_FILE (for restricted YouTube videos)
YTDLP_PROXY (for geo-blocked access)
Screenshots / Demo (optional)
Checklist
 Tested YouTube ingest
 Tested file upload ingest
 Verified videos row saved correctly
 Verified video_chunks rows + embeddings created
 Verified search endpoint returns expected results
