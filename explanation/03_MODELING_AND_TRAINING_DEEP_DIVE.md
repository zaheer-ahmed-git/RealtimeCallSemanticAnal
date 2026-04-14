# 03 - Modeling and Training Deep Dive

## 1. Model stack at a glance

### Sentiment model (text)
- Class: `SentimentAnalyzer`
- File: `backend/src/call_analysis/models.py`
- Default model shortcut: DistilBERT sentiment pipeline
- Alternative: FinBERT (`ProsusAI/finbert`)
- Fallback path: keyword-based scoring when model loading fails

### Emotion model (audio)
- Class: `EmotionDetector`
- File: `backend/src/call_analysis/models.py`
- Supports two backends:
  1. Legacy acoustic network (`AcousticEmotionModel`, CNN+LSTM with attention)
  2. Hugging Face checkpoint backend (Wav2Vec2 audio classification)

### Sale predictor (tabular fused features)
- Class: `SalePredictor`
- File: `backend/src/call_analysis/models.py`
- Model type: XGBoost classifier loaded via `joblib`
- Output: probability, class label, confidence estimate, confidence interval, feature-importance metadata

## 2. Feature fusion for sale prediction
`SalePredictor.create_fused_feature_vector()` builds features from:
- Sentiment aggregate:
  - mean
  - variance
- Emotion probabilities:
  - neutral
  - happiness
  - anger
  - sadness
  - frustration
- Conversational dynamics:
  - silence_ratio
  - interruption_frequency
  - talk_listen_ratio
  - turn_taking_frequency
  - filler_word_frequency (included in runtime vector)

Training script schema currently expects 11 required columns (without filler as mandatory).

## 3. Training scripts and what each one does

### `backend/scripts/best_train_emotion_model.py`
- Best-practice Wav2Vec2-based pipeline
- Dataset parsing for RAVDESS naming format
- Supports:
  - `--mode validate_data`
  - `--mode train`
  - `--mode evaluate`
- Default split strategy: actor-holdout (prevents speaker leakage)
- Saves Hugging Face checkpoint + metrics + confusion matrix artifacts

### `backend/scripts/train_emotion_model.py`
- Legacy acoustic CNN+LSTM training path
- Still useful if you want strict architecture matching with older acoustic backend

### `backend/scripts/generate_sale_training_dataset.py`
- Generates realistic synthetic call-level rows
- Controls label ratio, noise, contradictions, metadata richness
- Can output strict training schema compatible with sale trainer

### `backend/scripts/train_sale_predictor.py`
- Validates required columns
- Handles split strategy (stratified random, explicit split column, or chronological)
- Handles class imbalance via `scale_pos_weight`
- Applies calibration compatibility logic (`CalibratedClassifierCV` variants)
- Optional threshold optimization
- Saves model and metrics artifacts

### Validation tools
- `backend/scripts/validate_trained_models.py`
- `backend/scripts/validate_production_readiness.py` (partly stale against newest class interfaces; use with awareness)

## 4. Current artifact state in this repository

Detected under `backend/models/`:
- `sale_model.pkl` (present)
- `best_emotion_wav2vec2_v2/best_checkpoint/` (present)
- Emotion training reports and confusion matrix files (present)
- Sale training results currently stored in `backend/models/sale_predict_model/sale_training_results.json`

Note:
- Keep sale model sidecar files close to the deployed model path for consistent threshold loading behavior.

## 5. Metrics snapshot from saved artifacts

### Sale predictor (`sale_training_results.json`)
Validation:
- Accuracy: `0.7253`
- Precision: `0.5554`
- Recall: `0.4233`
- F1: `0.4805`
- ROC-AUC: `0.7315`

Test:
- Accuracy: `0.7220`
- Precision: `0.5480`
- Recall: `0.4189`
- F1: `0.4748`
- ROC-AUC: `0.7323`

### Emotion model summary (`best_emotion_training_summary.json`)
- Best epoch: `12`
- Best validation macro-F1: `0.8321`
- Split strategy: actor holdout (train actors 1-18, val 19-24)

## 6. Reproducible training commands (project-local)

### Generate synthetic sale data
```powershell
python backend\scripts\generate_sale_training_dataset.py --n_samples 20000 --sale_ratio 0.30 --output data\synthetic_sales_full.csv --training_output data\sale_training_data.csv --overwrite
```

### Train sale model
```powershell
python backend\scripts\train_sale_predictor.py --csv_path data\sale_training_data.csv --output_dir backend\models --early_stopping_rounds 20 --optimize_threshold
```

### Train best emotion model (Wav2Vec2)
```powershell
python backend\scripts\best_train_emotion_model.py --mode train --data_dir data\raw\ravdess --output_dir backend\models\best_emotion_wav2vec2_v2 --base_model facebook/wav2vec2-base --emotion_mapping default --split_strategy actor_holdout --train_actor_max 18 --epochs 30 --batch_size 8 --learning_rate 2e-5
```

## 7. Why these model choices are defendable
- DistilBERT/FinBERT gives strong pretrained NLP baselines with manageable compute.
- Wav2Vec2 checkpoint path provides stronger SER capability than only handcrafted acoustic features.
- XGBoost is robust for mixed engineered features and gives practical feature-importance introspection.
- Segment-level modeling improves temporal interpretability for call review.

## 8. Limitations to discuss transparently
1. Synthetic sale data is useful for pipeline stability, but real CRM-labeled calls are needed for final business-grade performance claims.
2. Emotion and sale models require strict feature/schema consistency between training and inference.
3. Some robustness scripts are older than current interfaces and should be treated as partial checks.
4. Confidence interval logic for sale prediction is heuristic and can be further improved with formal uncertainty methods.
