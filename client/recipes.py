import os
import mysql.connector
from recipe import recipe
from sqlalchemy import create_engine
import pymysql
from scipy.sparse.linalg import svds

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

    def helper(preds_df, userID, movies_df, original_ratings_df, num_recommendations=5):
        
        user_row_number = userID 
        sorted_user_predictions = preds_df.iloc[user_row_number].sort_values(ascending=False) # UserID starts at 1

        user_data = original_ratings_df[original_ratings_df.profileID == (userID)]
        user_full = (user_data.merge(movies_df, how = 'left', left_on = 'recipeID', right_on = 'recipeID').
                        sort_values(['rate'], ascending=False))
        
        recommendations = (movies_df[~movies_df['recipeID'].isin(user_full['recipeID'])]).merge(pd.DataFrame(sorted_user_predictions).reset_index(), how = 'left', left_on = 'recipeID',
                right_on = 'recipeID').rename(columns = {user_row_number: 'Predictions'}).sort_values('Predictions', ascending = False).iloc[:num_recommendations, :-1]
                      
    return user_full, recommendations
    
    ### Takes an userID as an input
    ### Returns 5 recommendations for the userID
    ### Returns a pandas dataframe wich Recipe name and recipe ID 
    def recommend_recipes(self, userID)
        # Read MySQL tables to pandas Dataframe using pysql
                          #'mysql+pymysql://mysql_user:mysql_password@mysql_host/mysql_db'
        db_connection_str = 'mysql+pymysql://a32saini:dbhty@zRCkIT5@LY4T^4@marmoset04.shoshin.uwaterloo.ca/project_28'
        db_connection = create_engine(db_connection_str)
        # store as dataframe 
        recipes         = pd.read_sql("SELECT recipe_name, recipe_id From CleanRecipes", con=dbConnection);
        reviews         = pd.read_sql("SELECT profile_id, recipe_id, rate From CleanReviews", con=dbConnection);
        
        usrID_index = -1
        # create a temp table which maps and stores profileID as index that starts from 0
        temp = reviews.sort_values("profileID").reset_index(drop=True)
        # Use a subset of reviews if the entire reviews makes the table crash.
        # temp = rv[:50000].sort_values("profileID").reset_index(drop=True)
        prev_id = -1
        curr_id = -1
        k = 0 
        for i in range(len(temp)):
            curr_id = temp.loc[i, 'profileID']
            if prev_id == curr_id:
                temp.loc[i, 'profileID'] = k - 1
            else :
                temp.loc[i, 'profileID'] = k
                k = k+1
            prev_id  = curr_id
            ## Store userID index for future use in the algorith
            if curr_id == userID:
               usrID_index = temp.loc[i, 'profileID']

        user_ratings = temp[['recipeID', 'profileID', 'rate']]

        # remove duplicates
        user_ratings_new = user_ratings.drop_duplicates(subset=["recipeID", "profileID"], keep = 'last').reset_index(drop = True)

        # Create a matrix for userID recipeID and the rating
        df_recipe_features = user_ratings_new.pivot(
                                                    index='profileID',
                                                    columns='recipeID',
                                                    values='rate'
                                                    ).fillna(0)
        ## SVD algorithm
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
        already_rated, recommendation = helper(preds_df, userID, recipes, user_ratings_new, 5)

    #returns a pandas dataframe wich Recipe name and recipe ID 
    # can be converted to np array if needed
    return recommendation


        
        
    
    # def performSignIn(self):

    # def performSignUp(self):
    
    # def findRecipeByIngredients(self):

    # def findRecipeByTotalTime(self):

    # def submitRecipe(self):

    # def submitReview(self):