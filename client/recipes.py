import mysql.connector
from mysql.connector.errors import Error
from recipe import recipe
from mining import mining
from sqlalchemy import create_engine
import pymysql
from scipy.sparse.linalg import svds
import pandas as pd
import numpy as np

class recipes:

    def __init__(self, loggedIn, profileID, username):
        self.loggedIn = loggedIn
        self.username = username
        self.profileID = profileID
        self.mycursor, self.database = self.connectToDatabase()
        self.startCLI()

    def startCLI(self):
        
        loginResponse = input("\nWould you like to Log In/Sign Up? (Y/N): ")
        loginResponse = self.inputValidater(loginResponse, ['Y', 'N', 'y', 'n'])
        
        if (loginResponse == "Y" or loginResponse == "y"):
            signingIn = """\n1. Sign In\n2. Sign Up \nPlease pick an option (1,2): """
            
            signingInResponse = input(signingIn)
            signingInResponse = self.inputValidater(signingInResponse, ['1', '2'])
            
            if (signingInResponse == "1"):
                self.performSignIn()
                if(self.loggedIn == False):
                    return
            elif (signingInResponse == "2"):
                self.performSignUp()
                if(self.loggedIn == False):
                    return
        else:
            self.loggedIn = False
            
        openingMessage = """\n1. Recipes\n2. Recommend recipes to me\nPlease pick an option (1,2): """
        
        firstResponse = input(openingMessage)
        firstResponse = self.inputValidater(firstResponse, ['1', '2'])
        
        if (firstResponse == "1"):
            recipesMessage = """\n1. Find Recipe:\n\t11. Find Recipe by Name\n\t12. Find Recipe by Ingredients\n\t13. Find Recipe by Total Time\n\t14. Search using all parameters\n2. Submit Recipe\n3. View and Edit your Recipes\nPlease pick an option (11,12,13,14,2,3): """

            recipesResponse = input(recipesMessage)
            recipesResponse = self.inputValidater(recipesResponse, ['11', '12', '13', '14', '2', '3'])
            if (recipesResponse == "11"):
                getRecipeName = input("\nPlease input the name of the recipe: ")
                self.findRecipeByName(getRecipeName)
            elif (recipesResponse == "12"):
                self.findRecipeByIngredients()
            elif (recipesResponse == "13"):
                self.findRecipeByTotalTime()
            elif (recipesResponse == "14"):
                self.fullSearchRecipes()
            elif (recipesResponse == "2"):
                self.submitRecipe()
            elif (recipesResponse == "3"):
                self.showUsersRecipes()


        elif (firstResponse == "2"):
            if (not self.loggedIn):
                print("You need to be logged in to have recipes recommended to you. Please Sign In/Sign Up.")
            else:
                if(not self.getNumOfReviews(self.profileID)):
                    print("You need to review at least 1 recipe to get recommendations. Check out some recipes and leave some reviews. The more reviews you leave - the better the recommendations!")
                else:
                    recommender = mining()
                    recommendedRecipes = recommender.recommend_recipes(self.profileID)
                    self.getRecipesFromDataframe(recommendedRecipes)

        return


    def connectToDatabase(self):
        conn = mysql.connector.connect(host = 'marmoset04.shoshin.uwaterloo.ca',
                  user = 'a32saini',
                  password = 'dbhty@zRCkIT5@LY4T^4',
                  database = 'project_28',
                  use_pure=True)

        mycursor = conn.cursor(dictionary=True, buffered=True)
        return mycursor, conn


    def findRecipeByName(self, recipeName):
        self.checkConn()
        
        recipeName = self.replaceApostrophe(recipeName)
        self.mycursor.execute("SELECT recipe_name, recipe_id From CleanRecipes WHERE recipe_name like '%{}%';".format(recipeName))
        myresult = self.mycursor.fetchall()

        if (len(myresult) == 0):
            print("There were no recipes by that name. Please restart and try a different name.")
            return

        recipesWithID = [] # add each recipe along with it's ID over here and present these to the user
        print("\nPick a recipe from the following list:\n")

        validResponse = []
        i = 0
        for x in myresult:
            i+=1
            validResponse.append(i)
            recipesWithID.append(recipe(x["recipe_name"], x["recipe_id"], i))
            
            print ("%i. %s" % (i, x["recipe_name"]))

        userPickedRecipe = int(input("\nPlease select a recipe: "))
        userPickedRecipe = self.inputValidaterInt(userPickedRecipe, validResponse)
        recipeID = recipesWithID[userPickedRecipe - 1].recipeID
        
        self.getIngredientsAndInstructionsForRecipe(recipeID)
        self.getReviewsForRecipe(recipeID)
        self.submitReview(recipeID)

        return

    def likeClauseForIngredients(self, ingredients):
        stringToReturn = ""
        
        for i in ingredients:
            i = self.replaceApostrophe(i)
            if (i != ingredients[-1]):
                recipeLike = "ingredients like '%{}%' AND ".format(i)
                stringToReturn = stringToReturn + recipeLike
            else:
                recipeLike = "ingredients like '%{}%'".format(i)
                stringToReturn = stringToReturn + recipeLike

        stringToReturn = stringToReturn
        return stringToReturn


    def findRecipeByIngredients(self):
        self.checkConn()
        getIngredients = input("\nPlease enter your ingredients separated by commas. (For eg: eggs, milk, sugar): ")
        ingredients = []
        ingredients = getIngredients.split(",")
        like = self.likeClauseForIngredients(ingredients)

        self.mycursor.execute( "SELECT recipe_name, recipe_id FROM CleanRecipes where recipe_id in (SELECT recipe_id From RecipeIngredients WHERE {});".format(like) )
        myresult = self.mycursor.fetchall()

        if (len(myresult) == 0):
            print("There were no recipes with that combination of Ingredients.")
            return

        recipesWithID = [] # add each recipe along with it's ID over here and present these to the user
        print("\nPick a recipe from the following list:\n")

        validResponse = []
        i = 0
        for x in myresult:
            i+=1
            validResponse.append(i)
            recipesWithID.append(recipe(x["recipe_name"], x["recipe_id"], i))
            
            print ("%i. %s" % (i, x["recipe_name"]))

        userPickedRecipe = int(input("\nPlease select a recipe: "))
        userPickedRecipe = self.inputValidaterInt(userPickedRecipe, validResponse)
        recipeID = recipesWithID[userPickedRecipe - 1].recipeID
        
        self.getIngredientsAndInstructionsForRecipe(recipeID)
        self.getReviewsForRecipe(recipeID)
        self.submitReview(recipeID)
        
        return


    def getIngredientsAndInstructionsForRecipe(self, recipeID):
        self.checkConn()
        self.mycursor.execute("SELECT ingredient_number, ingredient_name From Ingredients WHERE recipe_id = '{}' ORDER BY ingredient_number ASC;".format(recipeID))
        myresult = self.mycursor.fetchall()
        print("\nIngredients for Recipe: ")
        for x in myresult:
            print ("%s. %s" % (x["ingredient_number"], x["ingredient_name"]))

        self.mycursor.execute(" SELECT step, description From Instructions WHERE recipe_id = '{}' ORDER BY step ASC;".format(recipeID))
        myresult = self.mycursor.fetchall()
        print("\nInstructions for Recipe: ")
        for x in myresult:
            print ("%s. %s" % (x["step"], x["description"]))

        self.mycursor.execute(" SELECT prepare_time, cook_time From CleanRecipes WHERE recipe_id = '{}';".format(recipeID))
        time = self.mycursor.fetchall()

        print("\nPrep time: {} minutes".format(time[0]["prepare_time"]))
        print("Cooking time: {} minutes".format(time[0]["cook_time"]))

        return

    def getReviewsForRecipe(self, recipeID):
        self.checkConn()
        yesOrNoReviews = input("\nWould you like to view Reviews for this Recipe? (Y/N): ")
        yesOrNoReviews = self.inputValidater(yesOrNoReviews, ['Y', 'N', 'y', 'n'])
        if (yesOrNoReviews == "Y" or yesOrNoReviews == "y"):
            filterByRating = input("\nWould you like to filter Reviews by Ratings? (Y/N): ")
            filterByRating = self.inputValidater(filterByRating, ['Y', 'N', 'y', 'n'])
            if(filterByRating == "Y" or filterByRating == "y"):
                getMinimumRating = int(input("Select a minimum rating from 1-5 "))
                getMinimumRating = self.inputValidaterInt(getMinimumRating, [1, 2, 3, 4, 5])
                self.mycursor.execute(" SELECT rate, comment From CleanReviews WHERE recipe_id = '{}' and rate >= '{}';".format(recipeID, getMinimumRating))
                myresult = self.mycursor.fetchall()
                
                i = 0

                if(len(myresult) == 0):
                    print("\nThere are no reviews for this recipe.")
                else:

                    for x in myresult:
                        i = i + 1
                        print("\nRating: %i STARS" % (x["rate"]))
                        print ("%i. %s" % (i, x["comment"]))
                

            elif(filterByRating == "N" or filterByRating == "n"):
                self.mycursor.execute(" SELECT rate, comment From CleanReviews WHERE recipe_id = '{}';".format(recipeID))
                myresult = self.mycursor.fetchall()
                
                i = 0
                if(len(myresult) == 0):
                    print("\nThere are no reviews for this recipe.")
                else:
                    for x in myresult:
                        i = i + 1
                        print("\nRating: %i STARS" % (x["rate"]))
                        print ("%i. %s" % (i, x["comment"]))



    def performSignIn(self):
        self.checkConn()
        getUsername = input("\nPlease enter your username: ")
        getPassword = input("Please enter your password: ")
        getUsername = self.replaceApostrophe(getUsername)
        getPassword = self.replaceApostrophe(getPassword)
        self.mycursor.execute( "SELECT profile_id FROM Users where username = '{}' AND password = '{}';".format(getUsername, getPassword))
        myresult = self.mycursor.fetchall()
        if (len(myresult) == 0):
            print("Incorrect Username or Password. Please restart the app and try again.")
        else:
            self.username = getUsername
            self.profileID = myresult[0]["profile_id"]
            self.loggedIn = True

        return

    def doesUsernameExist(self, username):
        self.checkConn()
        self.mycursor.execute( "SELECT * FROM Users where username = '{}';".format(username) )
        myresult = self.mycursor.fetchall()

        newUsername = username

        if (len(myresult) != 0):
            newUsername = input("\nPlease enter another username, as this is already taken: ")
            self.doesUsernameExist(newUsername)
        else:
            return newUsername

    def performSignUp(self):
        self.checkConn()
        getUsername = input("\nPlease enter a username: ")
        newUsername = self.doesUsernameExist(getUsername)
        getPassword = input("Please enter a password: ")
        getUsername = self.replaceApostrophe(getUsername)
        getPassword = self.replaceApostrophe(getPassword)
        self.mycursor.execute( "INSERT INTO Users (username, password) VALUES ('{}','{}');".format(newUsername, getPassword) )
        self.database.commit()
        self.mycursor.execute( "SELECT profile_id FROM Users where username = '{}' AND password = '{}';".format(newUsername, getPassword))
        myresult = self.mycursor.fetchall()
        self.username = newUsername
        self.profileID = myresult[0]["profile_id"]
        self.loggedIn = True
        return

    def findRecipeByTotalTime(self):
        self.checkConn()
        getMaxTime = int(input("\nPlease enter the maximum amount of time in minutes: "))
        self.mycursor.execute( "SELECT recipe_name, recipe_id FROM CleanRecipes where total_time <= {};".format(getMaxTime) )
        myresult = self.mycursor.fetchall()
        if (len(myresult) == 0):
            print("There were no recipes by that time limit.")
            return
        recipesWithID = [] # add each recipe along with it's ID over here and present these to the user
        print("Pick a recipe from the following list:")

        validResponse = []
        i = 0
        for x in myresult:
            i+=1
            validResponse.append(i)
            recipesWithID.append(recipe(x["recipe_name"], x["recipe_id"], i))
            
            print ("%i. %s" % (i, x["recipe_name"]))

        userPickedRecipe = int(input("Please select a recipe: "))
        userPickedRecipe = self.inputValidaterInt(userPickedRecipe, validResponse)
        recipeID = recipesWithID[userPickedRecipe - 1].recipeID
        
        self.getIngredientsAndInstructionsForRecipe(recipeID)
        self.getReviewsForRecipe(recipeID)
        self.submitReview(recipeID)
        
        return


    def submitRecipe(self):
        self.checkConn()
        if (not (self.loggedIn)):
            print("\nYou are not logged in. Please restart the app and Sign in/Sign up.")
            return
        
        recipeName = input("\nPlease enter a name for your recipe: ")
        recipeName = self.replaceApostrophe(recipeName)
        reviewCount = 0
        author = self.username

        ingredientList = []
        ingredients = input("\nPlease input all ingredients, along with their amount, separated by commas: ")
        ingredients = self.replaceApostrophe(ingredients)
        ingredientList = ingredients.split(",")

        instructionsList = []

        print("\nPlease input instructions step by step. Once you are done, enter '1' ")

        while(True):
            instructionToAdd = input("Instruction: ")
            instructionToAdd = self.replaceApostrophe(instructionToAdd)
            if(instructionToAdd == "1"):
                break
            instructionsList.append(instructionToAdd)
        

        prepare_time = int(input("\nPlease enter the preparation time in minutes: "))
        cook_time = int(input("Please enter the cook time in minutes: "))
        total_time = prepare_time + cook_time
        self.mycursor.execute("INSERT INTO CleanRecipes (recipe_name, review_count, recipe_photo, author, prepare_time, cook_time, total_time) VALUES ('{}', '{}', 'no photo', '{}', '{}', '{}', '{}');".format(recipeName, reviewCount, author, prepare_time, cook_time, total_time))
        self.database.commit()

        self.mycursor.execute("SELECT max(recipe_id) as maxID FROM CleanRecipes")
        myresult = self.mycursor.fetchall()
        self.mycursor.execute("INSERT INTO RecipeIngredients (recipe_id, ingredients) VALUES ('{}','{}')".format(myresult[0]["maxID"], ingredients))

        ingredientNumber = 0
        for i in ingredientList:
            i = self.replaceApostrophe(i)
            ingredientNumber = ingredientNumber + 1
            self.mycursor.execute("INSERT INTO Ingredients (recipe_id, ingredient_number, ingredient_name) VALUES ('{}','{}', '{}')".format(myresult[0]["maxID"], ingredientNumber, i))
        self.database.commit()
        instructionNumber = 0
        for i in instructionsList:
            instructionNumber = instructionNumber + 1
            self.mycursor.execute("INSERT INTO Instructions (recipe_id, step, description) VALUES ('{}','{}', '{}')".format(myresult[0]["maxID"], instructionNumber, i))
        self.database.commit()
        return

    def submitReview(self, recipe_id):
        self.checkConn()
        getReviewsResponse = input("\nWould you like to leave a review for this recipe? (Y/N): ")
        getReviewsResponse = self.inputValidater(getReviewsResponse, ['Y','y','N','n'])
        if(getReviewsResponse == "N" or getReviewsResponse == "n"):
            return
        elif(getReviewsResponse == "Y" or getReviewsResponse == "y"):

            if (self.loggedIn == False):
                print("\nYou need to be logged in to be able to leave a review. Please restart the app and Sign In/Sign Up.")
                return
            else:
                getRating = int(input("\nPlease enter a rating from 1-5: "))
                getRating = self.inputValidaterInt(getRating, [1, 2, 3, 4, 5])
                getReviewComments = input("\nPlease enter some comments: ")
                getReviewComments = self.replaceApostrophe(getReviewComments)
                self.mycursor.execute("SELECT review_count FROM CleanRecipes WHERE recipe_id = '{}'".format(recipe_id))
                countResult = self.mycursor.fetchall()
                countReviews = 0
                countReviews = countResult[0]["review_count"] + 1
                self.mycursor.execute("UPDATE CleanRecipes SET review_count = '{}' WHERE recipe_id = '{}'".format(countReviews, recipe_id))
                self.mycursor.execute("INSERT INTO CleanReviews (recipe_id, profile_id, rate, comment) VALUES ('{}','{}','{}','{}')".format(recipe_id, self.profileID, getRating, getReviewComments))
                self.database.commit()
                self.mycursor.execute("SELECT numOfReviews FROM Users WHERE profile_id = '{}'".format(self.profileID))
                myresult = self.mycursor.fetchall()
                numReviews = 0
                numReviews = myresult[0]["numOfReviews"] 
                numReviews = numReviews + 1
                self.mycursor.execute("UPDATE Users SET numOfReviews = '{}' WHERE profile_id = '{}'".format(numReviews, self.profileID))
                self.database.commit()

    def getRecipesFromDataframe(self, recipes):
        self.checkConn()
        recipesWithID = [] # add each recipe along with it's ID over here and present these to the user
        print("\nPick a recipe from the following list:\n")

        i = 0
        validValues = []
        for index, x in recipes.iterrows():
            i+=1
            validValues.append(i)
            recipesWithID.append(recipe(x['recipe_name'], x['recipe_id'], i))
            
            print ("%i. %s" % (i, x['recipe_name']))

        userPickedRecipe = int(input("\nPlease select a recipe: "))
        userPickedRecipe = self.inputValidaterInt(userPickedRecipe, validValues)
        recipeID = recipesWithID[userPickedRecipe - 1].recipeID
        
        self.getIngredientsAndInstructionsForRecipe(recipeID)
        self.getReviewsForRecipe(recipeID)
        self.submitReview(recipeID)

        return

    def inputValidater(self, userInput, validInput):
        
        for x in validInput:
            if (userInput == x):
                return userInput
    
        reenterInput = input("\nPlease enter a valid input. Choose from {}: ".format(validInput))
        return self.inputValidater(reenterInput, validInput)

    def inputValidaterInt(self, userInput, validInput):
        
        for x in validInput:
            if (userInput == x):
                return userInput
            else:
                continue
        reenterInput = int(input("\nPlease enter a valid input. Choose from {}: ".format(validInput)))
        return self.inputValidater(reenterInput, validInput)

    def checkConn(self):
        sq = "SELECT NOW()"
        try:
            self.mycursor.execute( sq )
        except mysql.connector.Error as e:
            if e.errno == 2006:
                self.mycursor, self.database = self.connectToDatabase()
            else:
                print ( "No connection with database. Please check your internet connection and try again." )
        return

    def getNumOfReviews(self, profileID):
        self.checkConn()

        self.mycursor.execute( "SELECT numOfReviews FROM Users where profile_id = '{}';".format(profileID))
        myresult = self.mycursor.fetchall()
        if (len(myresult) == 0):
            print("Error: User doesn't exist. Restar the app and Sign Up")
            return
        else:
            numReviews = myresult[0]["numOfReviews"]

        if (int(numReviews) < 1):
            return False
        else:
            return True
    
    def replaceApostrophe(self, input):
        return input.replace("'", "")
    
    def fullSearchRecipes(self):
        self.checkConn()
        getRecipeName = input("\nPlease input the name of the recipe. Enter 'Any' to skip this: ")
        getRecipeName = self.replaceApostrophe(getRecipeName)

        getIngredients = input("\nPlease enter your ingredients separated by commas. Enter 'Any' to skip this. (For eg: eggs, milk, sugar): ")
        ingredients = []
        if(getIngredients == 'Any' or getIngredients == 'any'):
            like = "ingredients like '%%'"
        else:
            ingredients = getIngredients.split(",")
            like = self.likeClauseForIngredients(ingredients)

        getMaxTime = (input("\nPlease enter the maximum amount of time in minutes. Enter 'Any' to skip this: "))
        
        if(getMaxTime == 'Any' or getMaxTime == 'any'):
            getMaxTime = 99999999
        else:
            getMaxTime = int(getMaxTime)

        if(getRecipeName == 'Any' or getRecipeName == 'any'):
            getRecipeName = ""

        self.mycursor.execute( "SELECT recipe_name, recipe_id FROM CleanRecipes where recipe_name like '%{}%' AND total_time <= {} AND recipe_id IN (SELECT recipe_id From RecipeIngredients WHERE {});".format(getRecipeName, getMaxTime, like))

        myresult = self.mycursor.fetchall()
        if (len(myresult) == 0):
            print("There were no recipes by that time limit.")
            return
        recipesWithID = [] # add each recipe along with it's ID over here and present these to the user
        print("Pick a recipe from the following list:")

        validResponse = []
        i = 0
        for x in myresult:
            i+=1
            validResponse.append(i)
            recipesWithID.append(recipe(x["recipe_name"], x["recipe_id"], i))
            
            print ("%i. %s" % (i, x["recipe_name"]))

        userPickedRecipe = int(input("Please select a recipe: "))
        userPickedRecipe = self.inputValidaterInt(userPickedRecipe, validResponse)
        recipeID = recipesWithID[userPickedRecipe - 1].recipeID
        
        self.getIngredientsAndInstructionsForRecipe(recipeID)
        self.getReviewsForRecipe(recipeID)
        self.submitReview(recipeID)
        
        return

            
    def showUsersRecipes(self):

        if(not self.loggedIn):
            print("\nYou are not logged in. Please restart the app and sign in/sign up")
            return
        else:
            self.mycursor.execute("SELECT recipe_name, recipe_id From CleanRecipes WHERE author = '{}';".format(self.username))
            myresult = self.mycursor.fetchall()
            if (len(myresult) == 0):
                print("You have not submitted any recipes yet")
                return
            else:

                recipesWithID = [] # add each recipe along with it's ID over here and present these to the user
                print("\nPick a recipe from the following list:\n")

                validResponse = []
                i = 0
                for x in myresult:
                    i+=1
                    validResponse.append(i)
                    recipesWithID.append(recipe(x["recipe_name"], x["recipe_id"], i))
                    
                    print ("%i. %s" % (i, x["recipe_name"]))

                userPickedRecipe = int(input("\nPlease select a recipe: "))
                userPickedRecipe = self.inputValidaterInt(userPickedRecipe, validResponse)
                recipeID = recipesWithID[userPickedRecipe - 1].recipeID
                self.getIngredientsAndInstructionsForRecipe(recipeID)

                editRecipe = input("Would you like to edit your recipe? (Y/N): ")
                editRecipe = self.inputValidater(editRecipe, ['Y', 'N', 'y', 'n'])
                
                if (editRecipe == "Y" or editRecipe == "y"):

                    recipeName = input("\nPlease enter a name for your recipe: ")
                    recipeName = self.replaceApostrophe(recipeName)
                    author = self.username

                    ingredientList = []
                    ingredients = input("\nPlease input all ingredients, along with their amount, separated by commas: ")
                    ingredients = self.replaceApostrophe(ingredients)
                    ingredientList = ingredients.split(",")

                    instructionsList = []

                    print("\nPlease input instructions step by step. Once you are done, enter '1' ")

                    while(True):
                        instructionToAdd = input("Instruction: ")
                        instructionToAdd = self.replaceApostrophe(instructionToAdd)
                        if(instructionToAdd == "1"):
                            break
                        instructionsList.append(instructionToAdd)
                    
                    prepare_time = int(input("\nPlease enter the preparation time in minutes: "))
                    cook_time = int(input("Please enter the cook time in minutes: "))
                    total_time = prepare_time + cook_time
                    self.mycursor.execute("UPDATE CleanRecipes SET recipe_name = '{}', prepare_time = '{}', cook_time = '{}', total_time = '{}' WHERE recipe_id = '{}'".format(recipeName, prepare_time, cook_time, total_time, recipeID))
                    self.database.commit()
                    self.mycursor.execute("DELETE FROM RecipeIngredients WHERE recipe_id = '{}';".format(recipeID))
                    self.mycursor.execute("INSERT INTO RecipeIngredients (recipe_id, ingredients) VALUES ('{}','{}')".format(recipeID, ingredients))

                    self.mycursor.execute("DELETE FROM Ingredients WHERE recipe_id = '{}';".format(recipeID))
                    self.mycursor.execute("DELETE FROM Instructions WHERE recipe_id = '{}';".format(recipeID))
                    ingredientNumber = 0
                    for i in ingredientList:
                        i = self.replaceApostrophe(i)
                        ingredientNumber = ingredientNumber + 1
                        self.mycursor.execute("INSERT INTO Ingredients (recipe_id, ingredient_number, ingredient_name) VALUES ('{}','{}', '{}')".format(recipeID, ingredientNumber, i))
                    self.database.commit()
                    instructionNumber = 0
                    for i in instructionsList:
                        instructionNumber = instructionNumber + 1
                        self.mycursor.execute("INSERT INTO Instructions (recipe_id, step, description) VALUES ('{}','{}', '{}')".format(recipeID, instructionNumber, i))
                    self.database.commit()



