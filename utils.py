from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import Type, TypeVar, Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

T = TypeVar("T", bound=BaseModel)

def get_llm():
    """Returns a configured ChatOllama instance."""
    # Ensure you have ollama installed and have run: `ollama pull gemma:latest` (or your specific model)
    # The user requested 'gemma-3-4b', but standard tags are 'gemma:2b', 'gemma:7b', 'gemma2:2b', etc.
    # We will default to 'gemma2' as a robust recent option, or use the user's specific string if they have a custom model.
    return ChatOllama(model="gemma3:4b", temperature=0.2)

def get_gemini_llm():
    """Returns a configured ChatGoogleGenerativeAI instance."""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2,
        convert_system_message_to_human=True
    )

import time

def structured_generator(
    system_prompt: str, 
    user_prompt: str, 
    output_schema: Type[T],
    llm: Optional[BaseChatModel] = None
) -> T:
    """Generates structured output using an LLM with retry logic."""
    llm = llm or get_llm()
    parser = JsonOutputParser(pydantic_object=output_schema)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "{user_input}")
    ])
    
    chain = prompt | llm | parser
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
             # Invoke with the user prompt as a variable
            response = chain.invoke({"user_input": user_prompt})
            
            # Handle cases where LLM returns a list instead of a dict
            if isinstance(response, list):
                if len(response) == 1 and isinstance(response[0], dict):
                    print("Warning: LLM returned single-item list, unwrapping...")
                    response = response[0]
                elif len(response) > 0:
                    print(f"Warning: LLM returned {len(response)}-item list, using first item...")
                    response = response[0] if isinstance(response[0], dict) else response
                else:
                    raise ValueError("LLM returned empty list")
            
            # Validate response is a dict
            if not isinstance(response, dict):
                raise TypeError(f"Expected dict, got {type(response).__name__}: {response}")
            
            return output_schema(**response)
        except Exception as e:
            if "rate_limit" in str(e).lower() and attempt < max_retries - 1:
                print(f"Rate limit hit. Waiting 10s before retry {attempt + 1}/{max_retries}...")
                time.sleep(10)
            elif attempt < max_retries - 1:
                 print(f"Error: {e}. Retrying {attempt + 1}/{max_retries}...")
                 time.sleep(2)
            else:
                raise e
