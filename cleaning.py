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
    recipe_steps: List[str]


def get_recipe(tags):
    tags = """
    istItem', 'position': 5, 'name': 'Sesame Soba Noodles with Mushrooms'}]}, {'@type': 'WebSite', '@id': 'https://www.delscookingtwist.com/#website', 'url': 'https://www.delscookingtwist.com/', 'name': 'Del&#039;s cooking twist', 'description': 'Plant-based | Wholesome | Organic', 'publisher': {'@id': 'https://www.delscookingtwist.com/#organization'}, 'potentialAction': [{'@type': 'SearchAction', 'target': {'@type': 'EntryPoint', 'urlTemplate': 'https://www.delscookingtwist.com/?s={search_term_string}'}, 'query-input': 'required name=search_term_string'}], 'inLanguage': 'en-US'}, {'@type': 'Organization', '@id': 'https://www.delscookingtwist.com/#organization', 'name': "Del's cooking twist", 'url': 'https://www.delscookingtwist.com/', 'logo': {'@type': 'ImageObject', 'inLanguage': 'en-US', '@id': 'https://www.delscookingtwist.com/#/schema/logo/image/', 'url': 'https://www.delscookingtwist.com/wp-content/uploads/2021/04/Del_sCookingTwist-1200x1200-1.png', 'contentUrl': 'https://www.delscookingtwist.com/wp-content/uploads/2021/04/Del_sCookingTwist-1200x1200-1.png', 'width': 1200, 'height': 1200, 'caption': "Del's cooking twist"}, 'image': {'@id': 'https://www.delscookingtwist.com/#/schema/logo/image/'}, 'sameAs': ['https://www.facebook.com/pages/Dels-cooking-twist/158928514282620', 'https://twitter.com/delstwist', 'https://instagram.com/delscookingtwist', 'https://www.linkedin.com/company/15256060/', 'https://www.pinterest.com/delstwist/', 'https://www.youtube.com/channel/UCX4VXKZduK2vq8vYIe4IxwQ']}, {'@type': 'Person', '@id': 'https://www.delscookingtwist.com/#/schema/person/3e4febf518c8a60ed3c5ada91c175c91', 'name': 'Delphine Fortin', 'image': {'@type': 'ImageObject', 'inLanguage': 'en-US', '@id': 'https://www.delscookingtwist.com/#/schema/person/image/', 'url': 'https://secure.gravatar.com/avatar/8122edd2bbf8d95c97b17fc9d7111a2e?s=96&d=mm&r=g', 'contentUrl': 'https://secure.gravatar.com/avatar/8122edd2bbf8d95c97b17fc9d7111a2e?s=96&d=mm&r=g', 'caption': 'Delphine Fortin'}, 'description': 'Hi! I\'m a French girl living in Sweden. I have loved cooking, baking and creating new recipes ever since I was young. I love my treats sweet or salty, depending on my mood, but they have to be delicious with a possibly "twist", my personal touch actually. That\'s why I finally came to the point that I somehow had to share my recipes with you and try out to teach you this little cooking twist which is mine. Whatever the recipe, there is two things you have to think about when you\'re cooking: use the true ingredients (no sweeteners or light products, never ever) and think fresh (no frozen ingredients). Here is the best way to eat healthy! I also love travelling and try to get inspiration from other cultures, that\'s why I want to tips you about the best places to eat in Paris, Stockholm, or every other places I tried and loved! Hope you will like my recipes (but fore sure you will) and give me back \'your\' personal twist then!', 'sameAs': ['http://www.delscookingtwist.com'], 'url': 'https://www.delscookingtwist.com/author/del/'}, {'@context': 'https://schema.org/', '@type': 'Recipe', 'name': 'Sesame Soba Noodles with Mushrooms', 'description': 'These Japanese sesame soba noodles with mushrooms are a quick and easy Asian recipe, ready in 20 minutes or less. The noodles are tossed in an aromatic mushroom sesame-soy sauce and garnished with sesame. It makes a delicious vegetarian dinner, light and loaded with sweet and sour flavors.', 'author': {'@type': 'Person', 'name': 'Delphine Fortin'}, 'keywords': 'Sesame Soba Noodles', 'image': ['https://www.delscookingtwist.com/wp-content/uploads/2022/01/Sesame-Soba-Noodles-with-Mushrooms_4-225x225.jpg', 'https://www.delscookingtwist.com/wp-content/uploads/2022/01/Sesame-Soba-Noodles-with-Mushrooms_4-260x195.jpg', 'https://www.delscookingtwist.com/wp-content/uploads/2022/01/Sesame-Soba-Noodles-with-Mushrooms_4-320x180.jpg', 'https://www.delscookingtwist.com/wp-content/uploads/2022/01/Sesame-Soba-Noodles-with-Mushrooms_4.jpg'], 'url': 'https://www.delscookingtwist.com/sesame-soba-noodles-with-mushrooms/', 'recipeIngredient': ['10 ounces (280g) soba noodles', '⅓ cup (80 ml) soy sauce (or tamari sauce)', '3 Tablespoons toasted sesame oil', '2 Tablespoons rice vinegar', '1 Tablespoon sugar', 'Freshly ground black pepper', '1 Tablespoon ginger, freshly grated', '1 Tablespoon canola oil, for cooking', '2 small shallots, minced', '8 ounces (230g) wild mushrooms, roughly chopped*', '8 ounces (230g) cremini mushrooms, sliced*', '6-8 sprigs green onions sprig, thinly sliced', '3 Tablespoons black and/or white sesame seeds, slightly toasted'], 'recipeInstructions': [{'@type': 'HowToStep', 'text': 'Bring a large pot of water to a boil and cook the soba noodles for 4-5 minutes or just until tender, stirring occasionally with a fork so the noodles don&#8217;t clump. Drain in a colander and rinse well under cold water, tossing to remove the starch.', 'url': 'https://www.delscookingtwist.com/sesame-soba-noodles-with-mushrooms/#instruction-step-1'}, {'@type': 'HowToStep', 'text': 'While the noodles are cooking, in a medium bowl, whisk together the soy sauce, sesame oil, rice vinegar, sugar and black pepper. Add the fresh ginger and set aside.', 'url': 'https://www.delscookingtwist.com/sesame-soba-noodles-with-mushrooms/#instruction-step-2'}, {'@type': 'HowToStep', 'text': 'Heat canola oil in a large skillet placed over medium high heat, and once hot add shallots. Sauté for about one minute. Add mushrooms, half of the green onions, and cook for about 3-5 minutes, until mushrooms are tender and spring onions fragrant, stirring from time to time.', 'url': 'https://www.delscookingtwist.com/sesame-soba-noodles-with-mushrooms/#instruction-step-3'}, {'@type': 'HowToStep', 'text': 'Pour the soy and sesame sauce, cook for 30 seconds, then add the noodles, and toss until the noodles are heated through. Add the remaining green onion and half of the sesame seeds. Garnish with the remaining seeds and serve warm.', 'url': 'https://www.delscookingtwist.com/sesame-soba-noodles-with-mushrooms/#instruction-step-4'}], 'prepTime': 'PT10M', 'cookTime': 'PT10M', 'totalTime': 'PT20M', 'recipeYield': ['4', '4 servings'], 'recipeCategory': 'Savory', 'recipeCuisine': 'World Cuisine', 'suitableForDiet': 'VeganDiet', 'datePublished': '2022-01-28', '@id': 'https://www.delscookingtwist.com/sesame-soba-noodles-with-mushrooms/#recipe', 'isPartOf': {'@id': 'https://www.delscookingtwist.com/sesame-soba-noodles-with-mushrooms/#article'}, 'mainEntityOfPage': 'https://www.delscookingtwist.com/sesame-soba-noodles-with-mushrooms/'}]}
    """

    client = instructor.patch(OpenAI())
    return client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_model=Recipe,
        max_retries=5, 
        messages=[
            {
                "role": "user",
                "content": f"Extract the recipe from the following json-ld tags: {tags}",
            },
        ],
    )


# url = "https://cooking.nytimes.com/recipes/11519-kim-seversons-italian-meatballs?algo=identity&fellback=false&imp_id=1324904296764802&req_id=4377013278008448&surface=cooking-search-web&variant=holdout_cooking-search"
# url = "https://www.halfbakedharvest.com/better-than-takeout-dan-dan-noodles/"
url = "https://www.delscookingtwist.com/sesame-soba-noodles-with-mushrooms/"
# url = "https://www.adve:42nturesofanurse.com/instant-pot-crack-chicken/"

if __name__ == "__main__":
    content = get_url_content(url)
    tags = get_json_ld_tags(content)
    recipe = get_recipe(tags)
    print(recipe)
