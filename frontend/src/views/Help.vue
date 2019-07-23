<template>
    <div class="help">
        <div>
            <b-card-group deck class="margin-10-px">
                <b-card style="background-color: #147340; color: white;" title="Entities are the things you're searching for:">
                    <b-list-group>
                        <b-list-group-item variant="success" target="_blank" href="https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters.html#track">Click for Twitter Documentation for tracking Entities</b-list-group-item>
                        <b-list-group-item variant="success" router-link to="/Config">Click to return to Config to try it out!</b-list-group-item>
                    </b-list-group>
                </b-card>
            </b-card-group>
            <b-card-group deck class="margin-10-px">
                <b-card style="background-color: #147340; color: white;" title="Need Assistance with Twitter keys?:">
                    <b-list-group>
                        <b-list-group-item variant="success" target="_blank" href="https://developer.twitter.com/en/apply/user">1) Apply for a Twitter Developer Account</b-list-group-item>
                        <b-list-group-item variant="success" target="_blank" href="https://developer.twitter.com/en/docs/basics/apps/overview">2) Create a Twitter App</b-list-group-item>
                        <b-list-group-item variant="success" target="_blank" href="https://developer.twitter.com/en/docs/basics/authentication/guides/access-tokens.html">3) Use Access Tokens on BotSlayer-CE</b-list-group-item>
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
            <p>© BotSlayer-CE</p>
        </div>
    </div>
</template>

<script>
</script>

<style scoped>
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
