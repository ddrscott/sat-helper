import re
from openai import OpenAI

questions = None

def build_questions(src_path:str='docs/sat-reading-mod-1.md'):
    text = open(src_path, 'r').read()

    results = re.findall('(?:##\s)(\d+)\n(.*?)(?=\n##\s\d+|$)', text, re.DOTALL)

    questions = {}
    for idx, found in results:
        questions[idx] = found

    return questions

def build_prompt(num, answer):
    global questions
    if questions is None:
        questions = build_questions()
    text = questions[num]
    return f"""\
Given the following SAT practice question:
---
{text}
---
The student answered incorrectly with `{answer}`.
My student answered incorrectly with `{answer}`.
Please help explain how to get the correct answer, and possibly why the student chose `{answer}`,
instead of the correct answer.
"""

def generate_response(prompt):
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a SAT test prep assistant."},
            {"role": "user", "content": prompt}
        ],
        stream=True
    )
    parts = []
    for chunk in completion:
        for choice in chunk.choices:
            if choice.delta is None:
                continue
        part = chunk.choices[0].delta.content
        if part:
            parts.append(part)
        print(part, end='')

    return ''.join(parts)


def generate_all_responses(incorrect_answers:str="2a,3c,4c,6a,7c,8b,10a,11b,13d,14d,15b,17d,18a,25a,26a,27d,31d,33b"):
    answers = incorrect_answers.split(',')
    for answer in answers:
        num, ans = answer[:-1], answer[-1]
        prompt = build_prompt(num, ans)
        response = generate_response(prompt)
        open(f'docs/responses/{num}{ans}.md', 'w').write(response)
    

if __name__ == '__main__':
    generate_all_responses()
