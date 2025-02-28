
from jinja2 import Environment, FileSystemLoader

gpt_template = Environment(loader=FileSystemLoader(".")).get_template("careplan_prompt_v2.0.j2")

def anwer_to_care_planer(openai_client, answers: dict) -> str:
    system_prompt = gpt_template.render()

    user_input = "\n".join(
        [f"{key}: {value}" for key, value in answers.items()]
    )
    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": user_input,
            }
        ]
    )
    careplan_text = completion.choices[0].message.content
    if careplan_text:
        return careplan_text
    else:
        return ""


if __name__ == "__main__":
    import argparse
    import json

    import openai

    parser = argparse.ArgumentParser()
    parser.add_argument("--question-file", "-q", type=str)
    args = parser.parse_args()

    openai_client = openai.OpenAI()

    if args.question_file:
        with open(args.question_file, "r") as f:
            answers = json.load(f)
    else:
        answers ={
            "question_1": "歩行がつらくなり、デイサービスの利用が大変",
            "question_2": "ショートステイの利用を増やしたい",
            "question_3": "要介護2",
            "question_4": "特に指示なし",
            "question_5": "訪問介護",
            "question_6": "トイレまでの移動が大変",
            "question_7": "本人が一人で生活している（独居）",
            "question_8": "1割負担"
        }

    print(anwer_to_care_planer(openai_client, answers))
