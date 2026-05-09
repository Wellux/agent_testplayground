# ralph-voice-server — minimal container.
# whisper.cpp is NOT installed here; install it on the host (Mac mini) and
# bind-mount or co-install. The container only handles the FastAPI plane.
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY pyproject.toml ./
COPY voice_server ./voice_server
RUN pip install --no-cache-dir .

EXPOSE 7117

ENV RALPH_VOICE_HOST=0.0.0.0 RALPH_VOICE_PORT=7117
CMD ["python", "-m", "voice_server"]
