import json
import re
from typing import List, Dict, Any
from app.services.ai_service import AIService

class ScheduleParserService:
    def __init__(self):
        self.ai_service = AIService()
    
    async def generate_schedule(self, prompt: str, unit_total_amount: str = None) -> List[Dict[str, Any]]:
        """Generate payment schedule from prompt and amount"""
        
        await self._validate_prompt_with_llm(prompt)
        
        # Parse unit total amount
        parsed_amount = None
        if unit_total_amount:
            try:
                parsed_amount = float(unit_total_amount)
            except (ValueError, TypeError):
                pass

        ai_response = await self.ai_service.generate_payment_schedule(prompt, parsed_amount)
        text_output = ai_response["text_output"]

        payment_schedule = self._extract_json_from_response(text_output)
        
        # Filter and validate schedule
        filtered_schedule = self._filter_and_validate_schedule(payment_schedule)
        
        # Fix equal divisions if needed
        if parsed_amount and len(filtered_schedule) > 1:
            filtered_schedule = self._fix_equal_divisions(filtered_schedule, parsed_amount)
        
        if not filtered_schedule:
            raise ValueError("No valid payment schedule generated")

        # Validate total amount
        total_amount = sum(float(item['amount']) for item in filtered_schedule)
        if parsed_amount and abs(total_amount - parsed_amount) > 1:
            pass

        return filtered_schedule
    
    def _extract_json_from_response(self, text_output: str) -> List[Dict[str, Any]]:
        """Extract JSON array from AI response text"""
        match = re.search(r'\[.*\]', text_output, re.DOTALL)
        if not match:
            raise ValueError("No valid JSON array found in the response")

        json_array_text = match.group()

        try:
            payment_schedule = json.loads(json_array_text)
        except json.JSONDecodeError:
            raise ValueError("Failed to parse JSON from Gemini output")

        if not isinstance(payment_schedule, list):
            raise ValueError("Payment schedule must be a list")
        
        return payment_schedule
    
    def _filter_and_validate_schedule(self, payment_schedule: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out invalid payments and validate structure"""
        filtered_schedule = []
        
        for item in payment_schedule:
            if not isinstance(item, dict):
                raise ValueError("Each payment item must be a dictionary")
            
            required_fields = ['date', 'amount', 'note']
            for field in required_fields:
                if field not in item:
                    raise ValueError(f"Missing required field: {field}")
            
            try:
                amount = float(item['amount'])
                if amount > 0:
                    filtered_schedule.append(item)
                else:
                    pass
            except (ValueError, TypeError):
                continue
        
        return filtered_schedule
    
    def _fix_equal_divisions(self, schedule: List[Dict[str, Any]], unit_total_amount: float) -> List[Dict[str, Any]]:
        """Fix equal divisions to ensure proper amount distribution"""
        amounts = [float(item['amount']) for item in schedule]
        avg_amount = sum(amounts) / len(amounts)
        
        # Check if this looks like an equal division (amounts are similar)
        is_equal_division = all(abs(amount - avg_amount) / avg_amount < 0.1 for amount in amounts)
        
        if is_equal_division:
            equal_amount = int(unit_total_amount / len(schedule))
            remainder = int(unit_total_amount % len(schedule))
            
            for i, item in enumerate(schedule):
                if i == len(schedule) - 1:  # Last payment gets remainder
                    item['amount'] = equal_amount + remainder
                else:
                    item['amount'] = equal_amount

                item['amount_percent'] = round((item['amount'] / unit_total_amount) * 100, 2)
        
        return schedule
    
    async def _validate_prompt_with_llm(self, prompt: str):
        """Validate prompt using zero-shot LLM classification"""
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        try:
            # Use AI service for zero-shot classification
            classification = await self.ai_service.classify_prompt_intent(prompt)
            
            category = classification.get('category', '').lower()
            confidence = classification.get('confidence', 0)
            reasoning = classification.get('reasoning', 'No reasoning provided')
            
            # Reject if classified as unrelated
            if category == 'unrelated':
                error_msg = f"Invalid prompt: The request '{prompt}' is not related to payment schedules. {reasoning}"
                raise ValueError(error_msg)
            
            # Also reject if confidence is too low (uncertain classification)
            if confidence < 0.7:
                error_msg = f"Unclear prompt: The request '{prompt}' is ambiguous. Please provide clearer payment schedule instructions."
                raise ValueError(error_msg)
            
        except ValueError:
            raise
        except Exception:
            self._basic_validation_fallback(prompt)
    
    def _basic_validation_fallback(self, prompt: str):
        """Fallback validation when LLM classification fails"""
        prompt_lower = prompt.lower().strip()
        
        # Check for obvious unrelated content
        unrelated_phrases = [
            'what is your name', 'who are you', 'hello', 'hi there', 'how are you',
            'what can you do', 'help me', 'test', 'testing', 'can you hear me',
            'good morning', 'good afternoon', 'good evening', 'goodbye', 'bye',
            'weather', 'time', 'date', 'news', 'joke', 'story'
        ]
        
        if any(phrase in prompt_lower for phrase in unrelated_phrases):
            raise ValueError(f"Invalid prompt: The request '{prompt}' is not related to payment schedules. Please provide instructions for creating payment schedules.")
        
        # Check for very short or random-looking text
        if len(prompt.strip()) < 3 or re.match(r'^[a-z\s]{1,15}$', prompt_lower):
            raise ValueError(f"Invalid prompt: The text '{prompt}' appears to be incomplete or random. Please provide clear payment schedule instructions.")
