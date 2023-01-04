import sqlite3
from scraper import scrape

def main():
    # create db if not exists
    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS recipes
                    (name text, website text NOT NULL UNIQUE, servings real, prep_time float64, cook_time float64, calories real, fat real, carbs real, protein real, ingredients text)''')
    conn.commit()
    recipe_curr = scrape('https://www.allrecipes.com/recipe/14685/slow-cooker-beef-stew-i/')
    c.execute('INSERT INTO recipes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (recipe_curr['name'], recipe_curr['website'], recipe_curr['servings'], recipe_curr['prep_time'], recipe_curr['cook_time'], recipe_curr['calories'], recipe_curr['fat'], recipe_curr['carbs'], recipe_curr['protein'], str(recipe_curr['ingredients'])))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()