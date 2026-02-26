from collections import Counter

import pandas as pd
import streamlit as st

from detector_core import (
    combine_risk_score,
    clean_text,
    detect_categories,
    explain_prediction,
    extract_urls,
    highlight_terms,
    sender_reputation,
    suspicious_term_count,
    train_and_evaluate_model,
    url_risk,
)

st.set_page_config(page_title="AI SMS/Email Spam & Scam Detector", layout="wide")


@st.cache_resource
def get_model_bundle():
    return train_and_evaluate_model()


bundle = get_model_bundle()
model = bundle.pipeline

st.title("📨 AI SMS/Email Spam & Scam Detector")
st.caption("Hybrid AI + rule engine for phishing, OTP fraud, banking scam, and lottery-style spam detection.")

with st.expander("Project Build Plan Mapping", expanded=False):
    st.markdown(
        """
- **Phase 1 (Basic Model):** dataset load + text cleaning + TF-IDF + Logistic Regression + holdout metrics.
- **Phase 2 (Smart Detection):** suspicious keywords + URL checks + combined risk score.
- **Phase 3 (Streamlit App):** text box + predict button + risk meter + explanation panel + dashboard.
- **Phase 4 (Advanced Upgrade):** hooks for BERT/chrome extension/deployment (documented in README).
        """
    )

st.sidebar.header("Model Snapshot")
st.sidebar.metric("Accuracy", f"{bundle.accuracy * 100:.1f}%")
st.sidebar.metric("Precision", f"{bundle.precision * 100:.1f}%")
st.sidebar.metric("Recall", f"{bundle.recall * 100:.1f}%")
st.sidebar.metric("F1 Score", f"{bundle.f1 * 100:.1f}%")
st.sidebar.caption("Metrics are estimated on a small in-project holdout split.")

if "history" not in st.session_state:
    st.session_state.history = []

left, right = st.columns([2, 1])

with left:
    sender = st.text_input("Sender (email/number/domain)", placeholder="alerts@sbi.co.in or VM-AXISBK")
    message = st.text_area("Paste SMS / Email text", height=220, placeholder="Paste full message content here...")
    run = st.button("Analyze Message", type="primary")

with right:
    st.subheader("⚡ Rule-Based Checks")
    sender_rep = sender_reputation(sender)
    rep_color = {"trusted": "🟢", "neutral": "🟡", "suspicious": "🔴", "unknown": "⚪"}[sender_rep]
    st.write(f"**Sender Reputation:** {rep_color} {sender_rep.title()}")

if run and message.strip():
    cleaned_message = clean_text(message)
    probs = model.predict_proba([cleaned_message])[0]
    spam_prob = float(probs[1])

    urls = extract_urls(message)
    url_findings = [(url, url_risk(url)) for url in urls]
    categories = detect_categories(message)
    term_count = suspicious_term_count(message)

    risk_score = combine_risk_score(spam_prob, sender_rep, url_findings, term_count)
    label = "Spam/Scam" if risk_score >= 50 else "Safe"
    reasons = explain_prediction(message, spam_prob, sender_rep, url_findings, risk_score)

    st.subheader("Prediction")
    c1, c2, c3 = st.columns(3)
    c1.metric("Label", label)
    c2.metric("Spam Probability (ML)", f"{spam_prob * 100:.1f}%")
    c3.metric("Final Risk Score", f"{risk_score:.1f}/100")

    st.subheader("Risk Meter")
    st.progress(int(risk_score))

    st.subheader("Highlighted Suspicious Terms")
    st.markdown(highlight_terms(message), unsafe_allow_html=True)

    st.subheader("Detected Scam Category")
    st.write(", ".join(categories))

    st.subheader("Explanation Box")
    for reason in reasons:
        st.write(f"- {reason}")

    st.subheader("URL Risk Detection")
    if url_findings:
        for url, level in url_findings:
            icon = {"low": "🟢", "medium": "🟡", "high": "🔴"}[level]
            st.write(f"{icon} `{url}` → **{level.upper()} risk**")
    else:
        st.write("No URLs found in text.")

    st.session_state.history.append(
        {
            "label": label,
            "ml_spam_probability": round(spam_prob, 4),
            "final_risk_score": round(risk_score, 2),
            "sender": sender,
            "categories": ", ".join(categories),
        }
    )

st.divider()
st.subheader("📊 Real-time Dashboard")
if st.session_state.history:
    history_df = pd.DataFrame(st.session_state.history)
    total = len(history_df)
    spam_count = int((history_df["label"] == "Spam/Scam").sum())

    d1, d2, d3 = st.columns(3)
    d1.metric("Total Messages", total)
    d2.metric("Spam/Scam Flagged", spam_count)
    d3.metric("Safe", total - spam_count)

    st.bar_chart(Counter(history_df["categories"].tolist()))
    st.line_chart(history_df[["ml_spam_probability", "final_risk_score"]])
    st.dataframe(history_df.tail(20), use_container_width=True)
else:
    st.info("No analysis yet. Submit a message to populate dashboard.")
