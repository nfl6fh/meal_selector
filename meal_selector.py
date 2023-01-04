import sqlite3
import requests
import re

def main():
    # get user input for calories and macros
    calories = ''
    while not calories:
        calories = input('Enter the maximum number of calories you want to eat: ')
        try:
            calories = int(calories)
            if calories <= 0:
                print('Please enter a positive number')
                calories = ''
            elif calories >= 10000:
                print('Please enter a number less than 10000')
                calories = ''
        except ValueError:
            print('Please enter a number')
            calories = ''

    protein = ''
    while not protein:
        protein = input('Enter the minimum amount of protein you want to eat (input 1 to ignore): ')
        try:
            protein = int(protein)
            if protein <= 0:
                print('Please enter a positive number')
                protein = ''
            elif protein >= 1000:
                print('Please enter a number less than 1000')
                protein = ''
        except ValueError:
            print('Please enter a number')
            protein = ''
        
    fat = ''
    while not fat:
        fat = input('Enter the minimum amount of fat you want to eat (input 1 to ignore): ')
        try:
            fat = int(fat)
            if fat <= 0:
                print('Please enter a positive number')
                fat = ''
            elif fat >= 1000:
                print('Please enter a number less than 1000')
                fat = ''
        except ValueError:
            print('Please enter a number')
            fat = ''

    carbs = ''
    while not carbs:
        carbs = input('Enter the minimum amount of carbs you want to eat (input 1 to ignore): ')
        try:
            carbs = int(carbs)
            if carbs <= 0:
                print('Please enter a positive number')
                carbs = ''
            elif carbs >= 1000:
                print('Please enter a number less than 1000')
                carbs = ''
        except ValueError:
            print('Please enter a number')
            carbs = ''

    # connect to database
    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()
    # get all recipes that meet the criteria
    c.execute(f'SELECT * FROM recipes WHERE calories <= {calories} AND protein >= {protein} AND fat >= {fat} AND carbs >= {carbs} ORDER BY protein DESC LIMIT 10')
    recipes = c.fetchall()
    # print out the recipes
    print('Here are some recipes that meet your criteria:')
    for i, recipe in enumerate(recipes):
        print(f'{i+1}. {recipe[0]} \n\tServings: {recipe[3]} \n\tCalories: {recipe[6]} \n\tProtein: {recipe[9]} \n\tFat: {recipe[7]} \n\tCarbs: {recipe[8]}')
    conn.close()

    while True:
        # get user input for which recipe to choose
        choice = input('Enter the number of the recipe you want to choose (leave blank to quit): ')
        if not choice:
            break
        try:
            choice = int(choice)
            if choice <= 0 or choice > len(recipes):
                print(f'Please enter a number between 1 and {len(recipes)} inclusive')
            else:
                # get the recipe url
                url = recipes[choice-1][1]
                # get the recipe html
                try:
                    r = requests.get(url)
                except requests.exceptions.RequestException as e:
                    print(e)
                    break
                if r.status_code != 200:
                    print(f'Error: {r.status_code}')
                    break
                # get the recipe name
                name = recipes[choice-1][0]
                # get the recipe ingredients
                ingredients = recipes[choice-1][10][1:-1]
                ingredients = ingredients.split('}, {')

                prep_time = hours_to_formatted(recipes[choice-1][4])
                print(f'Prep time: {prep_time}')

                cook_time = hours_to_formatted(recipes[choice-1][5])
                print(f'Cook time: {cook_time}')

                # convert the ingredients to a list of string from format {'quantity': '1', 'unit': 'cup', 'name': 'chicken broth'}
                for i, ingredient in enumerate(ingredients):
                    # strip leading and trailing {}
                    ingredient = ingredient.strip('{}')
                    # print(ingredient)
                    curr_str = ingredient[re.search(r'\'quantity\': \'', ingredient).end():re.search(r', \'unit\':', ingredient).start()-1]
                    curr_str += ' '
                    curr_str += ingredient[re.search(r', \'unit\': \'', ingredient).end():re.search(r', \'name\':', ingredient).start()-1]
                    curr_str += ' '
                    curr_str += ingredient[re.search(r', \'name\': \'', ingredient).end():-1]
                    ingredients[i] = curr_str
                # get the recipe instructions
                instructions = re.findall(r'.mntl-sc-block-html">\n.*\n', r.text)
                for i, instruction in enumerate(instructions):
                    instructions[i] = instruction[22:-1]
                # print out the recipe
                print(f'{name} \nIngredients:')
                for ingredient in ingredients:
                    print(f'\t{ingredient}')
                print('Instructions:')
                for i, instruction in enumerate(instructions):
                    print(f'\t{i+1}. {instruction}')
        except ValueError:
            print('Please enter a number')


def hours_to_formatted(hours : float) -> str:
    """Converts hours to a formatted string of hours and minutes"""
    hours_int = int(hours)
    minutes = int((hours - hours_int) * 60)
    return f'{f"{hours_int} hours" if hours_int > 0 else ""}{" and " if hours_int > 0 and minutes > 0 else ""}{f"{minutes} minutes" if minutes > 0 else ""}'

if __name__ == '__main__':
    main()