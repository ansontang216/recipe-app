select directions, 
ROUND(LENGTH(directions) - LENGTH(REPLACE(directions,"**","")))/ LENGTH("**") as numOfOccurence
from CleanRecipes limit 1;