drop table if exists CleanRecipes;
drop table if exists CleanReviews;
drop table if exists Ingredients;
drop table if exists Users;
drop table if exists Instructions;

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
);

load data infile '/var/lib/mysql-files/02-Recipes/project28/cleaned_reviews2.csv' ignore into table CleanReviews
     fields terminated by ','
     enclosed by '"'
     lines terminated by '\n'
     ignore 1 lines
(@id,recipe_id,profile_id,rate,comment);

CREATE TABLE Ingredients 
(
ingredient_id int NOT NULL AUTO_INCREMENT,
recipe_id int NOT NULL,
ingredient_number int,
ingredient_name text,
PRIMARY KEY(ingredient_id),
FOREIGN KEY(recipe_id) REFERENCES CleanRecipes(recipe_id)
);

create temporary table ingredient_numbers as (
  select 1 as n
  union select 2 as n
  union select 3 as n
  union select 4 as n
  union select 5 as n
  union select 6 as n
  union select 7 as n
  union select 8 as n
  union select 9 as n
  union select 10 as n
  union select 11 as n
  union select 12 as n
  union select 13 as n
  union select 14 as n
  union select 15 as n
  union select 16 as n
  union select 17 as n
  union select 18 as n
  union select 19 as n
  union select 20 as n
  union select 21 as n
  union select 22 as n
  union select 23 as n
  union select 24 as n
  union select 25 as n
  union select 26 as n
  union select 27 as n
  union select 28 as n
  union select 29 as n
);

insert into Ingredients (recipe_id,ingredient_number,ingredient_name)
select recipe_id,
	n as step,
 substring_index(
    substring_index(ingredients, '**', n), 
    '**', 
    -1
  ) as description
from CleanRecipes
join ingredient_numbers
  on 
  ROUND(LENGTH(ingredients) - LENGTH(REPLACE(ingredients,"**","")))/ LENGTH("**") >= n - 1
order by recipe_id,step;

CREATE TABLE Users
(
profile_id int NOT NULL,
PRIMARY KEY(profile_id)
);

insert into Users(profile_id)
select distinct profile_id from CleanReviews;

CREATE TABLE Instructions
(
recipe_id int NOT NULL,
step int NOT NULL,
description text,
FOREIGN KEY(recipe_id) REFERENCES CleanRecipes(recipe_id)
);

create temporary table instruction_numbers as (
  select 1 as n
  union select 2 as n
  union select 3 as n
  union select 4 as n
  union select 5 as n
  union select 6 as n
  union select 7 as n
  union select 8 as n
  union select 9 as n
  union select 10 as n
  union select 11 as n
  union select 12 as n
);

insert into Instructions (recipe_id,step,description)
select recipe_id,
  n as step,
 substring_index(
    substring_index(directions, '**', n), 
    '**', 
    -1
  ) as description
from CleanRecipes
join instruction_numbers
  on 
  ROUND(LENGTH(directions) - LENGTH(REPLACE(directions,"**","")))/ LENGTH("**") > n - 1;

ALTER TABLE CleanReviews
ADD FOREIGN KEY (profile_id) REFERENCES Users(profile_id);

ALTER TABLE CleanReviews
ADD FOREIGN KEY (recipe_id) REFERENCES CleanRecipes(recipe_id);

ALTER TABLE CleanRecipes
DROP COLUMN ingredients;

ALTER TABLE CleanRecipes
DROP COLUMN directions;