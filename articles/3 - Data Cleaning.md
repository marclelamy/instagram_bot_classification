
Now that I had the data on my computer and cleaned, I though that most was done, there's still some work you know, clean, analyze and do some crazy XGBoost stuff, the data is collected so it's good! 

Saying that this step was long and hard would be an understatement. I discovered data labelling the hard way and promise myself to never do it again. and that I quit multiple times because of that step. I stoped for a month, then two and then I put it behind me but a post on Linkedin making me excited about how to label the data easierly, make me go back again. This is how I labelled the data, and all the techniques that I used.



## Introduction 
There is no more itterative process than the data labelling. 

Bots are very similar to each other, they all have something similar between each other. It can be the Bio hey use, the comments, the scam domain, the photos, anything. So when I was finding a new bot with a technique, I could use it to find other bots.

I divided the labelling in three parts: Manual labelling where I had to look at each user one by one, Semi-automatic labelling where I could look at some users' attribute and label a batch of them and automatic labelling where I could label users without looking. I listed below all the different techniques I used. The order is not important, I used one, came back to the other, six month later thought of a new one and still came back to the first one, and so on.


## Manual Labelling
This was the most annoying and slow process. I had to go though each user one by one, look at their photos, comments, bio, and decide if they were a bot or not. To same me some time and minimize my decision making, I build user summaries photos. Those summaries contains all the informations about the users: their photos, bio, accounts attributes like the number of followers, following, number of posts, etc. I also added the comments they made on other users posts. Having all those informations in one place made the manual labelling process much faster. I then build a small script to open each photo one by one and I would flag them as legit user, sex bots, other bots and I'm not sure, check again later. For each of them, I labelled them twice as I know that errors can easily happen. At best, I labelled a user every 2s meaning at least 4s was needed to label any user which is very costly. 

This step was needed for the other labelling techniques to work.


## Semi Manual Labelling
### 1. Image Dupes: XX labels
When doing the manual labelling, I found out that many of the bots have the same profile picture and photos on the profile. I randomly learnt on Linkedin about Image Dupes which is a technique to find duplicate images in a given directory. I used it to find duplicates images and then grouped them in a folder where they were ordered by most to least duplicates. Some had errors and where far from the same so I just removed them.Once the folder was free from non bots, I could label them all at once. This is some of the "clean" folder.



ADD GIF ABOUT IT






### Explain about the model helper and how it discovered the other bots
The model helper was here for me when I was doing manual labelling. It was projecting on the screen a green or red color depending if the next user was predicted to be a bot rather than a human. It would also display the prediction and turn the color orange if the likelihood was between 10% and 90%. The model was already quite good with a 90% accuracy and F1 which helped me label users a little faster. 