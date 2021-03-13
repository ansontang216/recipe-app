CREATE database recipes_project_28;

CREATE TABLE recipes 
(
recipe_id int NOT NULL,
recipe_name varchar,
review_count int,
recipe_photo blob,
author varchar(100),
prepare_time int,
cook_time int,
total_time int,
ingredients text,
directions text,
PRIMARY KEY(recipe_id)
);

CREATE TABLE raw_recipes 
(
id int NOT NULL,
name varchar(100),
minutes int,
contributor_id int,
submitted date,
tags JSON,
nutrition JSON,
n_steps int,
steps JSON,
description text,
ingredients JSON,
n_ingredients int
PRIMARY KEY(id)
);

CREATE TABLE raw_interactions
(
recipe_id int NOT NULL,
user_id int NOT NULL,
date_field datetime,
rating int,
review text,
PRIMARY KEY(recipe_id, user_id)
);

CREATE TABLE reviews
(
recipe_id int NOT NULL,
profile_id int NOT NULL,
rate int,
comment text,
PRIMARY KEY(recipe_id)
);

CREATE TABLE PP_users
(
id int NOT NULL,
techniques JSON,
items JSON,
n_items int,
ratings JSON,
n_ratings int,
PRIMARY KEY(id)
);

CREATE TABLE PP_recipes
(
recipe_id int NOT NULL,
i int,
name_tokens JSON,
ingredients_tokens JSON,
step_tokens JSON,
techniques JSON,
calorie_level int,
ingredient_ids JSON,
PRIMARY KEY(recipe_id)
);

CREATE TABLE food_coded
(
GPA	decimal(4,3),
Gender int,
breakfast int,
calories_chicken int,	
calories_day int,
calories_scone int,
coffee int,
comfort_food text,	
comfort_food_reasons text,
comfort_food_reasons_coded int,	
cook int,
comfort_food_reasons_coded int,
cuisine int,
diet_current char(300), 
diet_current_coded int,	
drink int,	
eating_changes text,
eating_changes_coded int,	
eating_changes_coded1 int,
eating_out int,
employment int,	
ethnic_food	int,
exercise int,
father_education int,	
father_profession char(100),	
fav_cuisine	char(20),
fav_cuisine_coded int,	
fav_food int,
food_childhood text, 	
fries int, 	
fruit_day int,	
grade_level int,	
greek_food int,
healthy_feeling int,	
healthy_meal text,	
ideal_diet text,
ideal_diet_coded int,	
income int,
indian_food int,	
italian_food int,	
life_rewarding int,
marital_status int,	
meals_dinner_friend	text,
mother_education int, 	
mother_profession text,	
nutritional_check int,	
on_off_campus int,	
parents_cook int,	
pay_meal_out int,	
persian_food int,	
self_perception_weight int,	
soup int,	
sports int,	
thai_food int,	
tortilla_calories int,	
turkey_calories	int,
type_sports text,	
veggies_day int,	
vitamins int,
waffle_calories int,
weight int
)