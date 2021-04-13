import os
import mysql.connector
from recipe import recipe
from sqlalchemy import create_engine
import pymysql
from scipy.sparse.linalg import svds
import pandas as pd
import numpy as np

class recipes:

    def __init__(self):
        self.mycursor, self.database = self.connectToDatabase()
        self.startCLI()
        self.loggedIn = False
        self.username = ""
        self.profileID = 0

    def startCLI(self):
        
        loginResponse = input("Would you like to Log In/Sign Up? (Y/N): ")

        if (loginResponse == "Y"):
            signingIn = """1. Sign In\n2. Sign Up """
            
            signingInResponse = input(signingIn)

            if (signingInResponse == "1"):
                print("Peforming sign in..")
                self.performSignIn()
            elif (signingInResponse == "2"):
                self.performSignUp()

        openingMessage = """1. Recipes\n2. Recommend recipes to me"""

        firstResponse = input(openingMessage)

        if (firstResponse == "1"):
            recipesMessage = """1. Find Recipe:\n11. Find Recipe by Name\n12. Find Recipe by Ingredients\n13. Find Recipe by Total Time\n2. Submit Recipe"""

            recipesResponse = input(recipesMessage)

            if (recipesResponse == "11"):
                getRecipeName = input("Please input the name of the recipe: ")
                self.findRecipeByName(getRecipeName)
            elif (recipesResponse == "12"):
                self.findRecipeByIngredients()
            elif (recipesResponse == "13"):
                self.findRecipeByTotalTime()
            elif (recipesResponse == "2"):
                self.submitRecipe()

        elif (firstResponse == "2"):
            recommendedRecipes = self.recommend_recipes(self.profileID)
            self.getRecipesFromDataframe(recommendedRecipes)

        return


    def connectToDatabase(self):
        conn = mysql.connector.connect(host = 'marmoset04.shoshin.uwaterloo.ca',
                  user = 'a32saini',
                  password = 'dbhty@zRCkIT5@LY4T^4',
                  database = 'project_28',
                  use_pure=True)

        mycursor = conn.cursor(dictionary=True)
        return mycursor, conn


    def findRecipeByName(self, recipeName):
        
        self.mycursor.execute("SELECT recipe_name, recipe_id From CleanRecipes WHERE recipe_name like '%{}%';".format(recipeName))
        myresult = self.mycursor.fetchall()

        recipesWithID = [] # add each recipe along with it's ID over here and present these to the user
        print("Pick a recipe from the following list:")

        i = 0
        for x in myresult:
            i+=1
            recipesWithID.append(recipe(x["recipe_name"], x["recipe_id"], i))
            
            print ("%i. %s" % (i, x["recipe_name"]))

        userPickedRecipe = int(input("Please select a recipe: "))
        recipeID = recipesWithID[userPickedRecipe - 1].recipeID
        
        self.getIngredientsAndInstructionsForRecipe(recipeID)
        self.getReviewsForRecipe(recipeID)
        self.submitReview(recipeID)

        return

    def likeClauseForIngredients(self, ingredients):
        stringToReturn = ""

        for i in ingredients:
            if (i != ingredients[-1]):
                recipeLike = "ingredients like '%{}%' AND ".format(i)
                stringToReturn = stringToReturn + recipeLike
            else:
                recipeLike = "ingredients like '%{}%'".format(i)
                stringToReturn = stringToReturn + recipeLike

        stringToReturn = stringToReturn
        return stringToReturn


    def findRecipeByIngredients(self):
        getIngredients = input("Please enter your ingredients separated by commas. (For eg: eggs, milk, sugar)")
        ingredients = []
        ingredients = getIngredients.split(",")
        like = self.likeClauseForIngredients(ingredients)

        self.mycursor.execute( "SELECT recipe_name, recipe_id FROM CleanRecipes where recipe_id in (SELECT recipe_id From RecipeIngredients WHERE {});".format(like) )
        myresult = self.mycursor.fetchall()

        recipesWithID = [] # add each recipe along with it's ID over here and present these to the user
        print("Pick a recipe from the following list:")

        i = 0
        for x in myresult:
            i+=1
            recipesWithID.append(recipe(x["recipe_name"], x["recipe_id"], i))
            
            print ("%i. %s" % (i, x["recipe_name"]))

        userPickedRecipe = int(input("Please select a recipe: "))
        recipeID = recipesWithID[userPickedRecipe - 1].recipeID
        
        self.getIngredientsAndInstructionsForRecipe(recipeID)
        self.getReviewsForRecipe(recipeID)
        self.submitReview(recipeID)
        
        return


    def getIngredientsAndInstructionsForRecipe(self, recipeID):

        self.mycursor.execute("SELECT ingredient_number, ingredient_name From Ingredients WHERE recipe_id = '{}' ORDER BY ingredient_number ASC;".format(recipeID))
        myresult = self.mycursor.fetchall()
        
        for x in myresult:
            print ("%s. %s" % (x["ingredient_number"], x["ingredient_name"]))

        self.mycursor.execute(" SELECT step, description From Instructions WHERE recipe_id = '{}' ORDER BY step ASC;".format(recipeID))
        myresult = self.mycursor.fetchall()

        for x in myresult:
            print ("%s. %s" % (x["step"], x["description"]))

        return

    def getReviewsForRecipe(self, recipeID):

        yesOrNoReviews = input("Would you like to view Reviews for this Recipe? (Y/N)")

        if (yesOrNoReviews == "Y"):
            filterByRating = input("Would you like to filter Reviews by Ratings? (Y/N)")

            if(filterByRating == "Y"):
                getMinimumRating = int(input("Select a minimum rating from 1-5 "))
            
                self.mycursor.execute(" SELECT rate, comment From CleanReviews WHERE recipe_id = '{}' and rate >= '{}';".format(recipeID, getMinimumRating))
                myresult = self.mycursor.fetchall()
                
                i = 0
                for x in myresult:
                    i = i + 1
                    print ("%i. %s" % (i, x["comment"]))

            elif(filterByRating == "N"):
                self.mycursor.execute(" SELECT rate, comment From CleanReviews WHERE recipe_id = '{}';".format(recipeID))
                myresult = self.mycursor.fetchall()
                
                i = 0
                for x in myresult:
                    i = i + 1
                    print ("%i. %s" % (i, x["comment"]))

    def helper(self, preds_df, userID, movies_df, original_ratings_df, num_recommendations=5):
    
        user_row_number = userID 
        sorted_user_predictions = preds_df.iloc[user_row_number].sort_values(ascending=False) # UserID starts at 1

        user_data = original_ratings_df[original_ratings_df.profile_id == (userID)]
        user_full = (user_data.merge(movies_df, how = 'left', left_on = 'recipe_id', right_on = 'recipe_id').
                        sort_values(['rate'], ascending=False))
    
        recommendations = (movies_df[~movies_df['recipe_id'].isin(user_full['recipe_id'])]).merge(pd.DataFrame(sorted_user_predictions).reset_index(), how = 'left', left_on = 'recipe_id',
                right_on = 'recipe_id').rename(columns = {user_row_number: 'Predictions'}).sort_values('Predictions', ascending = False).iloc[:num_recommendations, :-1]
    
        return user_full, recommendations

    def recommend_recipes(self, userID):

        db_connection_str = 'mysql+pymysql://a32saini:dbhty@zRCkIT5@LY4T^4@marmoset04.shoshin.uwaterloo.ca/project_28'
        db_connection = create_engine(db_connection_str)
    
        recipes         = pd.read_sql("SELECT recipe_name, recipe_id From CleanRecipes", con=db_connection)
        reviews         = pd.read_sql("SELECT profile_id, recipe_id, rate From CleanReviews", con=db_connection)
        

        usrID_index = -1
        # create a temp table which maps and stores profileID as index that starts from 0
        temp = reviews.sort_values("profile_id").reset_index(drop=True)
        # Use a subset of reviews if the entire reviews makes the table crash.
        # temp = rv[:50000].sort_values("profileID").reset_index(drop=True)
        prev_id = -1
        curr_id = -1
        k = 0 
        for i in range(len(temp)):
            curr_id = temp.loc[i, 'profile_id']
            if prev_id == curr_id:
                temp.loc[i, 'profile_id'] = k - 1
            else :
                temp.loc[i, 'profile_id'] = k
                k = k+1
            prev_id  = curr_id
            ## Store userID index for future use in the algorith
            if curr_id == userID:
               usrID_index = temp.loc[i, 'profile_id']
        

        user_ratings = temp[['recipe_id', 'profile_id', 'rate']]

        # remove duplicates
        user_ratings_new = user_ratings.drop_duplicates(subset=["recipe_id", "profile_id"], keep = 'last').reset_index(drop = True)

        # Create a matrix for userID recipeID and the rating
        df_recipe_features = user_ratings_new.pivot(
                                                    index='profile_id',
                                                    columns='recipe_id',
                                                    values='rate'
                                                    ).fillna(0)
        # SVD algorithm
        R = df_recipe_features.values
        user_ratings_mean = np.mean(R, axis = 1)
        R_demeaned = R - user_ratings_mean.reshape(-1, 1)

        U, sigma, Vt = svds(R_demeaned, k = 50)
        sigma = np.diag(sigma)
        all_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt) + user_ratings_mean.reshape(-1, 1)
        
        # Get rating predictions
        preds_df = pd.DataFrame(all_user_predicted_ratings, columns = df_recipe_features.columns)

        #Get recommendations
        # 5 is the number of recommendation, can change it to a different number too
        already_rated, recommendation = self.helper(preds_df, usrID_index, recipes, user_ratings_new, 5)
        
        #returns a pandas dataframe wich Recipe name and recipe ID 
        # can be converted to np array if needed
        return recommendation

    def performSignIn(self):

        getUsername = input("Please enter your username: ")
        getPassword = input("Please enter your password: ")
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
        self.mycursor.execute( "SELECT * FROM Users where username = '{}';".format(username) )
        myresult = self.mycursor.fetchall()

        newUsername = username

        if (len(myresult) != 0):
            newUsername = input("Please enter another username, as this is already taken ")
            self.doesUsernameExist(newUsername)
        else:
            return newUsername

    def performSignUp(self):
        getUsername = input("Please enter a username: ")
        newUsername = self.doesUsernameExist(getUsername)
        getPassword = input("Please enter a password: ")
        self.mycursor.execute( "INSERT INTO Users (username, password) VALUES ('{}','{}');".format(newUsername, getPassword) )
        self.database.commit()
        self.mycursor.execute( "SELECT profile_id FROM Users where username = '{}' AND password = '{}';".format(newUsername, getPassword))
        myresult = self.mycursor.fetchall()
        self.username = newUsername
        self.profileID = myresult[0]["profile_id"]
        self.loggedIn = True
        return

    def findRecipeByTotalTime(self):

        getMaxTime = int(input("Please enter the maximum amount of time in minutes"))
        self.mycursor.execute( "SELECT recipe_name, recipe_id FROM CleanRecipes where total_time <= {};".format(getMaxTime) )
        myresult = self.mycursor.fetchall()

        recipesWithID = [] # add each recipe along with it's ID over here and present these to the user
        print("Pick a recipe from the following list:")

        i = 0
        for x in myresult:
            i+=1
            recipesWithID.append(recipe(x["recipe_name"], x["recipe_id"], i))
            
            print ("%i. %s" % (i, x["recipe_name"]))

        userPickedRecipe = int(input("Please select a recipe: "))
        recipeID = recipesWithID[userPickedRecipe - 1].recipeID
        
        self.getIngredientsAndInstructionsForRecipe(recipeID)
        self.getReviewsForRecipe(recipeID)
        self.submitReview(recipeID)
        
        return


    def submitRecipe(self):

        if (not (self.loggedIn)):
            print("You are not logged in. Please restart the app and Sign in/Sign up.")
            return
        
        recipeName = input("Please enter a name for your recipe: ")
        reviewCount = 0
        author = self.username

        ingredientList = []
        ingredients = input("Please input all ingredients, along with their amount, separated by commas: ")
        ingredientList = ingredients.split(",")

        instructionsList = []

        print("Please input instructions step by step. Once you are done, enter '1' ")

        while(True):
            instructionToAdd = input("Instruction: ")
            if(instructionToAdd == "1"):
                break
            instructionsList.append(instructionToAdd)
        

        prepare_time = int(input("Please enter the preparation time in minutes: "))
        cook_time = int(input("Please enter the cook time in minutes: "))
        total_time = prepare_time + cook_time
        self.mycursor.execute("INSERT INTO CleanRecipes (recipe_name, review_count, recipe_photo, author, prepare_time, cook_time, total_time) VALUES ('{}', '{}', 'no photo', '{}', '{}', '{}', '{}');".format(recipeName, reviewCount, author, prepare_time, cook_time, total_time))
        self.database.commit()

        self.mycursor.execute("SELECT max(recipe_id) as maxID FROM CleanRecipes")
        myresult = self.mycursor.fetchall()
        self.mycursor.execute("INSERT INTO RecipeIngredients (recipe_id, ingredients) VALUES ('{}','{}')".format(myresult[0]["maxID"], ingredients))

        ingredientNumber = 0
        for i in ingredientList:
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

        getReviewsResponse = input("Would you like to leave a review for this recipe? (Y/N): ")
        if(getReviewsResponse == "N"):
            return
        elif(getReviewsResponse == "Y"):

            if (not self.loggedIn):
                print("You need to be logged in to be able to leave a review. Please restart the app and Sign In/Sign Up.")
                return
            else:
                getRating = int(input("Please enter a rating from 1-5: "))
                getReviewComments = input("Please enter some comments: ")

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

        recipesWithID = [] # add each recipe along with it's ID over here and present these to the user
        print("Pick a recipe from the following list:")

        i = 0
        for index, x in recipes.iterrows():
            i+=1
            recipesWithID.append(recipe(x['recipe_name'], x['recipe_id'], i))
            
            print ("%i. %s" % (i, x['recipe_name']))

        userPickedRecipe = int(input("Please select a recipe: "))
        recipeID = recipesWithID[userPickedRecipe - 1].recipeID
        
        self.getIngredientsAndInstructionsForRecipe(recipeID)
        self.getReviewsForRecipe(recipeID)
        self.submitReview(recipeID)

        return