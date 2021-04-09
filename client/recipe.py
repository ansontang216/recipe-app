class recipe:

    def __init__(self, recipeName, recipeID, recipeNumber):
        self.recipeName = recipeName # to present to the user
        self.recipeID = recipeID # to select ingredients, instructions, reviews for recipe
        self.recipeNumber = recipeNumber # recipes will be numbered when presented to a user and they pick a number to pick a recipe
