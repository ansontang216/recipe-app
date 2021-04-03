CREATE TABLE Ingredients 
(
ingredient_id int NOT NULL,
ingredient_name varchar,
PRIMARY KEY(ingredient_id)
);

CREATE TABLE RecipeIngredient 
(
recipe_id int NOT NULL,
ingredient_id int NOT NULL,
amount decimal(10,2),
unit_measurement varchar(100),
FOREIGN KEY(recipe_id) REFERENCES CleanRecipes(recipe_id),
FOREIGN KEY(ingredient_id) REFERENCES Ingredients(ingredient_id)
);

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
join numbers
  on 
  ROUND(LENGTH(directions) - LENGTH(REPLACE(directions,"**","")))/ LENGTH("**") > n - 1;

CREATE TABLE Users
(
user_id int NOT NULL AUTO_INCREMENT,
PRIMARY KEY(user_id)
);