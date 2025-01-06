from rich import print
import os
from openai import OpenAI
from datasets import Dataset, DatasetDict, load_dataset
import json

topic = "Conversation of a chatbot which helps, negotiates and convinces payees only to pay (with discounts if applicable), record promise, callback, and disputes."
n_subtopics = 2
n_questions = 2

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

# 1. Subtopics Generation

TOPIC_GENERATION_PROMPT_TEMPLATE = """\
Given a topic, generate a list of {n_subtopics} subtopics that are related to the topic.

The topic is: {topic}

The list must be without numbers, and without any description of the subtopics. The subtopics should be separated by a comma. There must be no other text than the list.
"""

def generate_subtopics(client, topic, n_subtopics):
    prompt = TOPIC_GENERATION_PROMPT_TEMPLATE.format(topic=topic, n_subtopics=n_subtopics)
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
    return response

responses = generate_subtopics(client, topic=topic, n_subtopics=n_subtopics)
print("\n1. < Subtopics Generation >\n\n", responses.choices[0].message.content, "\n")

# 2. Questions Generation

QUESTION_PROMPT_TEMPLATE = """\
Given a topic, generate {n_questions} questions that could be asked about that topic. Your response should be in a list format.

The topic is: {sub_topic}

The list must be without numbers. The questions should be separated by a newline character. There must be no other text than the list.
"""
subtopic_list = responses.choices[0].message.content.split(",")
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
    print(response.choices[0].message.content)
    return response.choices[0].message.content

def question_generator(client, subtopic_list, n_question):
    tasks = [generate_questions(client, subtopic, n_question) for subtopic in subtopic_list]
    question_list = tasks
    return question_list

question_list = question_generator(client, subtopic_list, n_questions)
print(question_list)

question_list_formatted = []
for question_set in question_list:
    question_list_formatted.extend([question.strip() for question in question_set.split("\n") if question])
len(question_list_formatted)