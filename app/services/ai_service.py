import requests
import json
import re
from datetime import date
from app.core.config import settings

class AIService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
    
    async def generate_payment_schedule(self, prompt: str, unit_total_amount: float = None) -> dict:
        """Generate payment schedule using Gemini AI"""
        
        if not self.api_key or self.api_key == "PUT_YOUR_API_KEY_HERE":
            raise ValueError(" GEMINI_API_KEY is missing or not set properly")

        url = f"{settings.gemini_api_url}?key={self.api_key}"
        
        today = str(date.today())
        
        # Build prompt context
        prompt_context = f"Prompt: \"{prompt}\""
        if unit_total_amount:
            prompt_context += f"\nUnit Total Amount: ${unit_total_amount:,.2f} (ALWAYS use this as the total amount)"
            prompt_context += f"\nIMPORTANT: If the prompt mentions any different total amount, IGNORE it and use the Unit Total Amount of ${unit_total_amount:,.2f} instead."
        
        full_prompt = f"""
        You are a smart assistant helping real estate companies.

        Convert this payment instruction into a JSON payment schedule.

        {prompt_context}

        Use today's date: {today}

        CRITICAL Instructions:
        - ALWAYS use the Unit Total Amount provided above as the total amount for calculations
        - If the prompt mentions any different total amount, IGNORE it completely
        - Calculate individual payment amounts based on percentages of the Unit Total Amount only
        - If percentages aren't specified, create a reasonable payment schedule
        - For equal divisions, divide the Unit Total Amount evenly
        - DO NOT include any payment entries with 0 amount
        - Only include payments with positive amounts greater than 0

        CALCULATION RULES:
        - For equal divisions: amount_per_payment = total_amount / number_of_payments
        - Keep amounts equal for all payments in equal divisions
        - Example: 900000 ÷ 3 = 300000 each payment
        - Calculate percentages: percentage = (amount / total_amount) * 100
        
        Output format:
        [
          {{
            "date": "YYYY-MM-DD",
            "amount_percent": 33.33,
            "amount": 300000,
            "note": "1st payment"
          }},
          {{
            "date": "YYYY-MM-DD",
            "amount_percent": 33.33,
            "amount": 300000,
            "note": "2nd payment"
          }},
          {{
            "date": "YYYY-MM-DD",
            "amount_percent": 33.34,
            "amount": 300000,
            "note": "final payment"
          }}
        ]

        Make sure amounts are calculated correctly with the Unit Total Amount.
        IMPORTANT: Skip any payment entries where the calculated amount is 0.
        """

        payload = {
            "contents": [
                {
                    "parts": [{"text": full_prompt}]
                }
            ]
        }

        headers = {"Content-Type": "application/json"}

        response = requests.post(url, headers=headers, data=json.dumps(payload))

        if response.status_code != 200:
            raise ValueError(f"Gemini API returned error: {response.status_code}")

        result = response.json()

        try:
            text_output = result['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError, TypeError) :
            raise ValueError("Invalid response structure from Gemini")

        return {"text_output": text_output}
    
    async def classify_prompt_intent(self, prompt: str) -> dict:
        """Use zero-shot classification to determine if prompt is payment-related"""
        
        if not self.api_key or self.api_key == "PUT_YOUR_API_KEY_HERE":
            raise ValueError("GEMINI_API_KEY is missing or not set properly")

        url = f"{settings.gemini_api_url}?key={self.api_key}"
        
        classification_prompt = f"""
        You are a text classifier. Analyze the following user input and classify it into one of these categories:

        CATEGORIES:
        1. "payment_schedule" - Requests related to creating, splitting, or managing payment schedules, installments, or financial plans
        2. "unrelated" - Everything else (greetings, questions about you, random text, non-payment topics)

        USER INPUT: "{prompt}"

        EXAMPLES:
        - "Split into 3 equal payments" → payment_schedule
        - "Create monthly installments" → payment_schedule  
        - "Pay 30% upfront, rest later" → payment_schedule
        - "What is your name?" → unrelated
        - "Hello there" → unrelated
        - "hjwbdjhhv diubiwd" → unrelated
        - "Tell me a joke" → unrelated

        Respond with ONLY a JSON object in this exact format:
        {{
            "category": "payment_schedule" or "unrelated",
            "confidence": 0.95,
            "reasoning": "Brief explanation of why this category was chosen"
        }}
        """

        payload = {
            "contents": [
                {
                    "parts": [{"text": classification_prompt}]
                }
            ]
        }

        headers = {"Content-Type": "application/json"}

        response = requests.post(url, headers=headers, data=json.dumps(payload))

        if response.status_code != 200:
            raise ValueError(f"Gemini classification API returned error: {response.status_code}")

        result = response.json()

        try:
            text_output = result['candidates'][0]['content']['parts'][0]['text']
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', text_output, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in classification response")
            
            classification_result = json.loads(json_match.group())
            
            # Validate required fields
            required_fields = ['category', 'confidence', 'reasoning']
            for field in required_fields:
                if field not in classification_result:
                    raise ValueError(f"Missing required field in classification: {field}")
            
            return classification_result
            
        except (KeyError, IndexError, TypeError, json.JSONDecodeError):
            raise ValueError("Invalid classification response structure from Gemini")
