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
step int NOT NULL AUTO_INCREMENT,
description,
FOREIGN KEY(recipe_id) REFERENCES CleanRecipes(recipe_id)
);

CREATE TABLE Users
(
user_id int NOT NULL AUTO_INCREMENT,
PRIMARY KEY(user_id)
);