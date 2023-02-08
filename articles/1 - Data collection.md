# Classifying Bots from Humans on Instragram: Data collection & storing

*This is the first article of a series of five. Here is the previous one, here the next one.*

In this article, I will take you on a journey of exploring the process of collecting and analyzing Instagram data to solve a problem that has been plaguing Instagram for years - identifying bots. WHAT ARE THE BOTS DOING AND WHY ARE THEY DANGEROUS. As someone who has been frustrated by the constant presence of bots on Instagram, I set out my end goal to prove that it is possible to build a model that can accurately predict bots using only public data and no NLP. 

SPOILER ALERT: I did it with an accuracy, F1 and AUC ~.97 and test/train diff of .03.

The notebook for this step of the process is on [Github](https://github.com/marclelamy/instagram_bot_classification/blob/main/1_data_collection.ipynb).




INSERT THE FLOW CHART SHOWING THE PATH OF THE DATA



## Collecting comments
For this step, I choose to collect the data using webscraping and Splinter. To get comments, I need post ID and to get them, I need to list pages first.

### Finding pages targeted by the bots

This was just finding the pages for which the bots comment on. I knew a couple like @championsleague, @mercedesamgf1, @ESPN. I remember two years ago, they were even commenting on Biden/Potus' pages. 
For the rest, friend sent me some and using the feature showing similar profiles. 

I listed about 20: @nfl, @championsleague, @mercedesamgf1, @ESPN, @bleacherreport, @houseofhighlights, @nba, @worldstar, @grmdaily, @pubity, @meme.ig, @brgridiron, @lakers, @ballislife, @nflonfox, @nflnetwork, @espnnfl, @cbssports, @thecheckdown


### Finding post IDs to get comments from 
For this, I used Splinter, a Python library that allows you to interact with your browser and websites pages. It uses Selenium under the hood but doesn't need as much code. 

to get the posts IDs, I first go to their page at URL `instagram.com/{ACCOUNT_NAME}` and scroll down to load more posts. Using beatufiul soup, I get the html of the page and collect all the links contaning `/p/` which is to indicate `post`. I decided to collect the 200 last posts ID because more than that might be posts that are too old in time as some pages post multiple times a day vs once a day, bots might have gone private or got banned, or the data too old.

To store all the data, I used sqlite3 with which I could store it in a database queryable with SQL.

Here's the code 
<script src="https://gist.github.com/marclelamy/a510fca1d857d821222b7f6b9e6f05a0.js"></script>





### Collecting comments from posts
Now that I have a list of post ids, I can access everyone of them with their url `https://www.instagram.com/p/{POSTID}/`, I can scrape comments! I just need to select all the comments, click on load more, and do that again. 


The code: 
<script src="https://gist.github.com/marclelamy/df24681ec9588e4044d8311b824ad0b4.js"></script>


### Renaming usernames to get cooler names 
Some users woudn't want their username show up in a table preview so I masked their usernames and anything that can be traced back to them. The function generate_slug() form the coolname library gives funny names.

The code: 
<script src="https://gist.github.com/marclelamy/693b5f6b93a4cd35d2e9259f13e92f65.js"></script>




## Collecting user data
### Function to fetch users data
The second part of the data collection is to collect the public data of each user. For this, I used Instaloader which is a very easy to use python library to get some data from Instagram. 

The code: 
The first piece of code is a function that fetches the data of a given username and stores the response json in a specific folder
<script src="https://gist.github.com/marclelamy/44efb2cd0f11c09a1e06afdaea2dfff9.js"></script>


### Function to convert the response json 
I need the data in a tabular format, hence need to convert the json in multiple tables. The json contains the informations about the user but also about their posts, two different granularity. 
The first table is about the user and has one row per user. The columns are like: follow count, post count, verified, bio, url in bio, etc. The second table from the json is about the posts of the users and has for each row a post. Knowing Instagram returns only the last 12, each username can have max 12 rows.

The code: 
<script src="https://gist.github.com/marclelamy/e6872302f5b1067884c19dcfbee09e99.js"></script>



### Fetch and convert each user and download thumbnails
Now that I have both functions ready to be called, I can loop though each username from the comment table, fetch their data, convert it into dataframes and then downloading their photo or video thumbnails. 

The code: 
<script src="https://gist.github.com/marclelamy/446a7887d436d43c3132c9a1309700ca.js"></script>



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




Did you use multiple techniques for labelling the data? 
Yes, I used different ones. The first step was to find pages that were targeted by bots. I knew some but got many others from friends. In total, I had about 20 pages. From there I collected 


Sure, can you provide more details on the specific methods you used to collect the Instagram data? 


Did you use the Instagram API or did you scrape the data from the website? If you used the API, were there any limitations or restrictions on the data you were able to collect?








How much data did you end up collecting in total, and what specific information or attributes did you gather for each user or post?

What steps did you take to store the data? Did you store it in a relational database or a NoSQL database, and why did you choose that particular storage solution?

What kind of data preprocessing did you perform before storing the data? Was there any missing data or outliers you had to handle?

Can you also provide more information about the data cleaning process? What steps did you take to ensure that the data was accurate and reliable for your analysis? How did you handle any duplicates or inconsistencies in the data?

Did you encounter any challenges or obstacles during the data collection and storage process? And How long did it take to collect and store the data?

How did you decide which Instagram users to collect data on?
Did you collect data on both public and private Instagram accounts? If so, how did you handle private accounts?
How did you handle any issues with rate limiting while collecting data from the Instagram API?
How did you handle any changes to the Instagram API during the data collection process?
Did you collect data on Instagram Stories or Reels? If so, how did you handle that data?
Did you collect data on Instagram comments? If so, what information did you gather from comments?
How did you handle any missing data or errors in the data you collected?
Were there any specific data privacy or ethical considerations you had to take into account during the data collection process?
How did you handle any issues with data duplication or inconsistency?
Did you collect data from other social media platforms in addition to Instagram? If so, which platforms and what data did you gather?
How did yungamou handle any issues with data storage capacity?
How did you back up the collected data to ensure its safety and security?
How did you handle any issues with data privacy and security during the storage process?
How did you ensure that the data was organized and structured in a way that made it easy to analyze?
How did you keep track of the data collection and storage pris ocess?
What steps did you take to validate the data after collecting and storing it?
What steps did you take to clean the data?
How did you handle any issues with data scalability?
How did you handle any issues with data quality?
What tools and technologies did you use to collect, store and clean the data?