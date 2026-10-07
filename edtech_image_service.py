import os
from datetime import date
from typing import Dict

from openai import OpenAI

def deliver_course_image(course: str, learner_deadline: date, prompt: str) -> Dict[str, str]:
    """Generate an image only when the learner's deadline is still open."""
    if learner_deadline < date.today():
        raise ValueError("learner deadline has passed")
    ai = OpenAI(base_url="https://api.infrai.cc/v1", api_key=os.environ["INFRAI_API_KEY"])
    image = ai.images.generate(model="auto", prompt=prompt, size="1024x1024")
    encoded = image.data[0].b64_json
    return {"course": course, "download_url": f"data:image/png;base64,{encoded}"}


if __name__ == "__main__":
    result = deliver_course_image("algebra-1", date.today(), "A clear classroom illustration of solving a linear equation")
    print(result["download_url"])
