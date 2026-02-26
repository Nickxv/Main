# AI SMS/Email Spam & Scam Detector

A resume-ready Streamlit project for detecting India-focused scams (OTP theft, KYC fraud, fake bank alerts, phishing links) from SMS/email text.

## Features

### Core
- Paste SMS/email text and predict **Spam/Scam** vs **Safe**
- ML probability score (TF-IDF + Logistic Regression)
- Suspicious keyword highlighting
- Explanation box with human-readable reasoning
- Sidebar model metrics: Accuracy, Precision, Recall, F1

### Advanced
- URL extraction + risk levels
- Sender reputation check (rule-based)
- Scam type detection: `phishing`, `lottery`, `otp fraud`, `banking scam`
- Combined risk score (ML + rules)
- Real-time dashboard with recent analysis history

## Build Plan Mapping

### Phase 1 — Basic Model
- Load in-project dataset
- Clean text
- Train TF-IDF + Logistic Regression
- Evaluate holdout metrics and display in sidebar

### Phase 2 — Smart Detection
- Suspicious keyword detection
- URL detection and risk analysis
- Final risk score from model + rule signals

### Phase 3 — Streamlit App
- Text box + predict button
- Risk meter/progress bar
- Explanation box and category output
- Dashboard for usage trends

### Phase 4 — Advanced Upgrade (next steps)
- Replace baseline model with BERT for better semantic detection
- Add dedicated multi-label scam classifier
- Add Chrome extension UI for inbox/SMS quick scan
- Deploy to Streamlit Cloud / Render and connect monitoring

## Project Structure

- `app.py`: Streamlit UI and dashboard.
- `detector_core.py`: model training + rule-engine logic.
- `tests/test_detector_core.py`: unit tests for core detection behavior.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Run tests

```bash
python -m unittest discover -s tests
```
