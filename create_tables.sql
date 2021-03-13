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