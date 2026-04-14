# 01 - Project and Architecture Overview

## 1. Project in one sentence
We built an AI-based call analysis platform that takes uploaded call audio, transcribes and diarizes it, extracts multimodal signals (text + audio + conversation dynamics), predicts sale likelihood, and shows results in a web dashboard.

## 2. Problem we solve
Call centers usually review calls manually or with basic text-only tools. That misses:
- How something was said (tone, pauses, interruptions)
- Speaker behavior patterns across a full call
- Probability-level decision support (for example, sale chance)

Our project addresses this with multimodal analysis and an explainable pipeline.

## 3. Main objectives implemented
- Audio upload and asynchronous processing
- Speech-to-text transcription
- Speaker diarization and role labeling (Agent/Customer)
- Segment-level sentiment analysis
- Segment-level emotion analysis
- Conversation-dynamics feature extraction
- Sale probability prediction
- Results storage, history, and exports (JSON/PDF/CSV)
- Frontend dashboard for live review

## 4. High-level architecture

### Frontend
- Next.js 14 + React + TypeScript + Tailwind
- Main app page and dashboard components
- Calls backend APIs through `/api/*` proxy

### Backend
- FastAPI service in `backend/src/call_analysis/web_app_fastapi.py`
- Orchestration class: `ConversationAnalyzer` in `backend/src/call_analysis/models.py`
- Audio/text preprocessing in `preprocessing.py`
- Feature logic in `feature_extraction.py`

### Models
- Sentiment: DistilBERT/FinBERT (Hugging Face)
- Emotion: Wav2Vec2 checkpoint backend and legacy acoustic CNN+LSTM backend
- Sale prediction: XGBoost (`sale_model.pkl`)

### Storage
- MongoDB for upload/analyze/status/results/history flow
- Filesystem for uploads and exported artifacts

## 5. Real end-to-end runtime flow
1. User uploads audio on frontend (`UploadForm.tsx`).
2. Backend `/api/upload` validates type/size and saves file under `uploads/`.
3. Backend inserts call document in MongoDB with status `pending`.
4. Frontend sends `/api/analyze` with `call_id`.
5. Backend starts background thread and updates progress.
6. Pipeline executes:
   - Whisper transcription
   - Speaker diarization (WhisperX+Resemblyzer or WhisperX built-in/pyannote)
   - Text-segment alignment + PII masking
   - Audio feature extraction
   - Sentiment + emotion + sale prediction
7. Backend stores normalized results in MongoDB.
8. Frontend polls `/api/status/{call_id}` and fetches `/api/results/{call_id}` when done.
9. Dashboard renders charts and allows export.

## 6. Actual repository structure covered in this analysis
- `backend/`: API, pipeline, models, training scripts, tests
- `frontend/`: pages, components, typed API client
- `document/`: setup, architecture, training, checklist, alignment docs

## 7. Current maturity (based on code + artifacts)
Strong areas:
- Complete backend API flow
- Complete frontend integration with typed API client
- Model artifacts available in repo (`sale_model.pkl`, Wav2Vec2 checkpoint)
- Training and validation scripts available
- Demo checklist and deployment docs exist

Open risks to discuss honestly in evaluation:
- Some documentation references old paths/names from earlier iterations
- A few test/validation scripts are out of sync with latest class methods
- Full production benchmarking on real organizational call data is still a next phase

## 8. What evaluators usually ask first (quick answers)
- "What is novel here?"
  - Multimodal fusion for call intelligence (text sentiment + audio emotion + conversation dynamics + sale prediction) in one integrated student-friendly system.
- "What is the actual deliverable?"
  - Working upload-to-dashboard web platform with history and exports, plus reproducible training pipelines.
- "How is this better than simple sentiment analysis?"
  - It uses per-segment emotions and interaction dynamics, not just transcript polarity.
