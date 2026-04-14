# 05 - Document Reconciliation, Demo Plan, and Defense Notes

## 1. Why this file exists
The `document/` folder contains many useful guides, but not all are equally current. This file gives one consistent, evaluator-ready narrative based on actual code + current artifacts.

## 2. Document folder map (high-value files)

### Core architecture and flow
- `document/COMPLETE_SYSTEM_FLOW.md`
- `document/ARCHITECTURE_DIAGRAMS.md`
- `document/DESIGN_DECISIONS.md`

### Setup and run
- `document/QUICK_START.md`
- `document/BACKEND_FRONTEND_SETUP.md`
- `document/DEMO_RUN_CHECKLIST_AND_MODEL_TRAINING.md`

### Training-specific
- `document/EMOTION_MODEL_TRAINING_GUIDE_MARCH_2026.md`
- `document/SALE_PREDICTOR_MODEL_TRAINING_GUIDE_MARCH_2026.md`
- `document/EMOTION_MAPPING_JUSTIFICATION.md`

### Requirement alignment and progress
- `document/FYP_DOCUMENT_ALIGNMENT.md`
- `document/FYP_COMPLETION_README.md`
- `document/REPORT.md`

## 3. Code-vs-doc reconciliation notes (important in viva)

### Accurate and aligned
- Backend FastAPI endpoints and async flow are implemented.
- Frontend integration with typed API calls is implemented.
- Sale and emotion model artifacts are present in repo.
- Training scripts are present and runnable with proper data/env setup.

### Partially stale or mixed-state documentation
- Some files mention earlier path names or older module naming.
- Some reports discuss in-progress status that is now improved in code.
- Validation scripts and tests described in docs are not all synchronized with latest internals.

How to answer this in evaluation:
- "Docs were produced incrementally during project phases; we now use the explanation pack as reconciled source of truth tied to current codebase."

## 4. Day-before-demo checklist

### Environment
- Python env active, backend dependencies installed
- Node modules installed in frontend
- MongoDB reachable
- HF token set if using real ASR/diarization models

### Models and artifacts
- `backend/models/sale_model.pkl` exists
- `backend/models/best_emotion_wav2vec2_v2/best_checkpoint` exists
- `EMOTION_MODEL_PATH` points to chosen checkpoint path

### Servers
- Backend starts cleanly on `http://localhost:8000`
- Frontend starts on `http://localhost:3000`
- `GET /health` returns healthy/degraded with understandable DB status

### Workflow smoke test
- Upload a small WAV file
- Start analysis
- Confirm polling progression
- Confirm results page and charts
- Confirm export download actions

## 5. Suggested live demo sequence (7-10 minutes)
1. Problem statement (30-45s).
2. High-level architecture slide (45-60s).
3. Show backend endpoint docs (`/docs`) and explain async pipeline (1 min).
4. Upload and analyze one real sample in UI (3-4 min).
5. Show sentiment, emotion, sale gauge, key phrases (1-2 min).
6. Show history page and export outputs (1 min).
7. Close with limitations + future work (1 min).

## 6. Suggested fallback plan (if live processing is slow)
- Keep one already-completed `call_id` in DB and open `/results/[callId]` directly.
- Keep local JSON/PDF export samples ready from previous run.
- If diarization is too slow, explain architecture with status endpoint while showing already generated results.

## 7. Defense angles for likely evaluator concerns

### "How do you know this is not just a static UI?"
- Show `api.ts` calls and backend status polling sequence.

### "Where is the ML actually used?"
- Point to `ConversationAnalyzer.analyze_conversation()` and model classes in `models.py`.

### "How do you handle operational failure?"
- Explain DB checks, status transitions (`pending -> processing -> completed/failed`), and frontend error toasts.

### "How do you protect user data?"
- Mention PII masking and secure configurable environment setup.

### "What is your biggest current limitation?"
- Real labeled CRM-ground-truth scale and broader production benchmarking remain the main next step.

## 8. If evaluator asks for one-line project impact
"We converted raw call audio into structured, model-driven business intelligence in one integrated web workflow, not just isolated experiments."
