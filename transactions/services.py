import json
from google import genai
import os


GEMINI_API_KEY = os.getenv("API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)


def scan_bill(image):

    image_bytes = image.read()

    prompt = """
    Analyze this bill or receipt.
    Extract the following information:
    1. Total amount paid.
    2. Expense category.
    3. Payment method.
    4. title
    Available categories:
    food, fuel, Shopping, health, shopping,
    travel, education, rent, bills,entertainment,groceries,personal,other.
    Available payment methods:
    cash, upi.
    If the payment method cannot be identified,
    return upi.
    Return only valid JSON with these fields:
    amount, category, payment_method,title.
    """

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=[
            prompt,
            {
                "inline_data": {
                    "mime_type": image.content_type,
                    "data": image_bytes
                }
            }
        ],
        config={
            "response_mime_type": "application/json"
        }
    )

    return json.loads(response.text)