# BotSlayer-CE (Community Edition)

## Installation instructions

To install BotSlayer-CE on any linux machine, user needs to first properly install the container software `docker`. Please follow the instructions on [Docker's website](https://docs.docker.com/install/). Please remember to add your current user to the `docker` user group, which will avoid the `sudo` command in using `docker`. 

With `docker` installed, you can then proceed to clone this repository, e.g.

    git clone https://github.com/IUNetSci/BotSlayer-CE.git

Enter the repo directory, and build the docker image by

    docker build --tag=bsce .
    
Upon completion of the image building, you can setup storage volumes and run the container by

    docker volume create pgdata
    docker run -dit -p 5432:5432 -p 5000:5000 -p 9001:9001 -v pgdata:/var/lib/postgresql/data bsce
    
If the container starts successfully, you should be able to find our frontend at `http://localhost:5000`, with logging running at `http://localhost:9001`.

## Summary of BotSlayer-CE

As social media became major platforms for political campaigns and discussions of other important issues, concerns have been growing about manipulation of the information ecosystem by bad actors.
Typical techniques used by the bad actors vary from astroturf and amplification of misinformation to trolling .
Attempts to manipulate discussions may and often does involve real humans; examples include trolls from Russia and Iran.
Recent reports show that malicious social bots --- inauthentic accounts controlled in part by software --- have been active during the U.S. presidential election in 2016, the 2017 Catalan referendum in Spain, the French Presidential Election of 2017, and the 2018 U.S. midterm election.

Detecting such manipulation presents serious research challenges. 
First, one needs to collect and analyze data, which requires significant storage and computing resources.
Second, finding patterns and signals of suspicious behaviors from huge amounts of data requires advanced computational skills.
In fact, most studies on this phenomenon are disseminated months or even years after the events.
Detecting potential manipulations from real-time social media data streams remains an open challenge.

To address this challenge, we developed a tool to detect and track potential amplification of information by likely coordinated bots on Twitter in real time.
The tool is called `BotSlayer`. Here we introduce `BotSlayer-CE`, the open-source Community Edition of the tool. There is also [a free but not open-source version](https://osome.iuni.iu.edu/tools/botslayer) that includes a proprietary bot detection software.

BotSlayer-CE is easy to install and can be customized to any topics of interest.
Its embedded algorithms and user-friendly interface make it possible for experts as well as reporters and citizens to study online manipulation. 

![Figure 1: System architecture of BotSlayer-CE.](system_design.png)

**Figure 1** shows an overview of the BotSlayer-CE system architecture with its backend and frontend.
The backend collects and analyzes tweets, while the frontend renders a dashboard that reports suspicious content to users.
The backend consists of a database, a tweet collector, and the middleware APIs for the frontend clients.

Data collection is query-driven and requires a Twitter app key.
The user-defined query is a set of keywords of interest, see [Twitter's document](https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters.html#track) for details.
These keywords are fed to Twitter's filtering API to fetch a stream of related tweets. The software extracts entities (hashtags, user handles, links, and media) for further analysis. 

Entities are stored in a PostgreSQL database, interfaced with the tweet collector and the middleware using `asyncpg` and `asyncio` in Python3.
All statistical and machine learning calculation are implemented in SQL query to leverage database concurrency on the server machine.
The whole backend is wrapped inside a Docker container to allow flexible and portable deployment.

BotSlayer-CE provides users with a dashboard that is accessible through any web browser.
The frontend allows users to set up the app key and change query of interest through a configuration page. 
The main page displays statistics of entities related to the query, ordered from the most suspicious to the least by a metric called `BS Level`.
Users can also re-order the entities by different metrics like botness and trendiness, or filter them by keywords or types to explore potentially suspicious behaviors.
For each entity, the dashboard provides links for users to go back to Twitter to check the original discussion or search on Google.
Users can also visualize the discourse around each entity on [Hoaxy](https://hoaxy.iuni.iu.edu/).
Finally, users can export aggregated statistics as spreadsheets.

To calculate the BS level of an entity, we extract four features: volume, trendiness, diversity, and botness in 4-hour sliding windows and apply logistic regression based on a manually annotated training set.
For the volume, we count the number of tweets containing each entity during the focal time window.
Trendiness is calculated as the ratio between the entity volume in two consecutive time windows.
The diversity is the ratio between the number of unique users and the number of tweets they post.
Finally, botness measures the level of bot-like activity.
The intuition for the BS level is that entities with intermediate diversity and high volume, trendiness, and botness tend to be more suspicious.

To measure the botness, BotSlayer-CE is equipped with a simple rule-based bot scoring function.
The bot scoring function uses simple heuristics based on high friend growth rate, high friend/follower ratio, high tweeting frequency, and default profile image to calculate bot scores. These heuristics yield about 0.70 AUC when tested on annotated accounts. They may be appropriate to detect some bots and not others. Depending on the research domain, different bot detection algorithms may be advisable. One can plug their favorite bot detection system into the `BotRuler` class ([BotRuler.py](https://github.com/IUNetSci/BotSlayer-CE/blob/master/backend/bev_backend/bev_backend/crawler/BotRuler.py)). One could implement simpler heuristics based on [high tweet rate](https://arxiv.org/abs/1606.06356) or [default profile image](https://arxiv.org/abs/1507.07109), use [state-of-the-art machine learning bot detection tools](https://botometer.iuni.iu.edu/), or train their own classifier. For example, the ["Pro" version of BotSlayer](https://osome.iuni.iu.edu/tools/botslayer/) uses a proprietary bot detection software. 
Accounts that display the suspicious behaviors mentioned above will have scores close to 1.
