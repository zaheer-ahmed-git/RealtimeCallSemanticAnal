# 06 - Evaluator Q and A Bank

Use this as quick viva prep. Answers are kept in project-specific terms.

## A. Problem and Scope

### Q1. What problem are you solving?
A. We analyze call center conversations using both what was said (text) and how it was said (audio emotion and dynamics), then estimate sale probability and show actionable dashboards.

### Q2. Why not use only text sentiment?
A. Text-only misses tone, pauses, interruptions, and emotional intensity, which are important for call outcomes.

### Q3. Who are the users?
A. Call center managers, QA teams, sales analysts, and agent trainers.

### Q4. What is your main deliverable?
A. A full upload-to-insight web system (FastAPI + Next.js) with history and export features, plus model training pipelines.

## B. Architecture

### Q5. What are your major layers?
A. Frontend UI, backend API/orchestration, ML pipeline (ASR/diarization/features/models), MongoDB persistence, and export/report layer.

### Q6. Which file is your main backend API file?
A. `backend/src/call_analysis/web_app_fastapi.py`.

### Q7. How does the frontend connect to backend?
A. Next.js rewrite proxy maps `/api/*` to `http://localhost:8000/api/*`.

### Q8. Is your processing synchronous?
A. No. Upload is separate, analysis runs in a background thread, and frontend polls status.

### Q9. Why background processing?
A. Audio analysis is compute-heavy and can exceed request timeout if done synchronously.

## C. Backend Flow

### Q10. What happens after upload?
A. File is validated and saved, MongoDB call record is created with `pending` status, then `/api/analyze` starts processing.

### Q11. How do you track progress?
A. Backend updates progress in DB (10, 20, 40, 60, 80, 100); frontend reads via `/api/status/{call_id}`.

### Q12. What are your critical API endpoints?
A. `/api/upload`, `/api/analyze`, `/api/status/{id}`, `/api/results/{id}`, `/api/history`, `/api/export/{id}` plus `/pdf` and `/csv`.

### Q13. What if MongoDB is down?
A. Main data-flow endpoints return `503` with a clear message instead of pretending success.

## D. Preprocessing and Features

### Q14. Which ASR model do you use?
A. Whisper (with WhisperX options in preprocessing workflow).

### Q15. How do you do speaker diarization?
A. Multiple modes: WhisperX + Resemblyzer (fast), WhisperX built-in pyannote mode, and pyannote fallback.

### Q16. How do you map speakers to customer/agent?
A. Heuristic role identification using first-speaker hints, speaking-time patterns, and keyword/question signals.

### Q17. What conversational dynamics do you compute?
A. Silence ratio, interruption frequency, talk/listen ratio, turn-taking frequency, filler-word frequency.

### Q18. Why filler words matter?
A. High filler frequency often correlates with hesitation or uncertainty in sales/customer interactions.

## E. Models

### Q19. Which sentiment models are supported?
A. DistilBERT (default) and FinBERT (financial domain), with keyword fallback if model load fails.

### Q20. How is emotion modeled?
A. `EmotionDetector` supports legacy acoustic CNN+LSTM and Wav2Vec2 checkpoint-based inference.

### Q21. Why XGBoost for sale prediction?
A. It performs well on structured engineered features, handles nonlinearity, and offers practical feature importance.

### Q22. What is fused for sale prediction?
A. Sentiment aggregates + emotion probabilities + conversational dynamics.

### Q23. Do you provide confidence?
A. Yes. Sale predictor returns probability, threshold-based class, and confidence interval estimate.

## F. Training

### Q24. What data is used for emotion training?
A. RAVDESS with actor-holdout split to reduce speaker leakage.

### Q25. Why actor-holdout split?
A. Random split can overestimate performance; actor-holdout better tests generalization to unseen speakers.

### Q26. What outputs come from emotion training?
A. Best checkpoint folder, confusion matrix, run config, history, summary reports.

### Q27. What columns are required for sale training?
A. 11 required columns plus `sale_outcome` label, matching `train_sale_predictor.py` expectations.

### Q28. Do you handle class imbalance?
A. Yes, via `scale_pos_weight` in XGBoost training.

### Q29. Do you calibrate probabilities?
A. Yes, using compatible calibration paths depending on sklearn version.

## G. Frontend

### Q30. How do you ensure frontend/backend type consistency?
A. Shared TypeScript interfaces and normalization logic in `frontend/src/lib/api.ts`.

### Q31. Which visual outputs are shown?
A. Sentiment chart, emotion distribution chart, sale probability gauge, key phrase lists, and summary cards.

### Q32. Can users export analysis?
A. Yes, as PDF, CSV, and JSON.

### Q33. What happens if result fetching fails?
A. UI shows toast errors and does not crash; users can retry.

## H. Security and Privacy

### Q34. How do you protect sensitive content?
A. PII masking is applied in text processing and result handling paths.

### Q35. How do you control uploaded files?
A. File type/size checks and unique filename generation are enforced.

### Q36. Are secrets hardcoded?
A. No, runtime configuration is environment-variable based.

## I. Quality and Validation

### Q37. How do you validate trained models?
A. With `backend/scripts/validate_trained_models.py` and targeted smoke tests.

### Q38. Are all tests fully current?
A. Some older tests/scripts are partially stale versus latest interfaces; core runtime flow is still functional and demonstrable.

### Q39. What metrics do you report?
A. For sale model: accuracy, precision, recall, F1, ROC-AUC; for emotion model: macro-F1 and confusion matrix.

### Q40. How do you avoid over-claiming?
A. We separate demonstrated system functionality from future benchmark ambitions and clearly state current limitations.

## J. Limitations and Future Work

### Q41. Biggest current limitation?
A. Need larger real CRM-labeled production datasets for stronger sale model generalization claims.

### Q42. What technical improvement would you do first?
A. Replace polling with WebSockets and improve uncertainty estimation with more formal methods.

### Q43. How would you improve model reliability?
A. Continuous retraining with real call labels, drift monitoring, and strict schema/version governance for features.

### Q44. Can this system support real-time streaming?
A. Not full streaming now; architecture is batch/async per upload. Real-time streaming is a planned extension.

## K. Defense-ready one-liners

### Q45. What is your core technical contribution?
A. A practical multimodal pipeline integrating ASR, diarization, sentiment, emotion, dynamics, and sale prediction into one deployed web workflow.

### Q46. What is your core engineering contribution?
A. End-to-end integration from upload to persisted analytics and exports with asynchronous orchestration.

### Q47. Why should this be accepted as an FYP outcome?
A. It demonstrates full-stack ML productization: data pipeline, model integration, API design, frontend visualization, and reproducible training scripts.

### Q48. If evaluator asks "what would you deploy tomorrow?"
A. Current stack with MongoDB Atlas, model artifact path locking, health checks, and a controlled demo dataset while continuing real-label model iteration.

### Q49. If evaluator asks "what did you personally learn?"
A. Integrating ML models is easier than making them production-coherent; orchestration, schema consistency, and failure handling are the real complexity.

### Q50. Final closing statement
A. We built a complete intelligent call analytics platform that is operational today and extensible for production maturity tomorrow.
