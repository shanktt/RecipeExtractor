from bs4 import BeautifulSoup
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Optional
import instructor
import requests
import json


def get_url_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    data = requests.get(url, headers=headers)
    return data.content


def get_json_ld_tags(html_content):
    tags = []

    soup = BeautifulSoup(html_content, "html.parser")
    script_tags = soup.find_all("script", type="application/ld+json")

    for tag in script_tags:
        try:
            data = json.loads(tag.string)
            tags.append(data)
        except json.JSONDecodeError as e:
            print(e)

    return tags


class Ingredient(BaseModel):
    """An ingredient for a recipe"""

    name: str
    amount: str
    notes: Optional[str] = Field(
        ...,
        description="Any notes about the ingredient listed by the recipe. Only present if the the recipe actually has notes pertaining to the ingredient",
    )


class Recipe(BaseModel):
    """A class representing a recipe"""

    name: str
    ingredients: List[Ingredient]
    recipe_steps: List[str] = Field(..., description="A list of steps for a recipe. Make sure to put different steps into separate entries")


def get_recipe(tags):
    client = instructor.patch(OpenAI())
    return client.chat.completions.create(
        # model="gpt-4-turbo-preview",
        model="gpt-3.5-turbo-0125",
        response_model=Recipe,
        max_retries=4, 
        messages=[
            {
                "role": "user",
                "content": f"Extract the recipe from the following json-ld tags: {tags}",
            },
        ],
    )


# url = "https://cooking.nytimes.com/recipes/11519-kim-seversons-italian-meatballs?algo=identity&fellback=false&imp_id=1324904296764802&req_id=4377013278008448&surface=cooking-search-web&variant=holdout_cooking-search"
url = "https://www.halfbakedharvest.com/better-than-takeout-dan-dan-noodles/"
# url = "https://www.delscookingtwist.com/sesame-soba-noodles-with-mushrooms/"
# url = "https://www.adve:42nturesofanurse.com/instant-pot-crack-chicken/"

if __name__ == "__main__":
    content = get_url_content(url)
    tags = get_json_ld_tags(content)
    # print(tags)
    recipe = get_recipe(tags)
    print(recipe)
