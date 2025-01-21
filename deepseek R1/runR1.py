# import os
# from dotenv import load_dotenv
import ollama
# from langchain_community.llms import Ollama
# from langchain_ollama import OllamaLLM
import re
from colorama import Fore, Style, init

# load_dotenv()
init(autoreset=True)

user = input("\n\nAsk R1:\n\n")
print("\n\nR1: *thinking*")

res = ollama.generate(
    model="deepseek-r1:1.5b",
    # model="qwen2.5:3b",
    prompt = user,
    # system="only funny responses",
    # options={'num_predict': 50}
)
# print("\n",res['response'],"\n")

text = res['response']

INNER_TEXT_COLOR = Style.DIM + Fore.WHITE  # Grey (dim white)
OUTER_TEXT_COLOR = Style.BRIGHT + Fore.WHITE  # Bright white

# Regex to match tags and their contents
pattern = re.compile(r'(<think>)(.*?)(</think>)(.*)', re.DOTALL)

match = pattern.match(text)
if match := pattern.match(text):
    tag_open, inner_text, tag_close, outer_text = match.groups()

    # Formatting for headings (### Step 1: Some title)
    inner_text = re.sub(r'### (.*?)\n', rf'\n{Style.BRIGHT}\1{Style.RESET_ALL}\n', inner_text)
    
    # Formatting inline math expressions \( ... \)
    inner_text = re.sub(r'\\\((.*?)\\\)', rf'{Style.BRIGHT}\1{Style.RESET_ALL}', inner_text)
    
    # Formatting block math expressions \[ ... \]
    inner_text = re.sub(r'\\\[(.*?)\\\]', rf'\n{Style.BRIGHT}\1{Style.RESET_ALL}\n', inner_text)
    
    # Formatting boxed answers \boxed{...}
    inner_text = re.sub(r'\\boxed{(.*?)}', rf'[{Style.BRIGHT}\1{Style.RESET_ALL}]', inner_text)
    
    # Modify outer_text to:
    outer_text = re.sub(r'\*\*(.*?)\*\*', r'\1', outer_text)  # Remove bold (**) formatting
    outer_text = re.sub(r'\\\[(.*?)\\\]', r'\n\n\1\n\n', outer_text)  # Convert math blocks to  new lines
    
    # Apply other cleaning steps as needed
    outer_text = re.sub(r'\\text{(.*?)}', r'\1', outer_text)  # Remove \text{} commands
    outer_text = re.sub(r'\s*\\,\s*', ' ', outer_text)  # Clean up LaTeX spacing
    outer_text = re.sub(r'\\\((.*?)\\\)', r'\1', outer_text)  # Remove inline math
    outer_text = re.sub(r'\\times', 'x', outer_text)  # Replace multiplication
    outer_text = re.sub(r'\^2', '²', outer_text)  # Format squared
    outer_text = re.sub(r'\\boxed{(.*?)}', r'[\1]', outer_text)  # Format boxes
    outer_text = re.sub(r'\s+', ' ', outer_text)  # Normalize spaces
    outer_text = re.sub(r'\n\s*\n', '\n\n', outer_text)  # Clean line breaks
    outer_text = outer_text.strip()
    
    separator = f"{INNER_TEXT_COLOR}{'-' * 80}{Style.RESET_ALL}"
    colored_output = (
        f"\n{separator}\n"
        f"\n{INNER_TEXT_COLOR}{inner_text.strip()}{Style.RESET_ALL}\n"
        f"\n{separator}\n\n"
        f"{OUTER_TEXT_COLOR}{outer_text}{Style.RESET_ALL}\n"
    )
    
    print(colored_output)


# model = OllamaLLM(
#     model=os.getenv('OLLAMA_MODEL_1', ''),
#     # metadata={"num_predict": 50},
#     num_predict=50,
#     # num_ctx=50 
# )

# prompt_input = "Why did the tomato cry?"
# response = model.invoke(prompt_input)

# print("\n",response,"\n")