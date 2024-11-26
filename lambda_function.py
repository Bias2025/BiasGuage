import json
import os
import re
import string
from anthropic import Anthropic


def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r"http\S+|@\w+|#\w+|\d+", "", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    return " ".join(text.split()).lower()


def analyze_bias(text):
    try:
        client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        prompt = f"""Analyze this text for bias and return JSON with:
        {{"label": "Biased" or "Neutral",
        "score": 0.0-1.0 confidence score,
        "explanation": "brief explanation",
        "biased_terms": ["list", "of", "terms"]}}

        Text: "{text}"
        """

        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=150,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.content[0].text
        return json.loads(content)
    except Exception as e:
        return {"label": "Error", "score": 0, "explanation": str(e), "biased_terms": []}


def lambda_handler(event, context):

    headers = {
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST",
    }

    try:
        if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
            return {"statusCode": 200, "headers": headers, "body": ""}

        if event.get("requestContext", {}).get("http", {}).get("method") != "POST":
            return {
                "statusCode": 405,
                "headers": headers,
                "body": json.dumps({"message": "Method Not Allowed"}),
            }

        request_body = json.loads(event.get("body", "{}"))
        if not request_body.get("text"):
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"message": "Missing text"}),
            }

        texts = request_body.get("text")

        if isinstance(texts, str):
            texts = [texts]

        results = [
            {"original_text": text, "cleaned_text": clean, **analyze_bias(clean)}
            for text, clean in [(t, clean_text(t)) for t in texts]
        ]

        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": headers,
            "body": results,
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": str(e)}),
        }
