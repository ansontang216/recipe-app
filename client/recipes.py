import os
import mysql.connector

class recipes:

    def __init__(self):
        self.mycursor = self.connectToDatabase()
        self.startCLI(self.mycursor)
        

    def startCLI(self, cursor):
        openingMessage = """1. Login
                            2. Recipes
                            3. Recipe Reviews """

        firstResponse = input(openingMessage)

        if (firstResponse == "1"):
            signingIn = """ """
        
        elif (firstResponse == "2"):
            recipesMessage = """1. Find Recipe:
                                    11. Find Recipe by Name
                                    12. Find Recipe by Preparation/Cook Time
                                    13. Find Recipe by Cook Time/Total Time
                                2. Submit Recipe"""

            secondResponse = input(recipesMessage)

        elif (firstResponse == "3"):
            reviewsMessage = """1. Find Review:
                                    11. Find Review by Recipe
                                    12. Find Review by Author
                                2. Submit Recipe"""


    def connectToDatabase(self):
        conn = mysql.connector.connect(host = 'marmoset04.shoshin.uwaterloo.ca',
                  user = 'a32saini',
                  password = 'dbhty@zRCkIT5@LY4T^4',
                  database = 'Loyal',
                  use_pure=True)

        mycursor = conn.cursor()

        return mycursor


    def findRecipeByName(self, recipeName, mycursor):

        mycursor = conn.cursor()
        mycursor.execute("SELECT * From CleanRecipes WHERE Name like '%recipeName%' ")
        myresult = mycursor.fetchall()
        for x in myresult:
            print(x)
        return
    
    #def findRecipeByIngredients():

    #def findRecipesByCookTime():

    #def findRecipeByTotalTime():

    #def findInstructionsForRecipe():
    
    #def findIngredientsForRecipe()