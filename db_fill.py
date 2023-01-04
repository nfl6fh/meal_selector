import sqlite3
from scraper import scrape
import requests
import re

def main():
    # create db if not exists
    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS recipes
                    (name text, website text NOT NULL UNIQUE, type text, servings real, prep_time float64, cook_time float64, calories real, fat real, carbs real, protein real, ingredients text)''')
    conn.commit()
    types = {
        'Slow Cooker': 'https://www.allrecipes.com/recipes/17253/everyday-cooking/slow-cooker/main-dishes/', 
        'Campus Cooking': 'https://www.allrecipes.com/recipes/157/everyday-cooking/campus-cooking/',
        'Meal Prep': 'https://www.allrecipes.com/recipes/14787/everyday-cooking/make-ahead/',
        'Everyday Leftovers': 'https://www.allrecipes.com/recipes/14503/everyday-cooking/everyday-leftovers/',
        'One Pot Meals': 'https://www.allrecipes.com/recipes/15436/everyday-cooking/one-pot-meals/',
        'Comfort Food': 'https://www.allrecipes.com/recipes/16099/everyday-cooking/comfort-food/',
        'Budget Cooking': 'https://www.allrecipes.com/recipes/15522/everyday-cooking/budget-cooking/',
        'Gourmet Recipes': 'https://www.allrecipes.com/recipes/1592/everyday-cooking/gourmet/'
        }
    for key, value in types.items():
        print(f'Getting recipes for {key}')
        recipes = get_recipes(value)
        for recipe in recipes:
            recipe_curr = scrape(recipe)
            if not recipe_curr:
                continue
            if recipe_curr['servings'] == '0':
                continue
            try:
                c.execute('INSERT INTO recipes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (recipe_curr['name'], recipe_curr['website'], key, recipe_curr['servings'], recipe_curr['prep_time'], recipe_curr['cook_time'], recipe_curr['calories'], recipe_curr['fat'], recipe_curr['carbs'], recipe_curr['protein'], str(recipe_curr['ingredients'])))
                conn.commit()
                print(f'Added {recipe_curr["name"]}')
            except sqlite3.IntegrityError:
                print(f'Error: {recipe_curr["name"]} already exists')
    conn.close()

def get_recipes(url: str) -> list:
    r = requests.get(url)
    urls = re.findall(r'href=".*" ', r.text[re.search(r'.fixedContent', r.text).start():])
    valid_urls = []
    for url in urls:
        if re.search(r'https://www.allrecipes.com/recipe/', url):
            valid_urls.append(url[6:-2])
    return valid_urls

if __name__ == '__main__':
    main()