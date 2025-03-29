
from jinja2 import Environment, FileSystemLoader, Template
from functools import lru_cache
from pathlib import Path

@lru_cache
def get_template(template_name: str) -> Template:
    base_dir = Path(__file__).resolve().parent
    template_dir = base_dir / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    return env.get_template(template_name)



def anwer_to_care_planer(openai_client, answers: dict) -> str:
    system_prompt = get_template("careplan_system_prompt.j2").render()
    user_prompt = get_template("careplan_user_prompt.j2").render(answers)

    completion = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": user_prompt,
            }
        ]
    )
    careplan_text = completion.choices[0].message.content
    if careplan_text:
        return careplan_text
    else:
        return ""

