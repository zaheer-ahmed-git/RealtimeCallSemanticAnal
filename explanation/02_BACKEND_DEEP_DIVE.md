# 02 - Backend Deep Dive

## 1. Backend entry points

### Main server runner
- File: `backend/run_web_app.py`
- Starts uvicorn with module `call_analysis.web_app_fastapi:app`
- Uses `Config.HOST`, `Config.PORT`, and `Config.DEBUG`

### CLI runners
- `backend/run_demo.py`: runs `DemoSystem` in terminal mode
- `backend/run_full_analysis.py`: full pipeline on one file
- `backend/run_diarization_only.py`: speaker diarization experiments using existing transcription

## 2. Core backend modules

### `config.py`
Responsibilities:
- Loads env vars via `python-dotenv`
- Defines API host/port, model options, upload limits, DB settings
- Creates runtime directories (`uploads`, `logs`, `output`, `exports`)

Important env vars:
- `HF_TOKEN`
- `MONGODB_URI`, `MONGODB_DATABASE`
- `HOST`, `PORT`, `DEBUG`
- `SENTIMENT_MODEL`, `SENTIMENT_MODEL_PATH`
- `EMOTION_MODEL_PATH`

### `web_app_fastapi.py`
Responsibilities:
- FastAPI app creation
- CORS
- MongoDB startup connection and diagnostics
- REST endpoints for upload/analyze/status/results/history/export

### `preprocessing.py`
Key classes:
- `AudioProcessor`
  - Audio validation/conversion
  - Whisper transcription (with long-audio chunking)
  - Multiple diarization modes:
    - WhisperX + Resemblyzer (fast CPU path)
    - WhisperX built-in diarization (pyannote-based)
    - Pyannote fallback
  - Speaker role mapping to `AGENT` / `CUSTOMER`
- `TextProcessor`
  - PII masking
  - Text normalization/tokenization
  - Timestamp-based text assignment to diarization segments

### `feature_extraction.py`
Key class:
- `FeatureExtractor`
  - Extracts audio features (MFCC, mel-spectrogram, pitch, chroma, energy, formants)
  - Extracts text embeddings (BERT lazy-loading)
  - Extracts dynamics:
    - silence ratio
    - interruption frequency
    - talk/listen ratio
    - turn-taking frequency
    - filler word frequency

### `models.py`
Key classes:
- `SentimentAnalyzer`
- `EmotionDetector`
- `SalePredictor`
- `ConversationAnalyzer` (main orchestrator)

## 3. API endpoint map (actual implementation)

Demo/data endpoints:
- `GET /`
- `GET /api/conversations`
- `GET /api/analyze/{conversation_id}`
- `GET /api/analyze-all`
- `GET /api/dashboard/{conversation_id}`
- `GET /api/insights`

Production upload/analysis endpoints:
- `POST /api/upload`
- `POST /api/analyze` (body: `{ "call_id": "..." }`)
- `GET /api/status/{call_id}`
- `GET /api/results/{call_id}`
- `GET /api/history`

Export endpoints:
- `GET /api/export/{call_id}` (JSON)
- `GET /api/export/{call_id}/pdf`
- `GET /api/export/{call_id}/csv`

Health:
- `GET /health`

## 4. Asynchronous analysis pipeline details
In `web_app_fastapi.py`, `_run_analysis_background()` executes these steps and progress updates:
- 10%: start transcription
- 20%: diarization completed
- 40%: text segmentation/processing completed
- 60%: audio feature extraction
- 80%: model inference
- 100%: final DB update with normalized output fields

Normalized fields written to `calls` collection include:
- `status`, `progress`
- `duration`, `participants`
- `avg_sentiment`, `sale_probability`
- `sentiment_scores` array
- `emotions` object
- `key_phrases` object
- full `result` payload

## 5. MongoDB dependency behavior
Main upload/analyze/status/results/history/export flow requires MongoDB.
- If DB is unavailable, endpoints raise `503` with guidance.
- Health endpoint reports degraded/not_configured accordingly.

This design avoids fake success for upload if persistence is missing.

## 6. Security and privacy mechanisms currently present
- PII masking through spaCy (with regex fallback)
- Upload type and max-size validation
- Unique timestamp-based filename generation to avoid overwrite
- Environment-driven secrets/config

## 7. Backend strengths to present
- Clean class-based orchestration (`ConversationAnalyzer`)
- Multiple diarization backends for robustness
- Segment-level processing instead of whole-call flattening
- Async workflow with status polling
- Export pipeline (JSON/PDF/CSV)

## 8. Known backend technical debt (important for evaluator honesty)
1. Some legacy scripts/tests reference methods not present in current classes (for example private validation helpers), so not all utility scripts are equally up to date.
2. `db_connection.py` is debug-style and not used as the production DB layer in FastAPI startup.
3. Sale predictor threshold sidecar file (`sale_training_results.json`) is expected near model path; artifact placement should stay consistent.
4. Some docs still mention older filenames/paths from previous project states.

## 9. Why backend design is defendable
- Separation of concerns is clear: preprocessing, features, models, API.
- Runtime and training are separated.
- Failure paths are explicit (not silent).
- Pipeline can be tested as whole (`run_full_analysis.py`) and by module (training/validation scripts).
