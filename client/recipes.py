import os
import mysql.connector
from recipe import recipe

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

        mycursor = conn.cursor(dictionary=True)
        return mycursor


    def findRecipeByName(self, recipeName, mycursor):

        mycursor.execute("SELECT recipe_name, recipe_id From CleanRecipes WHERE recipe_name like '%{}%'".format(recipeName))
        myresult = mycursor.fetchall()

        recipesWithID = [] # add each recipe along with it's ID over here and present these to the user
        print("Pick a recipe from the following list:")

        i = 0
        for x in myresult:
            i+=1
            recipesWithID.append(recipe(x["recipe_name"], x["recipe_id"], i))
            
            print ("%i. %s" % (i, x["recipe_name"]))

        userPickedRecipe = int(input("Please select a recipe: "))
        recipeID = recipesWithID[userPickedRecipe - 1].recipeID
        
        self.getIngredientsAndInstructionsForRecipe(mycursor, recipeID)
        self.getReviewsForRecipe(mycursor, recipeID)

        return

    def findRecipeByIngredients(self, ingredients, mycursor):
        

    def getIngredientsAndInstructionsForRecipe(self, mycursor, recipeID):

        mycursor.execute("SELECT ingredient_number, ingredient_name From Ingredients WHERE recipe_id = '{}' ORDER BY ingredient_number ASC;".format(recipeID))
        myresult = mycursor.fetchall()
        
        for x in myresult:
            print ("%s. %s" % (x["ingredient_number"], x["ingredient_name"]))

        mycursor.execute(" SELECT step, description From Instructions WHERE recipe_id = '{}' ORDER BY step ASC;".format(recipeID))
        myresult = mycursor.fetchall()

        for x in myresult:
            print ("%s. %s" % (x["step"], x["description"]))

        return

    def getReviewsForRecipe(self, mycursor, recipeID):

        yesOrNoReviews = input("Would you like to view Reviews for this Recipe? (Y/N)")

        if (yesOrNoReviews == "Y"):
            filterByRating = input("Would you like to filter Reviews by Ratings? (Y/N)")

            if(filterByRating == "Y"):
                getMinimumRating = int(input("Select a minimum rating from 1-5 "))
            
                mycursor.execute(" SELECT rate, comment From Instructions WHERE recipe_id = '{}' and rate >= '{}';".format(recipeID, getMinimumRating))
                myresult = mycursor.fetchall()
                
                i = 0
                for x in myresult:
                    i = i + 1
                    print ("%i. %s" % (i, x["comment"]))

            elif(filterByRating == "N"):
                mycursor.execute(" SELECT rate, comment From Instructions WHERE recipe_id = '{}';".format(recipeID))
                myresult = mycursor.fetchall()
                
                i = 0
                for x in myresult:
                    i = i + 1
                    print ("%i. %s" % (i, x["comment"]))

        
    
    # def performSignIn(self):

    # def performSignUp(self):
    
    # def findRecipeByIngredients(self):

    # def findRecipeByTotalTime(self):

    # def submitRecipe(self):

    # def submitReview(self):