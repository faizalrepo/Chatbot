from rich import print
import os
from openai import OpenAI
from datasets import Dataset, DatasetDict, load_dataset
import json
from huggingface_hub import login

from rich.progress import track
from rich.console import Console
from rich.status import Status

console = Console()

# topic = "Conversation between a payee and a Chatbot which helps, negotiates and convinces payees only to pay - full payment and payment plan (payment plan could include discounts if applicable), record promise, record callback, and record disputes, not more than that. "
# n_subtopics = 20    
n_questions = 25

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

# 1. Subtopics Generation

# TOPIC_GENERATION_PROMPT_TEMPLATE = """\
# Given a topic, generate a list of {n_subtopics} phrased subtopics for finetuning chatbot that are related to the long topic.

# The long topic is: {topic}

# The list must be without numbers, and without any description of the subtopics. The subtopics should be separated by a comma. There must be no other text than the list.
# """

# def generate_subtopics(client, topic, n_subtopics):
#     prompt = TOPIC_GENERATION_PROMPT_TEMPLATE.format(topic=topic, n_subtopics=n_subtopics)
#     response = client.chat.completions.create(
#         model="meta/llama-3.1-405b-instruct",#i was
#         messages=[
#             {"role": "user",
#              "content": prompt}
#         ],
#         temperature=0.2,
#         top_p=0.7,
#         max_tokens=1024,
#     )
#     return response

# responses = generate_subtopics(client, topic=topic, n_subtopics=n_subtopics)
# print("\n1. < Subtopics Generation >\n\n", responses.choices[0].message.content, "\n")

# 2. Questions Generation

subtopic = "Outstanding Debt Overview, Full Payment Option, Payment Plan Durations, Weekly Instalment Eligibility, Fortnightly Instalment Availability, Monthly Instalment Terms, Last Payment Date Clarifications, Discount Policy Details, Payment Methods Allowed, Promise-to-Pay Conditions, Callback Scheduling Process, Debt Breakdown Information, Dispute Handling Procedures, How Instalment Schedules are Structured, Available Benefits for Early Payments, Negotiating Instalment Options, Unable to Pay Today Scenarios, Scheduling Assistance with an Expert, Steps to Adjust Payment Timing, Discount Eligibility Timelines"

QUESTION_PROMPT_TEMPLATE = """\
Given a question topic, generate {n_questions} questions that would be asked by a debt payee to the payee assistant who handles payments, and other queries by the payee. Your response should be in a list format.

The topic is: {sub_topic}

The list must be without numbers. The questions should be separated by a newline character. The list alone - There must be no other text than the list.
"""
subtopic_list = subtopic.split(",")
def generate_questions(client, sub_topic, n_questions):
    prompt = QUESTION_PROMPT_TEMPLATE.format(sub_topic=sub_topic, n_questions=n_questions)
    response = client.chat.completions.create(
        model="meta/llama-3.1-405b-instruct",
        messages=[
            {"role": "user",
             "content": prompt}
        ],
        temperature=0.2,
        top_p=0.7,
        max_tokens=1024,
    )
    # print("\n2. < Questions Generation >\n\n", responses.choices[0].message.content, "\n")
    return response.choices[0].message.content

def question_generator(client, subtopic_list, n_question):
    tasks = []
    console.log("\n")
    for subtopic in track(subtopic_list, description="Generating questions"):
        task = generate_questions(client, subtopic, n_question)
        tasks.append(task)
    return tasks

question_list = question_generator(client, subtopic_list, n_questions)
print(question_list)

question_list_formatted = []
for question_set in question_list:
    question_list_formatted.extend([question.strip() for question in question_set.split("\n") if question])
len(question_list_formatted)

# 3. Responses Generation

RESPONSE_PROMPT_TEMPLATE = """\
Given a question, generate two responses that a payee assistant (who handles payments, and other queries by the payee) would respond. The instructions given to the payee assistant:

'Your primary focus is to encourage users to settle their debts promptly. Always respond in US English, ensuring your responses are friendly and supportive, while strictly adhering to payment rules. Offer payment plans, initially starting from today, with instalments that are equal and limited to weekly, fortnightly, or monthly frequencies. Present plans sequentially, starting with the shortest duration, and highlight the benefits of faster payments, mentioning discounts only if the user shows interest. Allow only Card or ACH payments for transactions and encourage full payment whenever possible. If a user cannot pay immediately, guide them toward making a promise for full payment within a timeframe, ensuring the date does not exceed this timeline. If the user cannot make a promise, offer to schedule a callback with an expert to discuss payment options. If a user cannot pay today, guide them through the process of adjusting their payment timing. If a user is eligible for a discount, explain the eligibility timelines. Handle any disputes professionally when triggered by the user.'

Your response should be in a list format, not more than 60 words per response.

The question is: {question}

The list must be in the format:

RESPONSE A: Response A text here
RESPONSE B: Response B text here
"""
def generate_responses(client, question):
    prompt = RESPONSE_PROMPT_TEMPLATE.format(question=question)
    response = client.chat.completions.create(
        model="meta/llama-3.1-405b-instruct",
        messages=[
            {"role": "user",
             "content": prompt}
        ],
        temperature=0.2,
        top_p=0.7,
        max_tokens=1024,
    )
    # print("\n3. < Responses Generation >\n\n", responses.choices[0].message.content, "\n")
    return response.choices[0].message.content

def response_generator(client, question_list):
    tasks = []
    console.log("\n")
    for question in track(question_list, description="Generating responses"):
        task = generate_responses(client, question)
        tasks.append(task)
    return tasks

question_response_list = response_generator(client, question_list_formatted)
question_response_pair_list = []
for question, response_set in zip(question_list_formatted, question_response_list):
    question_response_pair_list.append(
        {
            "question": question,
            "responses": {
                "response_a": {"response": response_set.split("RESPONSE B:")[0].replace("RESPONSE A:", "").strip()},
                "response_b": {"response": response_set.split("RESPONSE B:")[-1].split("\n\n")[0].strip()}
            },
        }
    )

with open('synthetic_data.jsonl', 'w') as f:
    for item in question_response_pair_list:
        f.write(json.dumps(item))
        f.write('\n')

messages = [
    {
        "role": "user",
        "content": "Hello!"
    },
    {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
    },
]

response = client.chat.completions.create(
    model="nvidia/nemotron-4-340b-reward",
    messages=messages,
)

print(response)

print(response.choices[0].logprobs.content)

def get_scores_from_response(openai_response_template):
    logprobs = openai_response_template.choices[0].logprobs.content
    score_dict = {}
    for score in logprobs:
        score_dict[score.token] = score.logprob
    return score_dict

print(get_scores_from_response(response))

def get_response_and_scores(client, model, question, response_content):
    messages = [
        {
            "role": "user",
            "content": question
        },
        {
            "role": "assistant",
            "content": response_content
        },
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    scores = get_scores_from_response(response)
    return scores

question_response_score_list = question_response_pair_list.copy()

def process_question_response_pairs(client, model, question_response_score_list):
    tasks = []
    results = []
    console.log("\n")
    
    for pair in track(question_response_score_list, description="Getting scores"):
        question = pair["question"]
        task_a = get_response_and_scores(client, model, question, pair["responses"]["response_a"]["response"])
        task_b = get_response_and_scores(client, model, question, pair["responses"]["response_b"]["response"])
        tasks.append((task_a, pair, "response_a"))
        tasks.append((task_b, pair, "response_b"))
        
    for task in track(tasks, description="Updating results"):
        result, question_response_pair, response_key = task
        question_response_pair["responses"][response_key].update(result)

process_question_response_pairs(client, "nvidia/nemotron-4-340b-reward", question_response_score_list)

threshold = 3.0

console.log("\n")

with console.status("[bold green]Saving results to file...") as status:
    with open(f'synthetic_data_with_scores_filtered-{threshold}.jsonl', 'w') as f:
        for item in track(question_response_score_list, description="Writing to file"):
            question = item["question"]
            response_a = item["responses"]["response_a"]
            response_b = item["responses"]["response_b"]
            response_a["question"] = question
            response_b["question"] = question
            if response_a["helpfulness"] < threshold and response_b["helpfulness"] < threshold:
                continue
            f.write(json.dumps(response_a))
            f.write('\n')
            f.write(json.dumps(response_b))
            f.write('\n')
        
login("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")
        
with open(f'synthetic_data_with_scores_filtered-{threshold}.jsonl', 'r') as f:
    data = [json.loads(line) for line in f]
dataset = Dataset.from_list(data)
dataset_dict = DatasetDict({"train": dataset})
dataset_dict.push_to_hub("not-faizal/test-dataset-prep-3")
# dataset_dict.save_to_disk(f"./preference-dataset-{threshold}.jsonl")