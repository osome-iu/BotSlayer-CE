# Warning

The "CE" version of BotSlayer is not meant for research, as it uses simple heuristics to calculate bot scores. We strongly recommend the ["Pro" version of BotSlayer](https://osome.iuni.iu.edu/tools/botslayer/), which has proprietary BotometerLite software and many other improvements. It is available for free, but will share data with Indiana University for research purposes.

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

## Introduction

Ever since social media became one of the major platforms for political campaigns and discussion of other important issues, the concern of bad actors' manipulation has been growing.
Recent reports show social bots, algorithm controlled social media accounts that act automatically, have been active during U.S. presidential elections in 2016, 2017 Catalan referendum in Italy, French Presidential Election of 2017 and 2018 U.S. midterm elections .
Other attempts to manipulate the discussion may involve real humans.
Examples include Russian and Iran trolls.
Typical techniques used by the bad actors vary from astroturfing, amplification of misinformation to trolling.

Detecting such manipulation has never been easy, even for researchers.
First, one needs to collect data which requires certain skills and computational resources.
Second, finding patterns and signals of suspicious behaviors from huge amount of data takes great efforts and advanced techniques.
In fact, most of the studies on this matter are finished months, even years, after the events.
Facing potential manipulations in the fresh stream data on social media everyday remains a challenge for everyone.

To mediate this issue, we introduce BotSlayer-CE, a tool to track and detect potential manipulation of information spreading by bots on Twitter in real time.
BotSlayer-CE is easy to install and can be customized to any topics of interest.
The embedded algorithm and user friendly interface enable anyone to detect and research on coordinated amplification of information by bots happening at the moment.

## BotSlayer-CE architecture

The system of BotSlayer-CE can be divided into its backend and its frontend:
![botlayerce_architecture](system_design.png)

The backend collects and analyzes tweets, while the frontend renders a dashboard that reports suspicious content to users.
The backend of BotSlayer-CE consists of a database, a tweet collector, and the middleware APIs for the frontend clients.
We use PostgreSQL database, interfaced with the tweet collector and the middleware using asyncpg and asyncio in Python3.
All calculation of statistics and predictions are implemented in SQL query to maximally utilize database concurrency on the server machine.
The whole backend is wrapped inside a Docker container to allow flexible and portable deployment.

BotSlayer-CE provides users with a dashboard.
Users can access the dashboard through any web browser.
The statistics of entities related to the query will be displayed on the dashboard.
The entities are ordered from the most suspicious to the least by the so-called BS Level.
Users can also re-order the entities by different metrics like botness and trendiness, or filter them by key words or types to explore potentially suspicious behaviors.
For each entity, the dashboard provides links for users to go back to Twitter to check the original discussion or search for it on Google.
User can also visualize the discourse around each entity on [Hoaxy](https://hoaxy.iuni.iu.edu/).
After sufficient exploration, users can export the aggregated statistics as spreadsheets to persist records for suspicious activities.
The frontend also allows the users to set up the app key and change query of interest through config page.

Data collection of BotSalyer is query-driven and requires a Twitter app key.
The user-defined query is a set of keywords of interest.
They can be hashtags, user handles, URLs, or free-form text.
These keywords are fed to Twitter's filtering API to fetch related tweets, which are then stored in a database for further analysis.
Valid keywords for the query and associated examples are detailed in the [documentation of Twitter APIs](https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters.html#track).

## BotSlayer-CE algorithms

As the core of BotSlayer-CE, BS level measure how suspicious each entity is.
To calculate BS level, we extract four features: volume, trendiness, diversity and botness in 4-hour windows for each entity and apply Logistic Regression.
We simply count the number of tweets containing each entity during the focal time window as volume of each entity.
The trendiness of each entity is calculated as the ratio between the volume in two consecutive time windows.
The the diversity is the ratio between the number of unique users and the number of tweets they post.
And botness measures the level of bot-like activities evolved with each entity.
Generally speaking, entities with high volume, trendiness, botness and relatively low diversity tend to be more suspicious.

To measure the botness, BotSlayer-CE is equipped with a simple rule-based bot detection tool.
Since bots typically tend to tweet more frequently, gain more friends in short time, have less followers and use default profile and so on, the bot detection tool inspects the profile of each account and produce a bot score between 0 and 1.
Accounts that demonstrate the suspicious behaviors mentioned above will have scores close to 1 whereas normal accounts will have scores close to 0.
Bot detection is a non-trivial task and often requires more complicated algorithms like machine learning to achieve good performance.
The embedded rule-based bot detection tool yields about 0.70 AUC when tested on annotated accounts shared in while state-of-the-art machine learning based bot detection tools typically have over 0.95 AUC in the same tests.
It provides useful signals for BotSlayer-CE, but is not accurate and robust enough for any serious scientific research.
For more accurate botness estimation, users can either resort to established tools like [Botometer](https://botometer.iuni.iu.edu/}\cite{davis2016botornot,varol2017online) or train a classifier on their own.
We also offer an 'PRO' version of BotSlayer with proprietary bot detection software which provides better bot detection support.
