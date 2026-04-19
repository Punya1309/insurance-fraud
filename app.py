from flask import Flask, request, jsonify, render_template
from openai import OpenAI

app = Flask(__name__)
client = OpenAI()

# ✅ Valid insurers
valid_companies = [
    "LIC", "HDFC Life", "ICICI Prudential", "SBI Life", "Max Life"
]

# 🚨 Suspicious keywords
suspicious_words = [
    "guaranteed returns",
    "no risk",
    "double your money",
    "100% profit",
    "limited time offer"
]

# 🧠 Rule-based scoring
def rule_based_score(text):
    score = 0
    issues = []
    text_lower = text.lower()

    for word in suspicious_words:
        if word in text_lower:
            score += 20
            issues.append(f"Suspicious phrase: {word}")

    if "policy" not in text_lower:
        score += 15
        issues.append("Missing policy details")

    if not any(company.lower() in text_lower for company in valid_companies):
        score += 25
        issues.append("Unrecognized insurer")

    return score, issues


# 🤖 AI Analysis
def analyze_with_ai(text):
    prompt = f"""
You are an expert insurance fraud detection assistant.

Analyze this policy:

{text}

Return:

Risk Score: (0-100)
Verdict: (Genuine / Needs Verification / Suspicious)
Key Issues:
- ...
Positive Signs:
- ...
Explanation:
...
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI analysis failed: {str(e)}"


# 🌐 Routes
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "No input provided"}), 400

    rule_score, issues = rule_based_score(text)
    ai_result = analyze_with_ai(text[:3000])

    final_score = min(rule_score + 40, 100)

    return jsonify({
        "score": final_score,
        "issues": issues,
        "ai": ai_result
    })


if __name__ == "__main__":
    app.run(debug=True)
