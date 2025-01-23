import ollama
import re
from colorama import Fore, Style, init
import time
import sys
from datetime import datetime

init(autoreset=True)

user = input(f"\n\n{Style.BRIGHT + Fore.WHITE}Ask R1:\n\n{Style.RESET_ALL}")

# print("\n\n<<<<  R1 is thinking...  >>>>\n", end='', flush=True)
start_time = time.time()

def show_timer():
    print("\n")
    while True:
        elapsed = time.time() - start_time
        mins = int(elapsed // 60)
        secs = int(elapsed % 60)
        timer_text = f"{mins} min {secs} sec" if mins > 0 else f"{secs} sec"
        print(f"\r<<<<  R1 is thinking... | {timer_text}  >>>>", end='', flush=True)
        time.sleep(1)


from threading import Thread
timer_thread = Thread(target=show_timer)
timer_thread.daemon = True
timer_thread.start()

res = ollama.generate(
    model="deepseek-r1:1.5b",
    prompt = user,
)

text = res['response']

INNER_TEXT_COLOR = Style.DIM + Fore.WHITE  
OUTER_TEXT_COLOR = Style.BRIGHT + Fore.WHITE  

pattern = re.compile(r'<think>(.*?)</think>\s*(.*)', re.DOTALL)

def reduce_newlines(text):
    lines = text.splitlines()
    cleaned_lines = []
    
    for line in lines:
        if line.strip():
            cleaned_lines.append(line.strip())
        elif cleaned_lines and cleaned_lines[-1] != "":
            cleaned_lines.append("")
            
    return "\n".join(cleaned_lines)

if match := pattern.match(text):
    inner_text = match.group(1)
    outer_text = match.group(2)

    inner_text = re.sub(r'### (.*?)\n', r'\n\1\n', inner_text)
    inner_text = re.sub(r'\\\((.*?)\\\)', r'\1', inner_text)
    inner_text = re.sub(r'\\\[(.*?)\\\]', r'\n\1\n', inner_text)
    inner_text = re.sub(r'\\boxed{(.*?)}', r'[\1]', inner_text)

    
    outer_text = outer_text.replace(r'\[', '').replace(r'\]', '')
    outer_text = outer_text.replace(r'###', '>>')
    # outer_text = outer_text.replace(r'- ', '    ')
    outer_text = outer_text.replace(r'\(', '').replace(r'\)', '')
    outer_text = outer_text.replace(r'\text{', '').replace('}', '')
    outer_text = outer_text.replace(r'\,', '')
    outer_text = outer_text.replace(r'\times', 'x')
    outer_text = outer_text.replace(r'^2', '²')
    outer_text = outer_text.replace(r'**', '')
    outer_text = outer_text.replace(r'\mathrm{\;', '').replace(r'}', '')
    outer_text = outer_text.replace(r'\boxed{', '').replace('}', '')
    outer_text = outer_text.replace(r'\\', '')
    outer_text = outer_text.replace(r'\\rm{', '')

    outer_text = reduce_newlines(outer_text)

    separator = f"{INNER_TEXT_COLOR}{'-' * 80}{Style.RESET_ALL}"
    colored_output = (
        f"\n{separator}\n"
        f"\n{INNER_TEXT_COLOR}{inner_text.strip()}{Style.RESET_ALL}\n"
        f"\n{separator}\n\n"
        f"{OUTER_TEXT_COLOR}{outer_text}{Style.RESET_ALL}\n"
    )
    
    print("\n")
    print(colored_output)

# Calculate and display total time at the end
total_time = time.time() - start_time
total_mins = int(total_time // 60)
total_secs = int(total_time % 60)

if total_mins > 0:
    print(f"<<<<  Thought for {total_mins} min {total_secs} sec  >>>>\n")
else:
    print(f"<<<<  Thought for {total_secs} seconds  >>>>\n")
