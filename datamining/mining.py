from scipy.sparse.linalg import svds
import pandas as pd
import numpy as np

class mining:

    def __init__(self, conn):
        self.conn = conn

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
        print("\nRecommender system is running it's algorithm..\n")

        recipes         = pd.read_sql("SELECT recipe_name, recipe_id From CleanRecipes", con=self.conn)
        reviews         = pd.read_sql("SELECT profile_id, recipe_id, rate From CleanReviews", con=self.conn)

        
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