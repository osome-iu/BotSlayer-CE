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
        <b-card v-if="(diskRemaining < 20)" style="background-color: orange">
            <b-card-text style="color: white">
                <strong>Warning: {{this.diskRemaining}}% disk space remaining!</strong>
                <br>You can add disk space to your server to alleviate the issue.
                <br>Otherwise, old data will be automatically deleted when less than <strong>10%</strong> free disk space remains.
            </b-card-text>
        </b-card>
        <b-form-group class="margin-10-px">
            <div style="margin-bottom: 10px">
            <span style="font-size: 125%; margin-right: 10px;">
                <span style="color: #00bb00;"><strong>Query: </strong></span>
                <span v-b-tooltip :title="this.configINI.seed.toString()" v-if="this.configINI.seed.toString().split(',').length > 3" style="border-bottom: 1px dotted" id="span-if">{{shortSeed(this.configINI.seed.toString())}}...</span>
                <span v-b-tooltip :title="this.configINI.seed.toString()" v-else style="border-bottom: 1px dotted" id="span-else">{{this.configINI.seed.toString()}}</span>

                <b-button v-b-tooltip :title="'Shows the results without the query: ' + this.configINI.seed.toString()" style="margin-right: 5px; margin-left: 5px" variant="success" @click="excludeQuery(); demoScore();"><span v-if="this.excludeCheck">Include</span><span v-else>Exclude</span></b-button>
                <b-button v-b-tooltip title="Refreshes the table with the latest data." variant="success" @click="clearFilter(); demoScore();"><strong>&#8635;</strong> Refresh</b-button>     
                <b-button v-b-tooltip title="Downloads a .csv file containing the data in the table below." style="margin-left: 5px" variant="success" @click="downloadCSV();">Export</b-button>

            </span>
            </div>
            
            <div class="d-flex justify-content-center">
                <span style="font-size: 125%; margin-right: 10px; color: #00bb00;"><strong>Show Only:</strong></span>
                <b-input-group class="col-3" size="sm">
                    <b-form-input v-model="filter" placeholder="Filter results" style=""></b-form-input>
                </b-input-group>
                <b-form-checkbox-group id="checkbox-group" v-model="scoreDemoFilter" name="demoFilters" switches>
                    <b-form-checkbox @input="onFiltered(filteredScoreDemoArr)" v-model="scoreDemoFilter" value="hashtags">Hashtags</b-form-checkbox>
                    <b-form-checkbox @input="onFiltered(filteredScoreDemoArr)" v-model="scoreDemoFilter" value="user_mentions">User Mentions</b-form-checkbox>
                    <b-form-checkbox @input="onFiltered(filteredScoreDemoArr)" v-model="scoreDemoFilter" value="media">Pics/Vids</b-form-checkbox>
                    <b-form-checkbox @input="onFiltered(filteredScoreDemoArr)" v-model="scoreDemoFilter" value="urls">Links</b-form-checkbox>
                </b-form-checkbox-group>
            </div>
        </b-form-group>

        <b-spinner style="width: 5rem; height: 5rem;" v-if="tableBusy" variant="success"></b-spinner>

        <b-pagination variant="success" class="margin-10-px" v-if="tablePresent" align="center" v-model="pageNum" :total-rows="totalData" :per-page="perPage"></b-pagination>

        <div v-if="(!tablePresent && !tableBusy)">
            <b-card class="margin-10-px" v-if="this.serverError" bg-variant="danger" text-variant="white">
                <b-card-text>
                    BotSlayer-CE has encountered a technical error.
                </b-card-text>
            </b-card>
            <b-card class="margin-10-px" v-else-if="this.insufficientData" style="background-color: #00bb00;" text-variant="white">
                <b-card-text>
                    BotSlayer-CE has collected a very small amount of data for this query.
                    <br>If you've been waiting a while, feel free to try changing the query seed.
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

        <b-table v-if="tablePresent" @filtered="onFiltered" stacked="lg" striped hover bordered outlined :filter="filter" :items="filteredScoreDemoArr" :fields="scoreDemoFields" :busy="tableBusy" :per-page="perPage" :current-page="pageNum" :sort-by.sync="sortBy" :sort-desc.sync="sortDesc">
            <!-- Programmatic header adjustment -->
            <template slot="HEAD_BS_Level" slot-scope="data">
                <span v-b-tooltip.bottom :title="data.field.headerTitle">{{ data.label }}</span>
            </template>
            <template slot="HEAD_Tweets" slot-scope="data">
                <span v-b-tooltip.bottom :title="data.field.headerTitle">{{ data.label }}</span>
            </template>
            <template slot="HEAD_Accounts" slot-scope="data">
                <span v-b-tooltip.bottom :title="data.field.headerTitle">{{ data.label }}</span>
            </template>
            <template slot="HEAD_Trendiness" slot-scope="data">
                <span v-b-tooltip.bottom :title="data.field.headerTitle">{{ data.label }}</span>
            </template>
            <template slot="HEAD_Botness" slot-scope="data">
                <span v-b-tooltip.bottom :title="data.field.headerTitle">{{ data.label }}</span>
            </template>
            
            <!-- Virtual composite columns -->
            <template slot="Research" slot-scope="data">
                <a target="_blank" v-b-tooltip :title="'Visualize with Hoaxy'" :href="'https://hoaxy.iuni.iu.edu/#query=' + data.item.Entity + '&sort=mixed&type=Twitter'"><font-awesome-icon icon="retweet"></font-awesome-icon></a> 
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
            </template>
            <template slot="Entity" slot-scope="data">
                <a target="_blank" v-if="(data.item.Type == 'media') || (data.item.Type == 'urls')" :href="'' + data.item.Entity">{{ parseStringURL(data.item.Entity.toString()) }}</a>
                <a target="_blank" v-if="(data.item.Type == 'user_mentions')" :href="'https://twitter.com/' + data.item.Entity.toString().substring(1)">{{ data.item.Entity }}</a>
                <a target="_blank" v-if="(data.item.Type == 'hashtags')" :href="'https://twitter.com/hashtag/' + data.item.Entity.toString().substring(1)">{{ data.item.Entity }}</a>
            </template>
            <template slot="Last_Seen" slot-scope="data">
                <span hidden>{{dateParser(data.item['Last_Seen'])}}</span>
                <timeago v-b-tooltip :title="data.item['Last_Seen']" style="border-bottom: 1px dotted" id="lastSeen" :datetime="data.item['Last_Seen']" :auto-update="60"></timeago>
            </template>
            <template slot="Trendiness" slot-scope="data">
                <span>{{data.item.Trendiness}}%</span>
            </template>
            <template slot="Botness" slot-scope="data">
                <span style="color: red"><strong>{{data.item.Botness}} / 5</strong></span>
            </template>
            <template slot="BS_Level" slot-scope="data">
                <b-progress :value="parseFloat(data.item.BS_Level)" :max="1"></b-progress>
            </template>
        </b-table>
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
                {key: 'Entity', label: 'Entity', sortable: true, class: 'text-left'},
                {key: 'Research', label: 'Research', sortable: false},
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
            perPage: 20,
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
            messages: [""],
            closedCE: false
        }
    },
    methods:
    {
        // Click Export to download CSV file
        downloadCSV: function()
        {
            // Construct download file name
            var rightNow = new Date();
            var rightNowStr = rightNow.getFullYear() + "y." + (rightNow.getMonth()+1) + "m." + rightNow.getDate() + "d_";
            rightNowStr += rightNow.getHours() + "h." + rightNow.getMinutes() + "m." + rightNow.getSeconds() + "s_";
            rightNowStr += rightNow.toTimeString().substr(9);

            var downloadStr = "botslayer-ce_" + rightNowStr + ".csv";

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
        // BotSlayer-CE auto-refreshes by default every 5 minutes to stay up-to-date.
        autoRefresh()
        {
            this.checkDisk();
            let demoPromise = this.demoScore();
            demoPromise.then
            (
                (response) =>
                {
                    clearTimeout(this.refreshTimeout);
                    this.refreshTimeout = setTimeout( ()=>{
                        this.autoRefresh();
                    }, this.refreshTimeoutDuration);
                },
                (error) =>
                {
                    clearTimeout(this.refreshTimeout);
                    console.warn("Couldn't refresh data.");
                }
            )
        },
        // BotSlayer-CE is best run within a docker container on an AWS EC2 instance
        // Regardless, BotSlayer-CE will alert you if your disk space is running low (20%)
        // It will also auto-delete the oldest data if the disk falls below 10% space
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
                    console.warn("Couldn't check disk space.");
                }
            )
        },
        // Exists entirely to create a Unix epoch that will be hidden
        // This creates proper datetime sorting while maintaining the human-readable version
        dateParser(dateFromDB)
        {
            var date = new Date(dateFromDB);
            var timestamp = date.getTime();

            return timestamp;
        },
        // Creates the "Query: #one, #two, #three..." section under the navbar.
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
        // Keeps the table columns relatively uniform
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
        // Twitter search will fail if you use the full URL with "/video/#"
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
        // The main function that populates the table with data
        demoScore: function()
        {
            // Captured the scope of "this"
            let vm = this;

            // Used for spinner and messages
            this.tableBusy = true;

            // Can include variables for different pagination styles, etc.
            // Mainly just says whether to exclude the original query from the table results
            var query_string = "exclusion=" + this.exclusion;

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
            // Exclude-Include switching
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
        closeCE: function()
        {
            this.closedCE = true;
        }
    },
    computed: 
    {
        // "Show Only: Hashtags, User Mentions, Pics/Vids, Links"
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
        }
    },
    props:
    {
        configINI: Object
    },
    created: function()
    {
        this.autoRefresh();
    }
}
</script>

<style>
    .btn-outline-success
    {
        background-color: white;
        margin: 10px;
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
    .btn-primary
    {
        background-color: #18c729;
        border-color: #18c729;
    }
    .btn-primary:hover
    {
        background-color: #16b826;
        border-color: #16b826;
    }
    .page-item.active
    .page-link 
    {
        z-index: 1;
        color: white;
        background-color: #16b826;
        border-color: #16b826;
    }
    .page-link
    {
        color: #16b826;
    }
    a:hover
    {
        color: #169826;
    }
    a
    {
        color: #16b826;
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
        background-color: rgba(0,75,0,0.20);
    }
    .card-body
    {
        padding: 0.25rem;
    }
    ::selection
    {
        background: rgb(128, 255, 128);
    }
</style>
