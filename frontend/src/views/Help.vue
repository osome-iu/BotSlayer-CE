<template>
    <div class="help">
        <div>
            <b-card-group deck class="margin-10-px">
                <b-card style="background-color: #147340; color: white;" title="Select tweets matching any of these criteria:">
                    <b-list-group>
                        <b-list-group-item target="_blank" href="https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters.html#track">Track: enter keywords, hashtags, usernames, or links to filter matching tweets. Click here for Twitter documentation.</b-list-group-item>
                        <b-list-group-item target="_blank" href="https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters.html#follow">Follow: enter Twitter account IDs to filter tweets matching specific accounts. Click here for Twitter documentation.</b-list-group-item>
                        <b-list-group-item target="_blank" href="https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters.html#locations">Locations: enter the coordinates of a geo-bounding box to filter tweets within a specific location. Click here for Twitter documentation.</b-list-group-item>
                    </b-list-group>
                </b-card>
            </b-card-group>
            <!-- <b-card-group deck class="margin-10-px">
                <b-card style="background-color: #147340; color: white;" title="Need Assistance with Twitter keys?">
                    <b-list-group>
                        <b-list-group-item variant="primary" target="_blank" href="https://developer.twitter.com/en/apply/user">1. Apply for a Twitter Developer Account. Click here for Twitter documentation.</b-list-group-item>
                        <b-list-group-item variant="primary" target="_blank" href="https://developer.twitter.com/en/docs/basics/apps/overview">2. Create a Twitter App. Click here for Twitter documentation.</b-list-group-item>
                        <b-list-group-item variant="primary" target="_blank" href="https://developer.twitter.com/en/docs/basics/authentication/guides/access-tokens.html">3. Use Access Tokens on BotSlayer-CE. Click here for Twitter documentation.</b-list-group-item>
                        <b-list-group-item variant="primary">
                            <iframe width="560" height="315" src="https://www.youtube.com/embed/6hsNOV1VDq8?start=289" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                        </b-list-group-item>
                    </b-list-group>
                </b-card>
            </b-card-group> -->
            <!-- <b-card-group deck class="margin-10-px">
                <b-card class="text-left" style="background-color: #147340; color: white;" title="What happens if I do not enter any filtering criteria?">
                    <b-card-text>
                        If all three filtering criteria in the Config database table (track, follow, locations) are empty,
                        BotSlayer-CE will collect a sample of the public tweet stream.
                    </b-card-text>
                </b-card>
            </b-card-group> -->
             <b-card-group deck class="margin-10-px">
                <b-card class="text-left" style="background-color: #147340; color: white;" title="What is an entity?">
                    <b-card-text>
                        Entities are pieces of information that appear in tweets and retweets matching the query. An entity
                        can be a hashtag, link, image, video, user handle, or text phrase.
                    </b-card-text>
                </b-card>
            </b-card-group>
           <b-card-group deck class="margin-10-px">
                <b-card class="text-left" style="background-color: #147340; color: white;" title="What do the columns in the dashboard mean?">
                    <b-card-text>
                        <strong>Tweets</strong>: Number of tweets and retweets that match the query and contain this entity in the last four hours.
                    </b-card-text>
                    <b-card-text>
                        <strong>Accounts</strong>: Number of distinct accounts tweeting messages that match the query and contain this entity in the last four hours.
                    </b-card-text>
                    <b-card-text>
                        <strong>Trendiness</strong>: Relative change in the number of tweets that match the query and contain this entity in the last four hours, compared to the previous four hours.
                    </b-card-text>
                    <b-card-text>
                        <strong>Botness</strong>: Average bot score across tweets that match the query and contain this entity in the last four hours. The score is not a probability or likelihood, but the higher it is, the greater the chances that there are bots amplifying this entity.
                    </b-card-text>
                    <b-card-text>
                        <strong>BS Level</strong>: Anomaly score that combines tweets, accounts, trendiness, and botness. The higher the BS level of an entity, the higher the estimated likelihood that the entity may be supported by a coordinated campaign involving social bots.
                    </b-card-text>
                </b-card>
            </b-card-group>
            <b-card-group deck class="margin-10-px">
                <b-card class="text-left" style="background-color: #147340; color: white;" title="What are the icons in the Research column?">
                    <b-card-text>
                        When you click on the plot icon in the Research column next to an entity, 
                        you will see timelines for the key quantities related to the entity. 
                        Clicking on the Hoaxy icon will visualize the diffusion network of the selected entity
                        on Hoaxy: who is being retweeted/quoted/mentioned by whom, and is there suspicious 
                        activity by likely automated accounts. The Twitter and Google icons will generate search 
                        queries on those respective platforms; for image entities, BotSlayer-CE performs a reverse 
                        image search on Google to find related images from the web.
                    </b-card-text>
                </b-card>
            </b-card-group>
            <b-card-group deck class="margin-10-px">
                <b-card class="text-left" style="background-color: #147340; color: white;" title="What is time warp?">
                    <b-card-text>
                        The BotSlayer-CE dashboard normally shows you what is happening right now. Use the time warp
                        feature to go back in time. Enter a past date/time and you will see what you would have seen 
                        on the dashboard at that point in time. Click the Now button to go back to the present.
                    </b-card-text>
                </b-card>
            </b-card-group>
            <b-card-group deck class="margin-10-px">
                <b-card class="text-left" style="background-color: #147340; color: white;" title="Is my BotSlayer-CE dashboard secure? Can I share the URL/IP/link address of my instance?">
                    <b-card-text>
                        Your BotSlayer-CE dashboard is accessible via the Web using the IP address of the server. 
                        It is accessible to anyone with the IP or URL; it is not secure and it is not encrypted. 
                        It is the user's responsibility to secure their data and abide by the Twitter's terms of service. 
                        We strongly recommend against sharing the IP or URL with anyone outside your organization 
                        or anyone you do not trust. In particular, do not share the link on social media or any 
                        public forum. People could easily steal the password, make changes to the system, and/or 
                        access data in violation of Twitter terms of service. 
                        We strongly recommend that your system administrator reconfigure the website 
                        to use HTTPS access with a trusted certificate, especially if you wish to share the 
                        dashboard publicly.
                    </b-card-text>
                </b-card>
            </b-card-group>
            <b-card-group deck class="margin-10-px">
                <b-card class="text-left" style="background-color: #147340; color: white;" title="Can I spin up multiple instances on the same machine?">
                    <b-card-text>
                        In theory, yes. You would need to map the internal Docker port (5000) 
                        to a different port for the server/system in each Docker container/instance. 
                        You would also want to create new volumes to persist database and
                        directory storage for each container. However, we have not tested how the performance 
                        of Docker containers scales in the same machine. If more than a few people
                        access the Web dashboards at the same time, the CPU demands to handle API requests 
                        may cause performance issues with multiple containers in the same machine.
                    </b-card-text>
                </b-card>
            </b-card-group>
            <b-card-group deck class="margin-10-px">
                <b-card class="text-left" style="background-color: #147340; color: white;" title="The system is slow or non-responsive. What can I do?">
                    <b-card-text>
                        If you run into issues with the dashboard being unresponsive, you do not see data being collected, 
                        or BotSlayer-CE is not running as expected, pay attention to the warnings at the top of the dashboard. 
                        For example, you may be hitting the Twitter API rate limit, so you may need to focus your query. 
                        If there is no warning pointing to the cause of the problems, you should consider using a server with 
                        more system resources (disk, CPU, memory).
                    </b-card-text>
                </b-card>
            </b-card-group>
            <b-card-group deck class="margin-10-px">
                <b-card class="text-left" style="background-color: #147340; color: white;" title="Can I spin up multiple instances with the same app key?">
                    <b-card-text>
                        We strongly recommend against it, as it will cause unpredictable errors. 
                        Each key has a rate limit. If you hit the rate limit, the software will stop 
                        collecting data by catching a rate limit error, and will wait for a while to restart 
                        the collection. One instance usually doesn't cause the rate limit error, because it
                        doesn't collect enough tweets, and can recover from rate limit errors. However, 
                        using the same key for multiple instances (even just two) will hit the rate limit error 
                        routinely and we have no control on which instance will stop its
                        collection when this happens.
                    </b-card-text>
                </b-card>
            </b-card-group>
            <b-card-group deck class="margin-10-px">
                <b-card style="background-color: #147340; color: white;" title="What are the BotSlayer-CE terms of service?">
                    <b-list-group>
                        <b-list-group-item target="_blank" href="https://osome.iuni.iu.edu/tools/botslayer/eula.html">Please refer to the BotSlayer End-User License Agreement (EULA)</b-list-group-item>
                    </b-list-group>
                </b-card>
            </b-card-group>
            <b-card-group deck class="margin-10-px">
                <b-card style="background-color: #147340; color: white;" title="How can I provide feedback?">
                    <b-list-group>
                        <b-list-group-item target="_blank" href="https://osome.iuni.iu.edu/contact/">Please refer to the contact page of the Observatory on Social Media</b-list-group-item>
                    </b-list-group>
                </b-card>
            </b-card-group>
        </div>
        <div class="footer">
            <a href="https://osome.iuni.iu.edu/" target="_blank ">OSoMe</a>
                | 
            <a href="http://iuni.iu.edu/" target="_blank ">IUNI</a>
                | 
            <a href="http://cnets.indiana.edu/" target="_blank ">CNetS</a>
            <p>© BotSlayer-CE 2019</p>
        </div>
    </div>
</template>

<script>
</script>

<style scoped>
    .text-left
    {
        text-align: left;
    }
    .btn-outline-primary
    {
        background-color: white;
        margin: 10px;
    }
    .margin-10-px
    {
        margin: 10px;
    }
    .footer
    {
        color: white;
        background-color: #147340;
    }
    .footer a
    {
        color: lightgray;
    }
    .footer a:hover
    {
        color: white;
    }
    .footer p
    {
        margin-bottom: 0px;
    }
</style>
