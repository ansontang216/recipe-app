import os
import mysql.connector

class recipes:

    def __init__(self):
        self.mycursor = self.connectToDatabase()
        self.startCLI(self.mycursor)
        self.loggedIn = False
        

    def startCLI(self, cursor):

        loginResponse = input("Would you like to Log In/Sign Up? (Y/N)")

        if (loginResponse == "Y"):
            signingIn = """1. Sign In
                           2. Sign Up """
            
            signingInResponse = input(signingIn)

            if (signingInResponse == "1"):
                self.performSignIn()
            elif (signingInResponse == "2"):
                self.performSignUp()

        openingMessage = """1. Recipes """

        firstResponse = input(openingMessage)

        if (firstResponse == "1"):
            recipesMessage = """1. Find Recipe:
                                    11. Find Recipe by Name
                                    12. Find Recipe by Ingredients
                                    13. Find Recipe by Total Time
                                2. Submit Recipe"""

            recipesResponse = input(recipesMessage)

            if (recipesResponse == "11"):
                self.findRecipeByName()
            elif (recipesResponse == "12"):
                self.findRecipeByIngredients()
            elif (recipesResponse == "13"):
                self.findRecipeByTotalTime()
            elif (recipesResponse == "2"):
                self.submitRecipe()
            
        # Once recipes are found and presented to the user
        # The user can choose a recipe and then they will be 
        # presented with it's ingredients, instructions and 
        # They will get an Y/N option to view the reviews for the Recipe
        # They will also have the option to submit a review for the Recipe if they are logged in


    def connectToDatabase(self):
        conn = mysql.connector.connect(host = 'marmoset04.shoshin.uwaterloo.ca',
                  user = 'a32saini',
                  password = 'dbhty@zRCkIT5@LY4T^4',
                  database = 'project_28',
                  use_pure=True)

        mycursor = conn.cursor()
        return mycursor


    def findRecipeByName(self, recipeName, mycursor):

        mycursor.execute("SELECT * From CleanRecipes WHERE Name like '%{}%'".format(recipeName))
        myresult = mycursor.fetchall()

        recipesWithID = [] # add each recipe along with it's ID over here and present these to the user

        for x in myresult:
            print(x)
        return

    # def performSignIn(self):

    # def performSignUp(self):
    
    # def findRecipeByIngredients(self):

    # def findRecipesByCookTime(self):

    # def findRecipeByTotalTime(self):

    # def findInstructionsForRecipe(self):
    
    # def findIngredientsForRecipe(self)

    # def presentRecipeToUser(self):

    # def findReviewsForRecipe(self, recipeID):

    # def submitRecipe(self):

    # def submitReview(self):