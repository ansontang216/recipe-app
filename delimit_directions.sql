select 
ROUND(LENGTH(directions) - LENGTH(REPLACE(directions,"**","")))/ LENGTH("**") as numOfOccurence
from CleanRecipes;


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


select recipe_id,
	n as ingredient_number,
 substring_index(
    substring_index(ingredients, '**', n), 
    '**', 
    -1
  ) as ingredient
from CleanRecipes
join numbers
  on 
  ROUND(LENGTH(ingredients) - LENGTH(REPLACE(ingredients,"**","")))/ LENGTH("**") > n - 1;