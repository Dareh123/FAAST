from openai import OpenAI
import os
import json
import re

def get_llm_response(content: str, system_prompt: str = "") -> str:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )

    messages = []
    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })
    
    messages.append({
        "role": "user",
        "content": content
    })

    completion = client.chat.completions.create(
        model="openai/gpt-4.1-nano",
        messages=messages,
        temperature = 0.1
    )
    return completion.choices[0].message.content

def get_json_llm_response(content: str, system_prompt: str) -> dict:
    """
    Extracts JSON from an LLM response.
    
    Args:
        content: The user prompt to send to the LLM
        system_prompt: Optional system prompt to guide the LLM
        
    Returns:
        A dictionary parsed from the JSON in the LLM response
    """
    
    # Get the raw response from the LLM
    response = get_llm_response(content, system_prompt)
    
    # Try to extract JSON using regex pattern matching
    json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
    match = re.search(json_pattern, response)
    
    if match:
        # Extract the JSON content from the code block
        json_str = match.group(1)
    else:
        # If no code block is found, try to use the entire response
        json_str = response
    
    try:
        # Parse the JSON string into a Python dictionary
        return json.loads(json_str)
    except json.JSONDecodeError:
        # If parsing fails, return an empty dictionary
        return {}
