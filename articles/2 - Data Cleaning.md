# Classifying Bots from Humans on Instragram part 2: Data cleaning
DON'T FORGET TO BRAG!!! THIS IS S A FUCKING ENORMOUS ACHIEVEMENT.

*This is the second article on a series of 6 *



Now that I had the data on my computer, I needed to clean it and consolidate all the datasets being at different grannularities. There are three db that need to be cleaned and consolidated: the comments, the users and the posts at the comment level as it is the most granular. I didnt directly cleaned the data as I wanted to keep it almost as it for the labelling. 


[label](https://www.google.com/url?sa%3Di%26url%3Dhttps%3A%2F%2Fimgflip.com%2Ftag%2Fignorant%26psig%3DAOvVaw1ptYn-3VtcJoD3xqTx93KW%26ust%3D1675902971887000%26source%3Dimages%26cd%3Dvfe%26ved%3D0CA8QjRxqFwoTCPixs5zXhP0CFQAAAAAdAAAAABAE)








Write an article for Medium about it saying what I did following the outline of the code:


This step of the process is divided in two parts: preparing each of the three tables and then merging all of them together. 
Starting with Comments, 

## Comments
table comtaining all the comments collectes and has a grannulatiry of one comment per row. 

### Removing irrelevent columns

When colelcting the comment I had data about: 
* page	
* postid	
* legend	
* post_likes	
* post_posted_time	
* username	
* full_comment_data	
* comment	
* comment_posted_time	
* comments_likes	
* comment_comments_count	
* data_collected_time

I only had in mind to keep what would be used to feed the model and kept the following columns:
* username
* comment
* comments_likes
* comment_posted_time
* post_posted_time 


## File description 
This file is meant to clean and tranform the data already existing to a format that will be used for labelling. Some EDA and feature engineering will be done here but as the data is not labelled, most of it will be done after the labelling.
## 0. Modules and UDFs
### 0.1 Setting notebook preferences

Setting pandas to not limit the number of displayed columns and connect to the database.
Now, each table is going to be cleaned and put in a nice format ready to be used during the data labelling
### 0.2 Changing all usernames names for cooler names



This is to be done on all dataset so better doing it at the beginning
Creating new name dictionary and save it direclty
## 1. Comments



This table contains all the comments collected and each row of the table represent a single comment. It's possible that if a user commented twice on a post, I collected both of the comment or caught the comment of the same users on multiple post.

The goal is to clean the table, and output it in a clean and organized table containing one comment per row.
### 1.1 Load data and quick explore
Luckily no duplicates, some columns as likes and comment likes need to be integers, others as the dates need to me in a date format.



* There are 134.465 rows of data, meaning the same number of comments

* Total of 88608 users meaning an average of 1.5 comment per user

* Post likes and comment need the numbers to be extracted and columns changed to integer 

* The three date columns don't have a correct type

* Some columns names are not explicit enough, might need to change them

* Some columns are irrelevant to this analysis. For example, the legend of the post will have no effect on the bot/non bot user so there is no point of keeping them

* No missing values! :emoji_dab:
### 1.2 Removing irrelevant columns & column names



I collected too much data, some columns are irrelevant to the analysis or the model develoment as the page, postid, post_likes and others are independant from the bots.
### 1.4 Posted time



Both posted time columns don't have the proper datatype, they need to be datetime. Itself they don't help much but I can subtract both date and know how many seconds after the post has been posted, the comment has been too. 



the column comment posted time is very important as many users spam the same commment and have 0-0 likes accros the tries, keeping the columns comment posted time prevent from removing fake duplicated.
For most of the comments collected, 75% have been posted in the first 10 minutes after the post has been posted. The median is a third of that, half of the comments were posted in the first three minutes. The peak of the most comments posted at the same time happends 19-20 seconds after the post is published. Once the users are labelled, it'll be interesting to see the difference in that 0-20 seconds window to see the ratio of bots compared to later. The data is not representative of all Instagram data as when collecting it, I was starting collecting the first IG was showing, the ones with the most likes.
### 1.5 Comment likes

The like columns is string containing the number of likes formated with thousand commas followed by 'Likes'. The column should be and ineger without any character being non numeric
75% of the comments have less than 295 likes with half less than 50 likes. Let's look at the relationship with likes and how it varies depending on when the comment has been posted. 
There is a general trend, the more time after the post is posted you comment, the less likes you will have. This is because there are already a bunch of poeple that have seen the post before the late comment so less potential like count. Except in rare situations, this is always the case for non verified users, they always have low likes if they don't comment at the beginning. For verified users, it's not the same as they ahave their followers naturally liking their comment or the page owner commenting on its own post. It'll be interesting to see how the distribution changes for bots/legit users.
### 1.6 Comment content



* While scraping the comments, I also collect the button name right under and collected in some comments 'Hide replies' and 'Reply'.

* Many comments have emojis
### 1.7 Export data
## 2. Last 12 posts



This is the table containing all the information about the last 12 posts of the users. 12 is not chosen but the number of posts automatically sent back by Instagram when looking a user profile. Each row is a post of a user. 

### 2.1 Load data and quick expolore
Couple of insights from that: 

* Missing values in video views but this is likely due to photos posts

* About 75k missing captions and 300k video views. Those are maybe due to posts being photos and just no caption

* Most of the columns have the wrong datatypes (float instead of int, object for date)

### 2.2 Removing irrelevant columns and renaming some
### 2.3 Videos 



Checking for missing values and changing types
Missing values are only for when the post is a video. Knowing there is the `is_video` flag in another column, I can fill the missing values by 0
### 2.4 Caption extraction



The caption contains the caption, date, people tagged but I won't do NLP and I have the timestamp so date so I'm only keeping if/how many accounts are tagged
### 2.5 Timestamp & likes CHECK TO BE SURE THAT ALL USERS HAVE MAX 12 POSTS AS THERE ARE DUPES AND USERS WITH 12+ POSTS



Changing then dtype of timestamp and likes to be datetime and likes
### 2.6 Export table
##  3. User Profile Data



User profile data is all the information on the user, each row is a single user, not like the precedent table.
### 3.1 Load data and quick expolore
Many columns are not useful to the rest of the analysis, some other have no meaning so we'll remove them



* Most of the columns have no mising values

* The columns 'is_xxx' and 'xxx_count' have wrong data types, they should be integers

* There are five pronouns columns with all different count of missing values

* The business and professional columns don't have the same count of missing values which is odd as I was imaginating that business attributes are for all busienss account

* The last 9 columns have only two non missing values. the user has 'STATE_CONTROLLED_MEDIA' for transparancy_product

* external_url_linkshimmed: Instagram redirect, useless as eternal_url is already there

* fbid & id: facebook/IG id, not relevant

* profile_pic_url and profile_pic_url_hd: not relevant, photos already downloaded

### 3.2 Renaming and removing columns: 

### 3.x Missing values



Replacing missing values by an empty string
### 3.3 External url



Keeping only the domain
### 3.4 Pronouns



Multiple columns are named pronouns but don't have the same number of values in each. The goal is to consolidate the columns into one.
The pronouns columns is useless as it has no information except missing values and empty strings
### 3.5 Count and binary columns



Many columns are binary, 1 or 0 to express if a user is a business account, is verified, etc and other expressing count as follower count, post counts, etc. All or most of those columns don't have a proper datatype but are objects where they should be integers
All columns with count in the name have the correct datatype and are clean of missing values. However, the Binary columns don't have the right type.
### 3.6 Business columns 



There are five colmns mentioning characteristics from business accounts: 

* is_business_account

* is_professional_account

* business_contact_method

* business_category_name

* category_enum

* category_name



... and maybe:

* should_show_category

* should_show_public_contacts

The missing values are not consistent but I don't think (will still have to check) that the bots are business/professional accounts so those columns don't matter a lot, I can leave the missing values
### 3.7 Duplicates



Some users have been collected multiple times, so I need to remove the duplicates. knowing a bot can with time, become private or delete its link, i'll order the data ascending and keep the last value as it's the one with less followers/follows
### 3.7 Export data
## 4.0 Merge into one table



Joining all table into a single one.
### 4.1 Adding columns
### 4.2 Exporting data
## 7.0 export data
## Playground

<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
Can you explain the process you used to clean your data?
What challenges did you face during the data cleaning process?
Did you use any specific tools or techniques to clean your data?
How did you handle missing or incomplete data?
Did you encounter any unexpected data issues during the cleaning process?
How did you ensure the quality of your data after cleaning?
Did you perform any data transformations during the cleaning process?
How did the data cleaning process impact your analysis and results?
Did you collaborate with any other individuals or teams during the data cleaning process?
What did you learn about the data during the cleaning process that you did not know before?
What recommendations would you give to others who are cleaning data for a similar project?
How did you document the data cleaning process to ensure reproducibility of your results?
Can you provide any examples of how you cleaned a specific dataset or column of data?