import requests
import re

def main():
    # right now this is just to test the scraper

    # get user input for website
    website = input("Enter a website to extract data from (leave blank for test): ")
    if not website:
        website = 'https://www.allrecipes.com/recipe/14685/slow-cooker-beef-stew-i/'

    print(scrape(website))

def scrape(website : str) -> dict:
    r = requests.get(website)
    if r.status_code != 200:
        print("Error: could not connect to website")
        return
    print(f'Connected to {website}')
    print(f'Status code: {r.status_code}')

    recipe_name = get_recipe_name(r.text)
    print(recipe_name)

    recipe = {'name': recipe_name, 'website': website}

    # get the nutrition facts from the response
    nutrition_facts = get_nutrition_facts(r.text)
    for key, value in nutrition_facts.items():
        recipe[key] = value
    print(nutrition_facts)
    ingredients = get_ingredients(r.text)
    if ingredients:
        for ingredient in ingredients:
            print(f'{ingredient["quantity"]} {ingredient["unit"]} {ingredient["name"]}')
        recipe['ingredients'] = ingredients
    else:
        print('No ingredients found')
    return recipe

def get_recipe_name(response_text : str) -> str:
    return response_text[re.search(r'article-heading mntl-text-block">\n', response_text).end():re.search(r'</h1>', response_text).start()]

def get_ingredients(response_text : str) -> list:
    ing_match = re.search(r'.mntl-structured-ingredients__list', response_text).start(), re.search(r'<!-- end: comp mntl-structured-ingredients -->', response_text).end()
    matches = []
    match_inds = []
    curr_ind = ing_match[0]
    spattern = re.compile(r'list-item')
    epattern = re.compile(r'</li>')
    while curr_ind < ing_match[1]:
        match_start = spattern.search(response_text, curr_ind).end()
        match_end = epattern.search(response_text, match_start).start()
        if match_start and match_end:
            if match_end > ing_match[1]:
                break
            match_str = response_text[match_start:match_end]
            quantity = match_str[re.search(r'quantity="true">', match_str).end():re.search(r'</span>', match_str).start()]
            match_str = match_str[re.search(r'</span>', match_str).end():]
            unit = match_str[re.search(r'unit="true">', match_str).end():re.search(r'</span>', match_str).start()]
            match_str = match_str[re.search(r'</span>', match_str).end():]
            name = match_str[re.search(r'name="true">', match_str).end():re.search(r'</span>', match_str).start()]
            matches.append({'quantity': quantity, 'unit': unit, 'name': name})
            match_inds.append({'start': match_start, 'end': match_end})
            curr_ind = match_inds[-1]['end']
    return matches

def get_nutrition_facts(response_text : str) -> dict:
    ind_servings = re.search(r'ervings Per Recipe</span>\n<span>', response_text).end()
    ind_cal = re.search(r'Calories</span>\n<span>', response_text).end()
    ind_fat = re.search(r'Total Fat</span>\n', response_text).end()
    ind_carb = re.search(r'Total Carbohydrate</span>\n', response_text).end()
    ind_prot = re.search(r'Protein</span>\n', response_text).end()

    servings = response_text[ind_servings:ind_servings+re.search(r'\d*', response_text[ind_servings:]).end()]
    calories = response_text[ind_cal:ind_cal+re.search(r'\d*', response_text[ind_cal:]).end()]
    fat = response_text[ind_fat:ind_fat+re.search(r'\d*', response_text[ind_fat:]).end()]
    carb = response_text[ind_carb:ind_carb+re.search(r'\d*', response_text[ind_carb:]).end()]
    prot = response_text[ind_prot:ind_prot+re.search(r'\d*', response_text[ind_prot:]).end()]

    return {'servings': servings, 'calories': calories, 'fat': fat, 'carbs': carb, 'protein': prot}

if __name__ == '__main__':
    main()