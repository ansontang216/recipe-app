drop table if exists CleanRecipes;
drop table if exists CleanReviews;

CREATE TABLE CleanRecipes(
	recipe_name varchar(100),
	recipeID int NOT NULL,
	review_count int,
	recipe_photo blob,
	author varchar(100),
	prepare_time int,
	cook_time int,
	total_time int,
	ingredients blob,
	directions blob,
	PRIMARY KEY(recipeID)
);

load data infile '/var/lib/mysql-files/02-Recipes/project28/cleaned-recipes2.csv' ignore into table CleanRecipes
     fields terminated by ','
     enclosed by '"'
     lines terminated by '\n'
     ignore 1 lines
     (@id,recipe_name,recipeID,review_count,recipe_photo,author,prepare_time,cook_time,total_time,ingredients,directions);

CREATE TABLE CleanReviews(
	recipe_id int NOT NULL,
	profile_id int NOT NULL,
	rate int,
	comment text
	-- PRIMARY KEY(recipe_id)
);

load data infile '/var/lib/mysql-files/02-Recipes/project28/cleaned_reviews2.csv' ignore into table CleanReviews
     fields terminated by ','
     enclosed by '"'
     lines terminated by '\n'
     ignore 1 lines
     (@id,recipe_id,profile_id,rate,comment);