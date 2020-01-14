<template>
    <div class="dataPage" style="overflow: auto;">
        <b-card v-if="!closedCE" bg-variant="danger">
            <b-card-text style="color: white">
                <b-btn-close @click="closeCE()" style="color: white"></b-btn-close>
                &#9888;
                <strong>
                    The "CE" version uses simple heuristics to calculate bot scores.
                    Depending on the research domain, more advanced algorithms with higher accuracy may be advisable.
                    <br>We strongly recommend the <a style="color: lightgray" target="_blank" href="https://osome.iuni.iu.edu/tools/botslayer/">"Pro" version of BotSlayer</a>, which has proprietary BotometerLite software and many other improvements. 
                    <br>It is available for free, but will share data with Indiana University for research purposes.
                </strong>
                &#9888;
            </b-card-text>
        </b-card>
        <b-card v-if="(diskRemaining < 20) && showDiskMessage" style="background-color: orange">
            <b-card-text style="color: white">
                <strong>{{this.diskRemaining}}% free disk space. Old data will be automatically deleted when less than 25% remains.</strong> 
                <br>You can add disk space to your server to alleviate the issue.
            </b-card-text>
        </b-card>
        <b-form-group class="margin-10-px" style="margin-top: 0px">
            <div style="margin-bottom: 10px">
            <span style="font-size: 110%; margin-right: 10px;">
                <span style="color: #00bb00;"><strong>Query: </strong></span>
                <span v-b-tooltip :title="this.configINI.seed.toString()" v-if="this.configINI.seed.toString().split(',').length > 3" style="border-bottom: 1px dotted; margin: 3px" id="span-if">{{shortSeed(this.configINI.seed.toString())}}...</span>
                <span v-b-tooltip :title="this.configINI.seed.toString()" v-else style="border-bottom: 1px dotted; margin: 3px" id="span-else">{{this.configINI.seed.toString()}}</span>

                <b-button v-b-tooltip :title="'Shows the results without the query: ' + this.configINI.seed.toString()" style="margin: 3px; margin-right: 60px" variant="primary" @click="excludeQuery(); autoRefresh();"><span v-if="this.excludeCheck">Include</span><span v-else>Exclude</span></b-button>
                
                <b-button v-b-tooltip :title="'Choose a local date and time, and then press Time Warp to see prior results. Your time zone is: ' + this.timeZoneAbbreviation + ' (' + this.offsetGMT + ')'" style="margin: 3px; padding: 3px" variant="primary"><datetime type="datetime" v-model="whenBS" use12-hour></datetime></b-button>
                <b-button v-b-tooltip title="Sends BotSlayer-CE back to the date and time chosen on the left." style="margin: 3px" variant="primary" @click="timeWarp(whenBS);">Time Warp</b-button>                
                <b-button v-if="!backInTime" v-b-tooltip title="Refreshes the table with the latest data." style="margin: 3px; margin-right: 60px" variant="primary" @click="demoScore();"><strong>&#8635;</strong> Refresh</b-button>
                <b-button v-if="backInTime" v-b-tooltip title="Returns BotSlayer-CE to the present date and time." style="margin: 3px; margin-right: 60px" variant="primary" @click="autoRefresh();"><strong>&#8635;</strong> Now</b-button>     
                <!--
                    Middleware portion needs some work. May return in beta version.
                    <b-button v-b-tooltip :title="'Pauses collection and stops auto-refresh. To re-enable auto-refresh, simply refresh the page.'" style="margin-left: 5px" variant="primary" @click="pauseCollection(collecting)"><span v-if="collecting">Pause</span><span v-else>Resume</span></b-button>
                -->
                <b-button v-b-tooltip title="Downloads a .csv file containing the data in the table below." style="margin: 3px" variant="primary" @click="downloadCSV();">Export</b-button>
            </span>
            </div>
            
            <div class="container d-flex flex-wrap" style="margin: 10px; max-width: 100%">
                <b-form-checkbox-group style="width: 100%" id="checkbox-group" v-model="scoreDemoFilter" name="demoFilters" switches>
                    <div class="d-flex flex-wrap">
                        <div class="col-lg-1"></div>
                        <span class="col-lg-1" style="font-size: 110%; margin-right: 10px; padding: 0; color: #00bb00;"><strong>Show Only:</strong></span>
                        <b-form-input class="col-lg-3" size="sm" v-model="filter" placeholder="Filter results" style="margin-right: 10px"></b-form-input>  
                        <b-form-checkbox class="col-lg-1" @input="onFiltered(filteredScoreDemoArr)" v-model="scoreDemoFilter" value="hashtags">Hashtags</b-form-checkbox>
                        <b-form-checkbox class="col-lg-1" @input="onFiltered(filteredScoreDemoArr)" v-model="scoreDemoFilter" value="urls">Links</b-form-checkbox>
                        <b-form-checkbox class="col-lg-1" @input="onFiltered(filteredScoreDemoArr)" v-model="scoreDemoFilter" value="media">Pics/Vids</b-form-checkbox>
                        <b-form-checkbox class="col-lg-1" @input="onFiltered(filteredScoreDemoArr)" v-model="scoreDemoFilter" value="intext">Text</b-form-checkbox>
                        <b-form-checkbox class="col-lg-2" @input="onFiltered(filteredScoreDemoArr)" v-model="scoreDemoFilter" value="user_mentions">User Mentions</b-form-checkbox>
                    </div>
                </b-form-checkbox-group>
            </div>
        </b-form-group>

        <div class="container">
            <div class="row align-items-center">
                <div class="col-lg-4">
                    <span class="multi-select" style="font-size: 110%; color: #00bb00;"><strong>Analyze Multiple: </strong></span>
                    <!-- BS data on Hoaxy -->
                    <span class="multi-select" v-if="selectedEntities.length > 0" target="_blank" v-b-tooltip :title="'Visualize your BotSlayer data with Hoaxy'" @click.stop.prevent="sendToHoaxy(0, whenBS, 'test')"><font-awesome-icon style="color: #14aa40; cursor: pointer" onmouseover="this.style.color='#14cc40'" onmouseout="this.style.color='#14aa40'" icon="robot"></font-awesome-icon></span>
                    <span class="multi-select" v-else v-b-tooltip :title="'(Disabled because you must select 1 or more entities)'"><font-awesome-icon style="color: #7b7b7b; cursor: pointer" onmouseover="this.style.color='#565656'" onmouseout="this.style.color='#7b7b7b'" icon="robot"></font-awesome-icon></span> 
                    <!-- Search on live Hoaxy -->
                    <a class="multi-select" v-if="selectedEntities.length > 0" target="_blank" v-b-tooltip :title="'Visualize what\'s happening right now with Hoaxy'" @click.stop.prevent="hoaxyLive()"><font-awesome-icon style="color: #14aa40; cursor: pointer" onmouseover="this.style.color='#14cc40'" onmouseout="this.style.color='#14aa40'" icon="heartbeat"></font-awesome-icon></a>
                    <a class="multi-select" v-else target="_blank" v-b-tooltip :title="'(Disabled because you must select 1 or more entities)'"><font-awesome-icon style="color: #7b7b7b; cursor: pointer" onmouseover="this.style.color='#565656'" onmouseout="this.style.color='#7b7b7b'" icon="heartbeat"></font-awesome-icon></a>
                    <!-- Timeline -->
                    <span class="multi-select" v-if="selectedEntities.length > 0" v-b-tooltip :title="'Explore how these entities have changed over time'" v-b-modal.timeline-modal @click="getTimelines(0, 'test', whenBS)"><font-awesome-icon style="color: #14aa40; cursor: pointer" onmouseover="this.style.color='#14cc40'" onmouseout="this.style.color='#14aa40'" icon="chart-line" /></span> 
                    <span class="multi-select" v-else v-b-tooltip :title="'(Disabled because you must select 1 or more entities)'"><font-awesome-icon style="color: #7b7b7b; cursor: pointer" onmouseover="this.style.color='#565656'" onmouseout="this.style.color='#7b7b7b'" icon="chart-line" /></span>
                    <!-- Tweet Share Button -->
                    <!-- <span id="twitter-button">
                        <a class="twitter-share-button"
                        href="https://twitter.com/share"
                        target="_blank"
                        :data-text="'Check out' + tweetEntityNames + 'https://hoaxy.iuni.iu.edu/#query=' + tweetHoaxyEntityNames + '&sort=mixed&type=Twitter found with #BotSlayer from @osome_IU'"
                        data-url="/"
                        data-size="large">
                        Tweet</a>
                        <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
                    </span> -->
                </div>
                <div class="col-lg-3 align-self-center">
                    <b-pagination v-if="tablePresent" align="center" v-model="pageNum" :total-rows="totalData" :per-page="perPage"></b-pagination>
                </div>
                <div class="col-lg-1"></div>
                <div class="col-lg-2">
                    <b-form-select style="margin-bottom: 16px" v-if="tablePresent" v-model="perPage" :options="options"></b-form-select>
                </div>
                <div class="col-lg-1"></div>
            </div>
        </div>

        <b-spinner style="width: 5rem; height: 5rem;" v-if="tableBusy" variant="primary"></b-spinner>

        <div v-if="(!tablePresent && !tableBusy)">
            <b-card class="margin-10-px" v-if="this.serverError" bg-variant="danger" text-variant="white">
                <b-card-text>
                    BotSlayer-CE has encountered a technical error.
                </b-card-text>
            </b-card>
            <b-card class="margin-10-px" v-else-if="this.insufficientData" style="background-color: #00bb00;" text-variant="white">
                <b-card-text>
                    BotSlayer-CE has collected a very small amount of data for this query.
                    <br>If you've been waiting a while, feel free to try changing the query.
                    <br>For instance, maybe more tweets are containing #puppies rather than #puppy today.
                </b-card-text>
            </b-card>
            <b-card class="margin-10-px" v-else-if="this.emptyArray" style="background-color: #00bb00;" text-variant="white">
                <b-card-text>
                    BotSlayer-CE hasn't collected any data for this query.
                    <br>Try testing a really popular hashtag or user for your query.
                    <br>If the table still doesn't appear below, check the Config page to see that the Twitter keys match.
                </b-card-text>
            </b-card>
        </div>

        <b-table v-model="tableVisibleRows" v-if="tablePresent" @filtered="onFiltered" stacked="lg" striped hover bordered outlined :filter="filter" :items="filteredScoreDemoArr" :fields="scoreDemoFields" :busy="tableBusy" :per-page="perPage" :current-page="pageNum" :sort-by.sync="sortBy" :sort-desc.sync="sortDesc" :sort-direction="'desc'">
            <!-- Programmatic header adjustment -->
            <template v-slot:head(BS_Level)="data">
                <span v-b-tooltip.hover.html="data.field.headerTitle">{{ data.label }}</span>
            </template>
            <template v-slot:head(Tweets)="data">
                <span v-b-tooltip.hover.html="data.field.headerTitle">{{ data.label }}</span>
            </template>
            <template v-slot:head(Accounts)="data">
                <span v-b-tooltip.hover.html="data.field.headerTitle">{{ data.label }}</span>
            </template>
            <template v-slot:head(Trendiness)="data">
                <span v-b-tooltip.hover.html="data.field.headerTitle">{{ data.label }}</span>
            </template>
            <template v-slot:head(Botness)="data">
                <span v-b-tooltip.hover.html="data.field.headerTitle">{{ data.label }}</span>
            </template>
            <template v-slot:head(Selected)="data">
                <span>
                    <font-awesome-icon v-if="anythingChecked" @click.stop.prevent="uncheckAll()" :icon="['far', 'check-square']" />
                    <font-awesome-icon v-if="!anythingChecked" @click.stop.prevent="checkAll()" :icon="['far', 'square']" />
                </span>
            </template>

            <!-- Virtual composite columns -->
            <template v-slot:cell(Research)="data">
                <span v-b-tooltip :title="'Explore how this entity has changed over time'" v-b-modal.timeline-modal @click="getTimelines(data.item.EntityID, data.item.Entity, whenBS, true)"><font-awesome-icon style="color: #14aa40; cursor: pointer" onmouseover="this.style.color='#14cc40'" onmouseout="this.style.color='#14aa40'" icon="chart-line" /></span> 
                <span v-if="!(data.item.Type == 'media') && !(data.item.Type == 'urls')">
                    | <a target="_blank" v-b-tooltip :title="'Search with Twitter'" :href="'https://twitter.com/search/?q=' + encodeURIComponent(data.item.Entity)"><font-awesome-icon :icon="['fab', 'twitter']" /></a>
                </span>
                <span v-if="(data.item.Type == 'media') || (data.item.Type == 'urls')">
                    | <a target="_blank" v-b-tooltip :title="'Search with Twitter'" :href="'https://twitter.com/search/?q=' + encodeURIComponent(parseTwitterURL(data.item.Entity))"><font-awesome-icon :icon="['fab', 'twitter']" /></a>
                </span>
                <span v-if="(data.item.Type == 'media')">
                    | <a target="_blank" v-b-tooltip :title="'Search with Google'" :href="'https://www.google.com/searchbyimage?&image_url=' + data.item.MediaLink"><font-awesome-icon :icon="['fab', 'google']" /></a>
                </span>
                <span v-if="!(data.item.Type == 'media')">
                    | <a target="_blank" v-b-tooltip :title="'Search with Google'" :href="'https://www.google.com/search?q=' + encodeURIComponent(data.item.Entity)"><font-awesome-icon :icon="['fab', 'google']" /></a>
                </span>
                <span v-if="!(data.item.Type == 'media')">
                    | <a target="_blank" v-b-tooltip.hover.html="'<strong>[NSFW!]</strong><hr> Search with 4chan'" :href="'https://find.4chan.org/?q=' + encodeURIComponent(data.item.Entity)">
                          <svg version="1.1" class="four-chan" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="16px" y="16px"
                              viewBox="-154.2 86.1 374.7 389.9" style="enable-background:new -154.2 86.1 374.7 389.9;" xml:space="preserve">
                              <path d="M-129,124c0-26,84-61,123,85c0,0-127,25-145-4c-18-28,46-45,46-55S-129,149-129,124z M-129,124c0-26,84-61,123,85 c0,0-127,25-145-4c-18-28,46-45,46-55S-129,149-129,124z M-129,124c0-26,84-61,123,85c0,0-127,25-145-4c-18-28,46-45,46-55 S-129,149-129,124z M182,111c26,0,62,84-85,124c0,0-25-128,4-146c28-17,45,46,55,46S157,111,182,111z M182,111c26,0,62,84-85,124 c0,0-25-128,4-146c28-17,45,46,55,46S157,111,182,111z M182,111c26,0,62,84-85,124c0,0-25-128,4-146c28-17,45,46,55,46 S157,111,182,111z M191,439c-2,26-87,56-118-92c0,0,129-17,145,12c16,30-49,42-50,52C168,422,193,414,191,439z M191,439 c-2,26-87,56-118-92c0,0,129-17,145,12c16,30-49,42-50,52C168,422,193,414,191,439z M191,439c-2,26-87,56-118-92c0,0,129-17,145,12 c16,30-49,42-50,52C168,422,193,414,191,439z M-98,459c-26,3-70-77,71-132c0,0,39,124,12,145c-26,20-49-41-59-40 C-85,433-73,456-98,459z M-98,459c-26,3-70-77,71-132c0,0,39,124,12,145c-26,20-49-41-59-40C-85,433-73,456-98,459z M-98,459 c-26,3-70-77,71-132c0,0,39,124,12,145c-26,20-49-41-59-40C-85,433-73,456-98,459z"/>
                          </svg>
                      </a>
                </span>
                <span v-if="!(data.item.Type == 'media')">
                    | <a target="_blank" v-b-tooltip.hover="'Search with Facebook'" :href="'https://www.facebook.com/search/top/?q=' + encodeURIComponent(data.item.Entity)">
                          <font-awesome-icon :icon="['fab', 'facebook-square']" />
                      </a>
                </span>
                <span v-if="!(data.item.Type == 'media') && !(data.item.Type == 'urls')">
                    | <a target="_blank" v-b-tooltip.hover="'Search with Reddit'" :href="'https://www.reddit.com/search?q=' + encodeURIComponent(data.item.Entity) + '&sort=relevance&t=all'">
                          <font-awesome-icon :icon="['fab', 'reddit-alien']" />
                      </a>
                </span>
                <span v-if="(data.item.Type == 'media') || (data.item.Type == 'urls')">
                    | <a target="_blank" v-b-tooltip.hover="'Submit link to Reddit'" :href="'https://www.reddit.com/search?q=' + encodeURIComponent(data.item.Entity) + '&sort=relevance&t=all'">
                          <font-awesome-icon :icon="['fab', 'reddit-alien']" />
                      </a>
                </span>
                <span v-if="!(data.item.Type == 'media') && !(data.item.Type == 'urls')">
                    | <a target="_blank" v-b-tooltip.hover="'Search with YouTube'" :href="'https://www.youtube.com/results?search_query=' + encodeURIComponent(data.item.Entity)">
                          <font-awesome-icon :icon="['fab', 'youtube']" />
                      </a>
                </span>
            </template>
            <template v-slot:cell(Hoaxy)="data">
                <span v-if="data.item['Accounts'] > 1" target="_blank" v-b-tooltip :title="'Visualize your BotSlayer-CE data with Hoaxy'" @click.stop.prevent="sendToHoaxy(data.item.EntityID, whenBS, data.item.Entity, true)"><font-awesome-icon style="color: #14aa40; cursor: pointer" onmouseover="this.style.color='#14cc40'" onmouseout="this.style.color='#14aa40'" icon="robot"></font-awesome-icon></span> 
                <span v-if="data.item['Accounts'] == 1" v-b-tooltip :title="'(Disabled because more than 1 account is needed for a network)'"><font-awesome-icon style="color: #7b7b7b; cursor: pointer" onmouseover="this.style.color='#565656'" onmouseout="this.style.color='#7b7b7b'" icon="robot"></font-awesome-icon></span> 
                    | 
                <a target="_blank" v-b-tooltip :title="'Visualize what\'s happening right now with Hoaxy'" :href="'https://hoaxy.iuni.iu.edu/#query=' + data.item.Entity + '&sort=mixed&type=Twitter'"><font-awesome-icon icon="heartbeat"></font-awesome-icon></a> 
            </template>
            <template v-slot:cell(Selected)="data">
                <template v-if="selectedEntities.includes(data.item)">
                    <font-awesome-icon @click.stop.prevent="uncheck(data.item)" :icon="['far', 'check-square']" />
                </template>
                <template v-else>
                    <font-awesome-icon @click.stop.prevent="check(data.item)" :icon="['far', 'square']" />
                </template>
            </template>
            <template v-slot:cell(Entity)="data">
                <a target="_blank" v-if="(data.item.Type == 'media') || (data.item.Type == 'urls')" :href="'' + data.item.Entity">{{ parseStringURL(data.item.Entity.toString()) }}</a>
                <a target="_blank" v-if="(data.item.Type == 'user_mentions')" :href="'https://twitter.com/' + data.item.Entity.toString().substring(1)">{{ data.item.Entity }}</a>
                <a target="_blank" v-if="(data.item.Type == 'hashtags')" :href="'https://twitter.com/hashtag/' + data.item.Entity.toString().substring(1)">{{ data.item.Entity }}</a>
                <a target="_blank" v-if="(data.item.Type == 'symbols')" :href="'https://twitter.com/search?q=' + data.item.Entity.toString()">{{ data.item.Entity }}</a>
                <span v-if="(data.item.Type == 'intext')"><strong>{{ data.item.Entity }}</strong></span>
            </template>
            <template v-slot:cell(Last_Seen)="data">
                <span hidden>{{dateParser(data.item['Last_Seen'])}}</span>
                <timeago v-b-tooltip.hover.html="data.item['Last_Seen']" style="border-bottom: 1px dotted" id="lastSeen" :datetime="data.item['Last_Seen']" :auto-update="60"></timeago>
            </template>
            <template v-slot:cell(Trendiness)="data">
                <span>{{data.item.Trendiness}}%</span>
            </template>
            <template v-slot:cell(Botness)="data">
                <span>{{data.item.Botness}} / 5</span>
            </template>
            <template v-slot:cell(BS_Level)="data">
                <b-progress :value="parseFloat(data.item.BS_Level)" :max="1"></b-progress>
            </template>
        </b-table>

        <div class="container">
            <div class="row">
                <div class="col-lg-4"></div>
                <div class="col-lg-3">
                    <b-pagination v-if="tablePresent" align="center" v-model="pageNum" :total-rows="totalData" :per-page="perPage"></b-pagination>
                </div>
                <div class="col-lg-1"></div>
                <div class="col-lg-2">
                    <b-form-select v-if="tablePresent" v-model="perPage" :options="options"></b-form-select>
                </div>
                <div class="col-lg-1"></div>
            </div>
        </div>

        <div class="footer">
            <a href="https://osome.iuni.iu.edu/" target="_blank ">OSoMe</a>
                | 
            <a href="http://iuni.iu.edu/" target="_blank ">IUNI</a>
                | 
            <a href="http://cnets.indiana.edu/" target="_blank ">CNetS</a>
            <p>© BotSlayer-CE 2019</p>
        </div>

        <b-modal id="timeline-modal" size="xl" centered :title="'Timeline for ' + selectedEntityNames">
            <div class="d-flex justify-content-center">
                <b-spinner style="width: 5rem; height: 5rem;" v-if="chartsBusy" variant="primary"></b-spinner>
            </div>
            <div>
                <div class="d-flex">
                    <apexchart :key="chartComponentKey" style="width: 50%" height="400" type="line" :options="accountChartOptions" :series="accountSeries"></apexchart>
                    <apexchart :key="chartComponentKey" style="width: 50%" height="400" type="line" :options="tweetChartOptions" :series="tweetSeries"></apexchart>
                </div>
                <div class="d-flex">
                    <apexchart :key="chartComponentKey" style="width: 50%" height="400" type="line" :options="trendChartOptions" :series="trendSeries"></apexchart>
                    <apexchart :key="chartComponentKey" style="width: 50%" height="400" type="line" :options="botscoreChartOptions" :series="botscoreSeries"></apexchart>
                </div>
            </div>
        </b-modal>

        <b-modal v-model="noHoaxyData" centered :title="'Failed to send data to Hoaxy'">
            There were no interactions, such as retweets, replies, mentions, or quotes, involved with this entity.
        </b-modal>

        <!-- Replace with generic timeout modal later -->
        <b-modal v-model="sendToHoaxyTimeout" centered :title="'Timeout'">
            The database is slow to respond. Please try again in a few moments.
        </b-modal>

        <b-modal v-model="apiTimeout" centered :title="'Timeout'">
            The database is slow to respond. Please try again in a few moments.
        </b-modal>
        
        <!-- Hoaxy Test Environment -->
        <!-- <form style="display: none" target="_blank" method="POST" enctype="application/json" action="http://192.168.33.10/"> -->
        <!-- Hoaxy Live Environment -->
        <form style="display: none" target="_blank" method="POST" enctype="application/json" action="https://hoaxy.iuni.iu.edu">
            <textarea style="display: none" name="data" v-model="hoaxySubmitData"></textarea>
            <input style="display: none" id="hoaxySubmitForm" type="submit">
        </form>
    </div>
</template>

<script>
import Config from "../../config.json"
import { unparse } from 'papaparse'
export default 
{
    name: 'dataPage',
    data: function()
    {
        return{
            scoreDemoArr: [],
            scoreDemoFields:
            [
                {key: 'BS_Level', label: 'BS Level', headerTitle: 'Anomaly score that combines tweets, accounts, trendiness, and botness. The higher the BS level of an entity, the higher the estimated likelihood that the entity may be supported by a coordinated campaign involving social bots.', sortable: true},
                {key: 'Selected', label: ''},
                {key: 'Entity', label: 'Entity', sortDirection: 'asc', sortable: true, class: 'text-left'},
                {key: 'Hoaxy', label: 'Hoaxy'},
                {key: 'Research', label: 'Research'},
                {key: 'Last_Seen', label: 'Last Seen', sortable: true},
                {key: 'Tweets', label: 'Tweets', headerTitle: 'Number of tweets and retweets that match the query and contain this entity in the last four hours.', sortable: true},
                {key: 'Accounts', label: 'Accounts', headerTitle: 'Number of distinct accounts tweeting messages that match the query and contain this entity in the last four hours.', sortable: true},
                {key: 'Trendiness', label: 'Trendiness', headerTitle: 'Relative change in the number of tweets that match the query and contain this entity in the last four hours, compared to the previous four hours.', sortable: true},
                {key: 'Botness', label: 'Botness', headerTitle: 'Average bot score across tweets that match the query and contain this entity in the last four hours.', sortable: true, tdClass: function(value){
                    if(value.substring(0) < '1')
                    {
                        return "table-primary"
                    }
                    else if(value.substring(0) < '2')
                    {
                        return "table-success"
                    }
                    else if(value.substring(0) < '3')
                    {
                        return "table-warning"
                    }
                    else if(value.substring(0) < '4')
                    {
                        return "table-orange"
                    }
                    else if(value.substring(0) < '5')
                    {
                        return "table-danger"
                    }
                    else
                    {
                        return "table-danger"
                    }
                    return "";}},              
            ],
            sortBy: 'BS_Level', // Make into a bar that's filled up to max if most suspicious (this score / max score)
            sortDesc: true,
            tablePresent: false,
            tableBusy: false,
            serverError: false,
            insufficientData: false,
            emptyArray: false,
            collecting: true,
            options: 
            [
                { value: 5, text: 'Per page: 5' },
                { value: 10, text: 'Per page: 10' },
                { value: 15, text: 'Per page: 15' },
                { value: 20, text: 'Per page: 20' },
                { value: 25, text: 'Per page: 25' },
                { value: 30, text: 'Per page: 30' },
                { value: 35, text: 'Per page: 35' },
                { value: 40, text: 'Per page: 40' },
                { value: 45, text: 'Per page: 45' },
                { value: 50, text: 'Per page: 50' },
            ],
            perPage: 10,
            pageNum: 1,
            totalData: 100,
            originalTotalData: 100, // Used to return to unfiltered state
            refreshTimeoutDuration: 300000, // 5 minutes
            refreshTimeout: 0,
            filter: "",
            diskRemaining: 99.99,
            scoreDemoFilter: [],
            exclusion: ' ',
            excludeCheck: false,
            latestVersion: "0.0.0",
            localVersion: "0.0.0",
            outOfDate: false,
            messages: [""],
            whenBS: "",
            backInTime: false,
            hoaxySubmitData: "",
            timeZoneAbbreviation: "",
            offsetGMT: "",
            chartComponentKey: 0, // Used for refreshing Vue
            chartsBusy: false,
            showDiskMessage: true,
            noHoaxyData: false,
            closedCE: false,
            accountChartOptions: 
            {
                chart: 
                {
                    id: 'accountChart',
                    group: 'botslayer'
                },
                height: 400,
                title: 
                {
                    text: "Accounts"
                },
                xaxis: 
                {
                    type: 'datetime',
                    labels: 
                    {
                        minHeight: 50
                    }
                },
                yaxis:
                {
                    labels:
                    {
                        minWidth: 75
                    }
                },
                tooltip: 
                {
                    x: { format: 'MMM. dd - HH:mm' }
                },
                toolbar: 
                {
                    show: true,
                    tools: 
                    {
                        download: true,
                        selection: true,
                        zoom: true,
                        zoomin: true,
                        zoomout: true,
                        pan: true,
                        reset: true | '<img src="/static/icons/reset.png" width="20">',
                        customIcons: []
                    },
                    autoSelected: 'zoom' 
                },
                colors: ['#00188f', '#fff100', '#00bcf2', '#ff8c00', '#00b294', '#e81123', '#009e49', '#ec008c', '#bad80a', '#68217a'],
            },
            accountSeries: [{
                name: '# of accounts',
                data: []
            }],
            tweetChartOptions: 
            {
                chart: 
                {
                    id: 'tweetChart',
                    group: 'botslayer'
                },
                height: 400,
                title: 
                {
                    text: "Tweets"
                },
                xaxis: 
                {
                    type: 'datetime',
                    labels: 
                    {
                        minHeight: 50
                    }
                },
                yaxis:
                {
                    labels:
                    {
                        minWidth: 75
                    }
                },
                tooltip: 
                {
                    x: { format: 'MMM. dd - HH:mm' }
                },
                toolbar: 
                {
                    show: true,
                    tools: 
                    {
                        download: true,
                        selection: true,
                        zoom: true,
                        zoomin: true,
                        zoomout: true,
                        pan: true,
                        reset: true | '<img src="/static/icons/reset.png" width="20">',
                        customIcons: []
                    },
                    autoSelected: 'zoom' 
                },
                colors: ['#00188f', '#fff100', '#00bcf2', '#ff8c00', '#00b294', '#e81123', '#009e49', '#ec008c', '#bad80a', '#68217a'],
            },
            tweetSeries: [{
                name: '# of tweets',
                data: []
            }],
            trendChartOptions: 
            {
                chart: 
                {
                    id: 'trendChart',
                    group: 'botslayer'
                },
                height: 400,
                title: 
                {
                    text: "Trendiness (%)"
                },
                xaxis: 
                {
                    type: 'datetime',
                    labels: 
                    {
                        minHeight: 50
                    }
                },
                yaxis:
                {
                    labels:
                    {
                        minWidth: 75
                    }
                },
                tooltip: 
                {
                    x: { format: 'MMM. dd - HH:mm' }
                },
                toolbar: 
                {
                    show: true,
                    tools: 
                    {
                        download: true,
                        selection: true,
                        zoom: true,
                        zoomin: true,
                        zoomout: true,
                        pan: true,
                        reset: true | '<img src="/static/icons/reset.png" width="20">',
                        customIcons: []
                    },
                    autoSelected: 'zoom' 
                },
                colors: ['#00188f', '#fff100', '#00bcf2', '#ff8c00', '#00b294', '#e81123', '#009e49', '#ec008c', '#bad80a', '#68217a'],
            },
            trendSeries: [{
                name: 'trendiness',
                data: []
            }],
            botscoreChartOptions: 
            {
                chart: 
                {
                    id: 'botscoreChart',
                    group: 'botslayer'
                },
                height: 400,
                title: 
                {
                    text: "Botness"
                },
                xaxis: 
                {
                    type: 'datetime',
                    labels: 
                    {
                        minHeight: 50
                    }
                },
                yaxis:
                {
                    max: 5,
                    min: 0,
                    labels:
                    {
                        minWidth: 75
                    }
                },
                tooltip: 
                {
                    x: { format: 'MMM. dd - HH:mm' }
                },
                toolbar: 
                {
                    show: true,
                    tools: 
                    {
                        download: true,
                        selection: true,
                        zoom: true,
                        zoomin: true,
                        zoomout: true,
                        pan: true,
                        reset: true | '<img src="/static/icons/reset.png" width="20">',
                        customIcons: []
                    },
                    autoSelected: 'zoom' 
                },
                colors: ['#00188f', '#fff100', '#00bcf2', '#ff8c00', '#00b294', '#e81123', '#009e49', '#ec008c', '#bad80a', '#68217a'],
            },
            botscoreSeries: [{
                name: 'average botness',
                data: []
            }],
            timelineData: "",
            selectedEntities: [],
            selectedEntityNames: [],
            anythingChecked: false,
            tableVisibleRows: [],
            sendToHoaxyTimeout: false,
            apiTimeout: false
        }
    },
    methods:
    {
        localVersionCheck()
        {
            var versionPromise = this.axios.get(Config.api_host + '/localVersion',
            {
                responseType: "text",
            });
            versionPromise.then
            (
                (response) =>
                {
                    this.localVersion = response.data;
                },
                (error) =>
                {
                    if(error.response && error.response.data[0] && error.response.data[0].timeout)
                    {
                        vm.apiTimeout = true;
                    }
                    console.warn("Couldn't check for local version.");
                }
            )
            return versionPromise;
        },
        latestVersionCheck()
        {
            var versionPromise = this.axios.get('https://osome.iuni.iu.edu/tools/botslayer/version.json',
            {
                reponseType: "json",
                headers: ""
            });
            versionPromise.then
            (
                (response) =>
                {
                    this.latestVersion = response.data.version;
                    this.messages = response.data.messages;
                },
                (error) =>
                {
                    console.warn("Couldn't check for latest version.");
                }
            )
            return versionPromise;
        },
        outOfDateCheck()
        {
            let versionPromises = [];
            
            versionPromises.push(this.localVersionCheck());
            versionPromises.push(this.latestVersionCheck());

            let allPromises = Promise.all(versionPromises);
            
            allPromises.then
            (
                (response) =>
                {
                    var localMajor = parseInt(this.localVersion.substring(0,1));
                    var localMinor = parseInt(this.localVersion.substring(2,3));
                    var localIncremental = parseInt(this.localVersion.substring(4,5));

                    var latestMajor = parseInt(this.latestVersion.substring(0,1));
                    var latestMinor = parseInt(this.latestVersion.substring(2,3));
                    var latestIncremental = parseInt(this.latestVersion.substring(4,5));

                    if(latestMajor > localMajor)
                    {
                        this.outOfDate = true;
                    }
                    if(latestMajor == localMajor && latestMinor > localMinor)
                    {
                        this.outOfDate = true;
                    }
                    if(latestMajor == localMajor && latestMinor == localMinor && latestIncremental > localIncremental)
                    {
                        this.outOfDate = true;
                    }
                },
                (error) =>
                {
                    console.warn("Couldn't check if BotSlayer-CE was out of date.");
                }
            )
        },
        downloadCSV: function()
        {
            // Construct download file name
            var rightNow = new Date();
            var rightNowStr = rightNow.getFullYear() + "y." + (rightNow.getMonth()+1) + "m." + rightNow.getDate() + "d_";
            rightNowStr += rightNow.getHours() + "h." + rightNow.getMinutes() + "m." + rightNow.getSeconds() + "s_";
            rightNowStr += rightNow.toTimeString().substr(9);

            var downloadStr = "botslayer_" + rightNowStr + ".csv";

            // Converting JSON to CSV with Papa Parse
            var json = this.scoreDemoArr;
            var csv = unparse(json);

            // Preparing csv file for download
            csv = "data:text/csv;charset=iso-639," + csv;
            csv = encodeURI(csv);
            csv = csv.replace(/#/g, '%23');
            var CSVLink = document.createElement("a");
            CSVLink.setAttribute("href", csv);
            CSVLink.setAttribute("download", downloadStr);
            document.body.appendChild(CSVLink);
            
            // File will be downloaded now
            CSVLink.click();
        },
        // Commenting out until middleware is ready, maybe in beta version.
        // pauseCollection(collecting)
        // {
        //     if(collecting)
        //     {
        //         var collectionPromise = this.axios.get(Config.api_host + '/pauseCollection',
        //         {
        //             responseType: "json",
        //         });
        //         collectionPromise.then
        //         (
        //             (response) =>
        //             {
        //                 console.log("Paused data collection.");
        //                 clearTimeout(this.refreshTimeout);
        //                 this.collecting = false;
        //             },
        //             (error) =>
        //             {
        //                 console.warn("Couldn't pause collection.");
        //                 this.collecting = true;
        //             }
        //         )
        //     }
        //     else
        //     {
        //         this.autoRefresh();
        //         this.collecting = true;
        //     }
        // },
        autoRefresh()
        {
            let demoPromise = this.demoScore();
            demoPromise.then
            (
                (response) =>
                {   
                    clearTimeout(this.refreshTimeout);
                    // Arrow functions retain scope, no need for 'this.' or 'vm.'
                    this.refreshTimeout = setTimeout( ()=>{
                        this.autoRefresh();
                    }, this.refreshTimeoutDuration);
                },
                (error) =>
                {
                    if(error.response && error.response.data[0] && error.response.data[0].timeout)
                    {
                        vm.apiTimeout = true;
                    }
                    clearTimeout(this.refreshTimeout);
                    // Add card or something for user info
                    console.warn("Couldn't refresh data.");
                }
            )
        },
        checkDisk()
        {
            var diskPromise = this.axios.get(Config.api_host + '/diskSpace',
            {
                responseType: "text",
            });
            diskPromise.then
            (
                (response) =>
                {
                    this.diskRemaining = parseFloat(response.data).toFixed(2);
                },
                (error) =>
                {
                    if(error.response && error.response.data[0] && error.response.data[0].timeout)
                    {
                        vm.apiTimeout = true;
                    }
                    console.warn("Couldn't check disk space.");
                }
            )
        },
        dateParser(dateFromDB)
        {
            // Exists entirely to create a Unix epoch that will be hidden
            // This creates proper datetime sorting while maintaining the human-readable version
            var date = new Date(dateFromDB);
            var timestamp = date.getTime();

            return timestamp;
        },
        shortSeed(seed)
        {
            var shortSeedArr = seed.split(',');
            var shortSeedStr = ""
            
            if(shortSeedArr.length == 1)
            {
                shortSeedStr = shortSeedStr + shortSeedArr[0];
            }
            else if(shortSeedArr.length == 2)
            {
                shortSeedStr = shortSeedStr + shortSeedArr[0] + "," + shortSeedArr[1];
            }
            else
            {
                shortSeedStr = shortSeedStr + shortSeedArr[0] + "," + shortSeedArr[1] + "," + shortSeedArr[2];
            }

            return shortSeedStr;
        },
        parseStringURL(urlString)
        {
            if(urlString.includes("twitter.com/"))
            {
                urlString = urlString.replace("http\:\/\/", "");
                urlString = urlString.replace("https\:\/\/", "");
                urlString = urlString.replace("www.", "");
                urlString = urlString.replace("twitter.com/", "@");
                urlString = urlString.replace(/\/status\/(\d+)/, "'s status");
                urlString = urlString.replace(/\/video\/(\d+)/, " video");
                urlString = urlString.replace(/\/photo\/(\d+)/, " photo");
                urlString = urlString.replace("status video", "video status");
                urlString = urlString.replace("status photo", "photo status");
                urlString = urlString.replace(/\?s=(\d+)/, "");
                urlString = urlString.replace("@i/web's status", "user status")
                if(urlString.substr(urlString.length - 1) == "/")
                {
                    urlString = urlString.substr(0, urlString.length - 1);
                }
            }
            else if (urlString.length > 40)
            {
                urlString = urlString.replace("http\:\/\/", "");
                urlString = urlString.replace("https\:\/\/", "");
                urlString = urlString.replace("www.", "");
                urlString = urlString.substring(0,20) + "..." + urlString.substring((urlString.length - 20), (urlString.length))
                if(urlString.substr(urlString.length - 1) == "/")
                {
                    urlString = urlString.substr(0, urlString.length - 1);
                }
            }
            else
            {
                urlString = urlString.replace("http\:\/\/", "");
                urlString = urlString.replace("https\:\/\/", "");
                urlString = urlString.replace("www.", "");
                if(urlString.substr(urlString.length - 1) == "/")
                {
                    urlString = urlString.substr(0, urlString.length - 1);
                }
            }

            return urlString;
        },
        parseTwitterURL(twitterURL)
        {
            if(twitterURL.includes("/video") || twitterURL.includes("/photo"))
            {
                twitterURL = twitterURL.replace(/\/video\/(\d+)/, "");
                twitterURL = twitterURL.replace(/\/photo\/(\d+)/, "");
                
                return twitterURL;
            }
            return twitterURL;
        },
        demoScore: function()
        {
            let vm = this;

            vm.backInTime = false;

            vm.tableBusy = true;

            var query_string = "exclusion=" + this.exclusion;

            this.checkDisk();
            
            var scoreDemoPromise = this.axios.get(Config.api_host + '/scoreDemo?' + query_string,
            {
                responseType: "json",
            });
            scoreDemoPromise.then
            (
                function(response)
                {
                    vm.nowCheck();

                    vm.scoreDemoArr = response.data;

                    // If there is data, plan on showing the table
                    if(vm.scoreDemoArr.length >= 1)
                    {
                        vm.tablePresent = true;
                    }

                    // Check for divideByZero/insufficientData error (low amount of data)
                    if(typeof response.data[0] != "undefined")
                    {
                        if(response.data[0].insufficient_data == true)
                        {
                            vm.insufficientData = true;
                            vm.emptyArray = false;
                            // Stop showing the table if the only response is {"insufficient_data": true}
                            vm.tablePresent = false;
                        }
                        else
                        {
                            vm.insufficientData = false;
                        }
                    }

                    // This means not even 1 tweet has been found
                    // So not even the divideByZero/insufficientData error could occur
                    if(vm.scoreDemoArr.length == 0)
                    {
                        vm.emptyArray = true;
                        vm.insufficientData = false;
                    }

                    vm.serverError = false;
                    
                    vm.tableBusy = false;
                    vm.collecting = true;

                    vm.totalData = vm.scoreDemoArr.length;
                },
                function(error)
                {
                    console.warn("No JSON retrieved.");
                    if(error.response && error.response.data[0] && error.response.data[0].timeout)
                    {
                        vm.apiTimeout = true;
                    }
                    vm.insufficientData = false;
                    vm.emptyArray = false;
                    vm.serverError = true;
                    vm.tableBusy = false;
                }
            )
            return scoreDemoPromise;
        },
        onFiltered(filteredItems) 
        {
            // Trigger pagination to update the number of buttons/pages due to filtering
            this.totalData = filteredItems.length;
            this.currentPage = 1;
        },
        clearFilter: function()
        {
            this.filter = '';
            // totalData is changed during filtering for pagination; reverting to intial query limit
            this.totalData = this.originalTotalData;
        },
        excludeQuery: function()
        {
            //TODO: Method for hitting exclusion button
            //Set exclusion to prop known as configINI
            this.excludeCheck = !this.excludeCheck;
            if(this.excludeCheck)
            {
                this.exclusion = encodeURIComponent(this.configINI.seed.toString());
            }
            else
            {
                this.exclusion = ' ';
            }
        },
        nowCheck: function()
        {
            // Format as ISO string: 2019-07-19T19:42:00.000Z
            var date = new Date();
            this.whenBS = date.toISOString();

            this.timeZoneAbbreviation = new Date().toLocaleTimeString('en-us',{timeZoneName:'short'}).split(' ')[2];

            var offsetGMTInt = new Date().getTimezoneOffset() / 60;
            offsetGMTInt *= -1;

            var offsetGMTString = "GMT";
            
            if(offsetGMTInt < 0)
            {
                offsetGMTString += offsetGMTInt;
            }
            else
            {
                offsetGMTString = offsetGMTString + "+" + offsetGMTInt;
            }

            if(offsetGMTString.includes("."))
            {
                offsetGMTString.replace(".75", ":45");
                offsetGMTString.replace(".5", ":30");
                offsetGMTString.replace(".25", ":15");
            }
            else
            {
                offsetGMTString += ":00";
            }
            
            this.offsetGMT = offsetGMTString;
        },
        timeWarp(bsTime)
        {
            clearTimeout(this.refreshTimeout);
            this.backInTime = true;

            // Formatting for use in middleware. bsTime is an ISO string by default
            var formattedTime = bsTime.substring(0,10) + " " + bsTime.substring(11,19);

            let vm = this;

            vm.tableBusy = true;

            var query_string = "exclusion=" + this.exclusion + "&time=" + formattedTime;

            var scoreDemoPromise = this.axios.get(Config.api_host + '/scoreDemo?' + query_string,
            {
                responseType: "json",
            });
            scoreDemoPromise.then
            (
                function(response)
                {
                    vm.scoreDemoArr = response.data;

                    // If there is data, plan on showing the table
                    if(vm.scoreDemoArr.length >= 1)
                    {
                        vm.tablePresent = true;
                    }

                    // Check for divideByZero/insufficientData error (low amount of data)
                    if(typeof response.data[0] != "undefined")
                    {
                        if(response.data[0].insufficient_data == true)
                        {
                            vm.insufficientData = true;
                            vm.emptyArray = false;
                            // Stop showing the table if the only response is {"insufficient_data": true}
                            vm.tablePresent = false;
                        }
                        else
                        {
                            vm.insufficientData = false;
                        }
                    }

                    // This means not even 1 tweet has been found
                    // So not even the divideByZero/insufficientData error could occur
                    if(vm.scoreDemoArr.length == 0)
                    {
                        vm.emptyArray = true;
                        vm.insufficientData = false;
                    }

                    vm.serverError = false;
                    
                    vm.tableBusy = false;
                    vm.collecting = true;

                    vm.totalData = vm.scoreDemoArr.length;
                },
                function(error)
                {
                    console.warn("No JSON retrieved.");
                    if(error.response && error.response.data[0] && error.response.data[0].timeout)
                    {
                        vm.apiTimeout = true;
                    }
                    vm.insufficientData = false;
                    vm.emptyArray = false;
                    vm.serverError = true;
                    vm.tableBusy = false;
                }
            )
            return scoreDemoPromise;
        },
        hoaxyLive: function()
        {
          this.tableBusy = true;
          this.selectedEntityNames = [];
          for(var i = 0; i < this.selectedEntities.length; i++)
          {
              this.selectedEntityNames.push(this.selectedEntities[i].Entity);
          }
          var entitiesString = ""
          entitiesString = this.selectedEntityNames.join(" OR ");

          this.tableBusy = false;

          var hoaxyTab = window.open("https://hoaxy.iuni.iu.edu/#query=" + entitiesString + "&sort=mixed&type=Twitter", "_blank");
          hoaxyTab.focus();
        },
        sendToHoaxy(entityIDs, bsTime, entity, singleMode)
        {
            this.noHoaxyData = false;
            
            let vm = this;

            vm.tableBusy = true;

            var selectedEntityIDs = [];

            if(!singleMode)
            {
                for (var i = 0; i < this.selectedEntities.length; i++)
                {
                  selectedEntityIDs[i] = this.selectedEntities[i].EntityID;
                }
            }

            if(entityIDs)
            {
                selectedEntityIDs[0] = entityIDs;
            }

            var formattedTime = bsTime.substring(0,10) + " " + bsTime.substring(11,19);

            var query_string = "entityIDs=" + selectedEntityIDs + "&time=" + formattedTime + "&entity=" + encodeURIComponent(entity);
            
            var sendToHoaxyPromise = this.axios.get(Config.api_host + '/sendToHoaxy?' + query_string,
            {
                responseType: "json",
            });
            sendToHoaxyPromise.then
            (
                function(response)
                {
                    if(response.data[0].no_data && (response.data[0].no_data == true))
                    {
                        vm.noHoaxyData = true;
                    }
                    else
                    {
                        vm.noHoaxyData = false;
                        vm.hoaxySubmitData = JSON.stringify(response.data);

                        // sleep time expects milliseconds
                        function sleep (time) 
                        {
                            return new Promise((resolve) => setTimeout(resolve, time));
                        }

                        sleep(50).then(() => {
                            vm.simulateFormSubmit();
                        });

                        vm.tableBusy = false;
                    }
                },
                function(error)
                {
                    console.warn("Couldn't receive data to send to Hoaxy.")
                    if(error.response && error.response.data[0] && error.response.data[0].error)
                    {
                        if(error.response.data[0].error.includes("timed out"))
                        {
                            vm.sendToHoaxyTimeout = true;
                        }
                    }
                    vm.tableBusy = false;
                }
            )
            return sendToHoaxyPromise;
        },
        simulateFormSubmit: function()
        {
            var simulateClick = function (elem) {
                // Create our event (with options)
                var evt = new MouseEvent('click', {
                    bubbles: true,
                    cancelable: true,
                    view: window
                });
                // If cancelled, don't dispatch our event
                var canceled = !elem.dispatchEvent(evt);
            };

            var hoaxySubmit = document.getElementById('hoaxySubmitForm');
            simulateClick(hoaxySubmit);
        },
        getTimelines(entityID, entity, bsTime, singleMode)
        {
            let vm = this;

            vm.chartsBusy = true;

            vm.accountSeries = [];
            vm.tweetSeries = [];
            vm.trendSeries = [];
            vm.botscoreSeries = [];

            var selectedEntityIDs = [];
            vm.selectedEntityNames = [];

            if(!singleMode)
            {
                for (var i = 0; i < this.selectedEntities.length; i++)
                {
                    selectedEntityIDs[i] = this.selectedEntities[i].EntityID;
                    vm.selectedEntityNames.push(this.selectedEntities[i].Entity);
                }
            }

            if(entityID)
            {
                selectedEntityIDs[0] = entityID;
                vm.selectedEntityNames.push(entity);
            }

            var formattedTime = bsTime.substring(0,10) + " " + bsTime.substring(11,19);

            var query_string = "entityIDs=" + selectedEntityIDs + "&time=" + formattedTime;

            var timelinePromise = this.axios.get(Config.api_host + '/timeline?' + query_string,
            {
                responseType: "json",
            });
            timelinePromise.then
            (
                function(response)
                {
                    for (var series = 0; series < selectedEntityIDs.length; series++)
                    {
                        vm.accountSeries[series] = {name: vm.selectedEntityNames[series],data: []}
                        vm.tweetSeries[series] = {name: vm.selectedEntityNames[series],data: []}
                        vm.trendSeries[series] = {name: vm.selectedEntityNames[series],data: []}
                        vm.botscoreSeries[series] = {name: vm.selectedEntityNames[series],data: []}
                        var hour = "";
                        for (hour in response.data)
                        {
                            if(response && response.data && response.data[hour] && response.data[hour][series])
                            {
                                var xyData = [];
                                xyData.push(hour);
                                xyData.push(parseInt(response.data[hour][series].acc_cnt));
                                vm.accountSeries[series].data.push(xyData);
                            }
                            else
                            {
                                vm.accountSeries[series].data.push([hour, 0]);
                            }

                            if(response && response.data && response.data[hour] && response.data[hour][series])
                            {
                                var xyData = [];
                                xyData.push(hour);
                                xyData.push(parseInt(response.data[hour][series].twt_cnt));
                                vm.tweetSeries[series].data.push(xyData);
                            }
                            else
                            {
                                vm.tweetSeries[series].data.push([hour, 0]);
                            }

                            if(response && response.data && response.data[hour] && response.data[hour][series])
                            {
                                var xyData = [];
                                xyData.push(hour);
                                xyData.push(parseInt(100 * response.data[hour][series].trend));
                                vm.trendSeries[series].data.push(xyData);
                            }
                            else
                            {
                                vm.trendSeries[series].data.push([hour, 0]);
                            }

                            if(response && response.data && response.data[hour] && response.data[hour][series])
                            {
                                var xyData = [];
                                xyData.push(hour);
                                xyData.push((5 * response.data[hour][series].mean_bs).toFixed(1));
                                vm.botscoreSeries[series].data.push(xyData);
                            }
                            else
                            {
                                vm.botscoreSeries[series].data.push([hour, 0]);
                            }
                        }
                    }

                    console.log(vm.accountSeries)

                    vm.chartComponentKey += 1; // Update Vue render

                    vm.chartsBusy = false;
                },
                function(error)
                {
                    console.warn("No JSON retrieved.");
                    if(error.response && error.response.data[0] && error.response.data[0].timeout)
                    {
                        vm.apiTimeout = true;
                    }
                    vm.chartsBusy = false;
                }
            )
            return timelinePromise;
        },
        hideDiskMessage: function()
        {
            this.showDiskMessage = false;
        },
        check(item)
        {
            this.selectedEntities.push(item);
            this.anythingChecked = true;
        },
        uncheck(item)
        {
            var index = this.selectedEntities.indexOf(item);
            if(index > -1)
            {
                this.selectedEntities.splice(index, 1);
            }
            if(this.selectedEntities.length == 0)
            {
                this.anythingChecked = false;
            }
        },
        uncheckAll: function()
        {
            this.selectedEntities = [];
            this.anythingChecked = false;
        },
        checkAll: function()
        {
            this.$set(this, "selectedEntities", this.tableVisibleRows);
            this.anythingChecked = true;
        },
        closeCE: function()
        {
            this.closedCE = true;
        }
    },
    computed: 
    {
        filteredScoreDemoArr: function()
        {
            let vm = this;
            return this.scoreDemoArr.filter(function(item)
            {
                if(vm.scoreDemoFilter.length > 0)
                {
                    if(vm.scoreDemoFilter.indexOf(item.Type) > -1)
                    {
                        return item;
                    }
                    else
                    {
                        return false;
                    }
                }
                else
                {
                    return item;
                }
            });
        },
        tweetEntityNames: function()
        {
            let tmp = [];
            for(var i = 0; i < this.selectedEntities.length; i++)
            {
                let ent = this.selectedEntities[i].Entity;
                tmp.push(ent);
            }
            return tmp.join(", ");
        },
        tweetHoaxyEntityNames: function()
        {
            let tmp = [];
            for(var i = 0; i < this.selectedEntities.length; i++)
            {
                let ent = this.selectedEntities[i].Entity;
                tmp.push(ent);
            }
            this.$nextTick(function(){
              twttr.widgets.load();
            })
            return tmp.join(" OR ");
        }
    },
    props:
    {
        configINI: Object
    },
    created: function()
    {
        this.autoRefresh();
    },
    mounted: function()
    {
        this.nowCheck();
        this.outOfDateCheck();
        setTimeout( ()=>{
            this.hideDiskMessage();
        }, 10000);
        twttr.widgets.load();
    }
}
</script>

<style>
    a
    {
        color: #14AA40;
    }
    a:hover
    {
        color: #14CC40;
    }
    .btn-outline-primary
    {
        background-color: white;
        margin: 10px;
    }
    .btn-primary
    {
        background-color: #14AA40;
        border-color: #14AA00;
    }
    .btn-primary:hover
    {
        background-color: #14CC40;
        border-color: #14CC00;
    }
    .page-link
    {
        color: #14AA40;
        border-color: #14AA00;
    }
    .page-item.active .page-link
    {
        background-color: #14AA40;
        border-color: #14AA00;
    }
    .page-link:hover
    {
        color: #14AA40;
        border-color: #14AA00;
    }
    .margin-10-px
    {
        margin: 10px;
    }
    .input-group .input-group-text 
    {
        width: 100%;
    }
    .table-orange:hover
    {
        background-color: #ffd7a6;
    }
    .table-orange
    {
        background-color: #ffdfc1;
    }
    .progress
    {
        background-color: rgb(58, 58, 58);
        -webkit-box-shadow: none;
        box-shadow: none;
    }
    .progress-bar
    {
        background-color: rgb(0, 205, 212);
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
    .table-hover tbody tr:hover
    {
        background-color: rgba(0,128,0,0.20);
    }
    ::selection
    {
        background: rgb(128, 255, 128);
    }
    .apexcharts-title-text 
    {
        font-weight: 600;
    }
    .four-chan path
    {
        fill: #14aa40;
    }
    .four-chan:hover path
    {
        fill: #14cc40;
    }
    .four-chan
    {
        width: 16px;
        height: 16px;
        cursor: pointer;
    }
    .multi-select
    {
        margin-top: 0px;
        margin-bottom: 0px;
        margin-left: 5px;
        margin-right: 5px;
    }
</style>
