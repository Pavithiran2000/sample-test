from typing import Union

def validate_amount(amount: str) -> float:
    """Validate and convert amount string to float"""
    if not amount or not amount.strip():
        raise ValueError("Amount cannot be empty")
    
    try:
        # Remove commas and convert to float
        clean_amount = float(amount.replace(',', ''))
        if clean_amount <= 0:
            raise ValueError("Amount must be greater than 0")
        return clean_amount
    except (ValueError, TypeError):
        raise ValueError("Invalid amount format")

def format_currency(amount: Union[int, float]) -> str:
    """Format amount as currency string"""
    return f"${amount:,.2f}"

def clean_prompt(prompt: str) -> str:
    """Clean and validate prompt string"""
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty")
    return prompt.strip()
