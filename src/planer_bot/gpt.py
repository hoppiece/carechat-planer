from jinja2 import Environment, FileSystemLoader, Template
from functools import lru_cache
from pathlib import Path
from openai import OpenAI


@lru_cache
def get_template(template_name: str) -> Template:
    base_dir = Path(__file__).resolve().parent
    template_dir = base_dir / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    return env.get_template(template_name)


def anwer_to_care_planer(openai_client: OpenAI, answers: dict) -> str:
    system_prompt = get_template("careplan_system_prompt.j2").render()
    user_prompt = get_template("careplan_user_prompt.j2").render(answers)

    completion = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    )
    careplan_text = completion.choices[0].message.content
    if careplan_text:
        return careplan_text
    else:
        return ""


def answer_to_user_prompt_from_secretary(openai_client: OpenAI, user_query: str) -> str:
    system_prompt = get_template("secretary_system_prompt.j2").render()

    response = openai_client.chat.completions.create(
        model="gpt-4o-search-preview",
        web_search_options={
            "search_context_size": "medium",  # 検索深度
            "user_location": {
                "type": "approximate",
                "approximate": {
                    "country": "JP",  # 地域
                },
            },
        },
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
        ],
    )
    answer_text = response.choices[0].message.content
    if answer_text:
        return answer_text
    else:
        return ""
