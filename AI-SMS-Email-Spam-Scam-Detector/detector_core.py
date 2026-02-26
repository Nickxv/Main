import re
from dataclasses import dataclass


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
    pipeline: object
    accuracy: float
    precision: float
    recall: float
    f1: float


def clean_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"https?://\S+|www\.\S+", " urltoken ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text




def _load_ml_dependencies():
    import pandas as pd
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import Pipeline
    return pd, TfidfVectorizer, LogisticRegression, accuracy_score, precision_recall_fscore_support, train_test_split, Pipeline

def train_and_evaluate_model() -> ModelBundle:
    pd, TfidfVectorizer, LogisticRegression, accuracy_score, prfs, train_test_split, Pipeline = _load_ml_dependencies()

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
    precision, recall, f1, _ = prfs(
        y_test,
        y_pred,
        average="binary",
        zero_division=0,
    )

    pipeline.fit(df["clean_text"], df["label"])
    return ModelBundle(
        pipeline=pipeline,
        accuracy=accuracy,
        precision=float(precision),
        recall=float(recall),
        f1=float(f1),
    )


def extract_urls(text: str) -> list[str]:
    return re.findall(r"https?://[^\s]+|www\.[^\s]+", text.lower())


def url_risk(url: str) -> str:
    risky_tokens = ["bit.ly", "tinyurl", "free", "verify", "login", "gift", "ru/"]
    if any(token in url for token in risky_tokens):
        return "high"
    if len(url) > 70 or url.count("-") >= 3:
        return "medium"
    return "low"


def _extract_sender_domain(value: str) -> str:
    sender = value.strip().lower()
    sender = re.sub(r"^https?://", "", sender)
    sender = sender.split("/")[0]

    if "@" in sender:
        return sender.rsplit("@", 1)[-1]
    return sender


def _is_trusted_domain(domain: str) -> bool:
    return any(domain == trusted or domain.endswith(f".{trusted}") for trusted in KNOWN_SENDERS)


def sender_reputation(sender: str) -> str:
    value = sender.strip().lower()
    if not value:
        return "unknown"

    domain = _extract_sender_domain(value)
    if _is_trusted_domain(domain):
        return "trusted"

    if any(trusted in domain for trusted in KNOWN_SENDERS):
        return "suspicious"

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
    return sum(1 for word in words if word in SUSPICIOUS_TERMS)


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


def explain_prediction(text: str, spam_prob: float, sender_rep: str, url_findings: list[tuple[str, str]], final_risk_score: float) -> list[str]:
    reasons = []
    term_hits = [term for term in re.findall(r"\b\w+\b", text.lower()) if term in SUSPICIOUS_TERMS]

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
        risky_urls = [url for url, level in url_findings if level in {"high", "medium"}]
        if risky_urls:
            reasons.append(f"Detected potentially risky URL(s): {', '.join(risky_urls[:2])}.")

    reasons.append(f"Combined risk score: {final_risk_score:.1f}/100 after ML + rule-based checks.")
    return reasons
