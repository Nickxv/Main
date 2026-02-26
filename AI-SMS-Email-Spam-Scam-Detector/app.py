import re
from collections import Counter
from dataclasses import dataclass

import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

st.set_page_config(page_title="AI SMS/Email Spam & Scam Detector", layout="wide")

SUSPICIOUS_TERMS = {
    "urgent", "verify", "kyc", "lottery", "winner", "otp", "account", "suspend", "link",
    "click", "prize", "refund", "limited", "alert", "bank", "update", "login", "reward",
    "claim", "blocked", "pay", "upi", "password", "immediately", "gift", "bonus", "pin"
}

KNOWN_SENDERS = {
    "sbi.co.in": "trusted",
    "icicibank.com": "trusted",
    "hdfcbank.com": "trusted",
    "gov.in": "trusted",
    "rbi.org.in": "trusted",
}

BAD_SENDER_HINTS = ["@gmail", "@yahoo", "@outlook", "-verify", "secure-update", "freegift", "winner"]

TRAIN_DATA = [
    ("Your OTP for login is 563902. Do not share with anyone.", 0),
    ("Dear user, your KYC is pending. Verify now to avoid account suspension.", 1),
    ("Congratulations! You won lottery prize. Click link to claim reward.", 1),
    ("Your SBI account statement for January is ready.", 0),
    ("Bank alert: update PAN and KYC immediately using this link", 1),
    ("Meeting moved to 3 PM. Please confirm attendance.", 0),
    ("You are selected for cashback. Share OTP to receive amount", 1),
    ("A/c debited for Rs 550 at Amazon. If not you call customer care.", 0),
    ("Your account will be blocked today. Login here to verify identity", 1),
    ("Electricity bill generated successfully. Due date 16th.", 0),
    ("Win iPhone for just Rs 10 registration. Limited seats", 1),
    ("Income tax refund processed to your registered bank account", 0),
    ("URGENT: update UPI PIN now or account suspended", 1),
    ("Thanks for shopping with us. Order #1032 shipped.", 0),
    ("KYC expired. Submit Aadhaar and PAN details at bit.ly/secure-verify", 1),
    ("IRCTC ticket booked successfully for tomorrow.", 0),
    ("Final reminder: your account will be frozen unless you login now", 1),
    ("Your Swiggy order has been delivered", 0),
]

CATEGORY_RULES = {
    "phishing": ["login", "verify", "click", "password", "account", "identity"],
    "lottery": ["lottery", "winner", "won", "prize", "reward", "claim"],
    "otp fraud": ["otp", "share otp", "one time password", "security code", "pin"],
    "banking scam": ["bank", "kyc", "pan", "upi", "account blocked", "suspend"],
}


@dataclass
class ModelBundle:
    pipeline: Pipeline
    accuracy: float


def clean_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"https?://\S+|www\.\S+", " URLTOKEN ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


@st.cache_resource
def train_and_evaluate_model() -> ModelBundle:
    df = pd.DataFrame(TRAIN_DATA, columns=["text", "label"])
    df["clean_text"] = df["text"].map(clean_text)

    x_train, x_test, y_train, y_test = train_test_split(
        df["clean_text"],
        df["label"],
        test_size=0.3,
        random_state=42,
        stratify=df["label"],
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
        ("clf", LogisticRegression(max_iter=1200)),
    ])
    pipeline.fit(x_train, y_train)
    y_pred = pipeline.predict(x_test)
    accuracy = float(accuracy_score(y_test, y_pred))

    # Re-fit on the full dataset for better inference behavior in app.
    pipeline.fit(df["clean_text"], df["label"])
    return ModelBundle(pipeline=pipeline, accuracy=accuracy)


def extract_urls(text: str) -> list[str]:
    return re.findall(r"https?://[^\s]+|www\.[^\s]+", text.lower())


def url_risk(url: str) -> str:
    risky_tokens = ["bit.ly", "tinyurl", "free", "verify", "login", "gift", "ru/"]
    if any(token in url for token in risky_tokens):
        return "high"
    if len(url) > 70 or url.count("-") >= 3:
        return "medium"
    return "low"


def sender_reputation(sender: str) -> str:
    value = sender.strip().lower()
    if not value:
        return "unknown"
    if any(domain in value for domain in KNOWN_SENDERS):
        return "trusted"
    if any(hint in value for hint in BAD_SENDER_HINTS):
        return "suspicious"
    if re.search(r"\d{5,}", value):
        return "suspicious"
    return "neutral"


def detect_categories(text: str) -> list[str]:
    text_low = text.lower()
    hits = [cat for cat, words in CATEGORY_RULES.items() if any(w in text_low for w in words)]
    return hits or ["general spam"]


def highlight_terms(text: str) -> str:
    parts = []
    for token in re.split(r"(\W+)", text):
        if token.lower() in SUSPICIOUS_TERMS:
            parts.append(f"<mark>{token}</mark>")
        else:
            parts.append(token)
    return "".join(parts)


def suspicious_term_count(text: str) -> int:
    words = re.findall(r"\b\w+\b", text.lower())
    return sum(1 for w in words if w in SUSPICIOUS_TERMS)


def combine_risk_score(spam_probability: float, sender_rep: str, url_findings: list[tuple[str, str]], term_count: int) -> float:
    score = spam_probability * 100

    if sender_rep == "suspicious":
        score += 12
    elif sender_rep == "trusted":
        score -= 6

    high_url_count = sum(1 for _, level in url_findings if level == "high")
    med_url_count = sum(1 for _, level in url_findings if level == "medium")
    score += high_url_count * 12
    score += med_url_count * 6

    score += min(term_count * 2, 12)
    return max(0.0, min(score, 100.0))


def explain_prediction(
    text: str,
    spam_prob: float,
    sender_rep: str,
    url_findings: list[tuple[str, str]],
    final_risk_score: float,
) -> list[str]:
    reasons = []
    term_hits = [t for t in re.findall(r"\b\w+\b", text.lower()) if t in SUSPICIOUS_TERMS]

    if term_hits:
        reasons.append(f"Suspicious vocabulary: {', '.join(sorted(set(term_hits))[:10])}.")

    if spam_prob > 0.8:
        reasons.append("ML model confidence is very high for spam/scam language patterns.")
    elif spam_prob > 0.55:
        reasons.append("ML model confidence is moderate; wording resembles known risky messages.")
    else:
        reasons.append("ML model confidence is low for spam-like wording.")

    if sender_rep == "suspicious":
        reasons.append("Sender identity pattern appears suspicious.")
    elif sender_rep == "trusted":
        reasons.append("Sender appears similar to a trusted institution domain.")

    if url_findings:
        risky_urls = [u for u, level in url_findings if level in {"high", "medium"}]
        if risky_urls:
            reasons.append(f"Detected potentially risky URL(s): {', '.join(risky_urls[:2])}.")

    reasons.append(f"Combined risk score: {final_risk_score:.1f}/100 after ML + rule-based checks.")
    return reasons


bundle = train_and_evaluate_model()
model = bundle.pipeline

st.title("📨 AI SMS/Email Spam & Scam Detector")
st.caption("Hybrid AI + rule engine for phishing, OTP fraud, banking scam, and lottery-style spam detection.")

with st.expander("Project Build Plan Mapping", expanded=False):
    st.markdown(
        """
- **Phase 1 (Basic Model):** dataset load + text cleaning + TF-IDF + Logistic Regression + holdout accuracy.
- **Phase 2 (Smart Detection):** suspicious keywords + URL checks + combined risk score.
- **Phase 3 (Streamlit App):** text box + predict button + risk meter + explanation panel + dashboard.
- **Phase 4 (Advanced Upgrade):** hooks for BERT/chrome extension/deployment (documented in README).
        """
    )

st.sidebar.header("Model Snapshot")
st.sidebar.metric("Holdout Accuracy (Phase 1)", f"{bundle.accuracy * 100:.1f}%")
st.sidebar.caption("Accuracy is estimated on a small in-project sample dataset.")

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
    url_findings = [(u, url_risk(u)) for u in urls]
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
