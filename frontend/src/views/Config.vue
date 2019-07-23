<template>
    <div class="config">
        <b-card v-if="errorMessage" bg-variant="danger">
            <b-card-text style="color: white">{{errorMessage}}</b-card-text>
        </b-card>
        <b-card v-if="saved" bg-variant="success">
            <b-card-text style="color: white">Config successfully saved!</b-card-text>
        </b-card>
        <b-card v-if="successfulChange" bg-variant="success">
            <b-card-text style="color: white">Successfully changed password!</b-card-text>
        </b-card>
        <b-card v-if="!passwordsMatch" bg-variant="danger">
            <b-card-text style="color: white">Passwords do not match.</b-card-text>
        </b-card>
        <div v-if="correctPass && !changingPassword">
        <h3 class="margin-10-px" style="color: #00bb00">Enter comma-separated values like words, hashtags, users, etc. below and press "SAVE" to track them:</h3>
        <div>
            <b-form-group id="configINIForm" class="margin-10-px">
                <div class="input-group" style="margin: 4px">
                    <div class="input-group-prepend">
                        <span class="input-group-text"><b-button style="padding: 0" v-b-tooltip title="Enter the things you wish to search for, such as: 'puppies kittens, #puppiesrule, example.com/article'. Further information can be found on the Help page."><font-awesome-icon :icon="['fas', 'question-circle']" /></b-button>&nbsp;Query:</span>
                    </div>
                    <b-form-input v-model="configINIFields.seed" placeholder="Ex: puppies kittens, #puppiesrule, example.com/article"></b-form-input>
                </div>
                
                <div class="input-group" style="margin: 4px">
                    <div class="input-group-prepend">
                        <span class="input-group-text"><b-button style="padding: 0" v-b-tooltip title="This is 1 of 4 twitter keys gained when creating a twitter app. For more info, refer to the Help page."><font-awesome-icon :icon="['fas', 'question-circle']" /></b-button>&nbsp;Consumer Key:</span>
                    </div>
                    <b-form-input v-model="configINIFields.consumerKey"></b-form-input>
                </div>

                <div class="input-group" style="margin: 4px">
                    <div class="input-group-prepend">
                        <span class="input-group-text"><b-button style="padding: 0" v-b-tooltip title="This is 1 of 4 twitter keys gained when creating a twitter app. For more info, refer to the Help page."><font-awesome-icon :icon="['fas', 'question-circle']" /></b-button>&nbsp;Consumer Secret:</span>
                    </div>
                    <b-form-input v-model="configINIFields.consumerSecret"></b-form-input>
                </div>

                <div class="input-group" style="margin: 4px">
                    <div class="input-group-prepend">
                        <span class="input-group-text"><b-button style="padding: 0" v-b-tooltip title="This is 1 of 4 twitter keys gained when creating a twitter app. For more info, refer to the Help page."><font-awesome-icon :icon="['fas', 'question-circle']" /></b-button>&nbsp;Access Token:</span>
                    </div>
                    <b-form-input v-model="configINIFields.accessToken"></b-form-input>
                </div>

                <div class="input-group" style="margin: 4px">
                    <div class="input-group-prepend">
                        <span class="input-group-text"><b-button style="padding: 0" v-b-tooltip title="This is 1 of 4 twitter keys gained when creating a twitter app. For more info, refer to the Help page."><font-awesome-icon :icon="['fas', 'question-circle']" /></b-button>&nbsp;Access Token Secret:</span>
                    </div>
                    <b-form-input v-model="configINIFields.accessTokenSecret"></b-form-input>
                </div>
            </b-form-group>
            <b-button variant="success" @click="saveConfig()">SAVE</b-button>
            <div class="margin-10-px">
                <b-spinner style="width: 5rem; height: 5rem;" v-if="saving" variant="success"></b-spinner>
            </div>
        </div>
        </div>
        
        <div v-else-if="!correctPass && !firstTime && !changingPassword" class="margin-30-px">
            <div class="input-group">
                <div class="input-group-prepend">
                    <span class="input-group-text">Password:</span>
                </div>
                <b-form-input autofocus v-if="!invalidPassword" v-model="currentPass" :type="'password'" @keyup.enter="checkPass()"></b-form-input>
                <b-form-input v-else class="is-invalid" v-model="currentPass" :type="'password'" @keyup.enter="checkPass()"></b-form-input>
            </div>
            <b-button class="margin-10-px" variant="success" @click="checkPass()">Login</b-button>
            <br>
            <b-button class="margin-10-px" style="margin-top: 0px" variant="success" @click="changingPassword = !changingPassword">Change Password</b-button>
        </div>

        <div v-else-if="firstTime" class="margin-30-px">
            <h1 style="color: #007bbb"><strong>First Time Setup</strong></h1>
            <div class="input-group">
                <div class="input-group-prepend">
                    <span class="input-group-text">New Password:</span>
                </div>
                <b-form-input autofocus v-if="passwordsMatch" v-model="newPassword" :type="'password'"></b-form-input>
                <b-form-input autofocus v-else class="is-invalid" v-model="newPassword" :type="'password'"></b-form-input>
            </div>
            <div class="input-group">
                <div class="input-group-prepend">
                    <span class="input-group-text">Confirm New Password:</span>
                </div>
                <b-form-input v-if="passwordsMatch" v-model="newPasswordConfirm" :type="'password'"></b-form-input>
                <b-form-input v-else class="is-invalid" v-model="newPasswordConfirm" :type="'password'"></b-form-input>
            </div>
            <b-button class="margin-10-px" variant="success" @click="changePasswordFirstTime()">Change Password</b-button>
        </div>

        <div v-else-if="changingPassword" class="margin-30-px">
            <h1 style="color: #007bbb"><strong>Change Your Password:</strong></h1>
            <div class="input-group">
                <div class="input-group-prepend">
                    <span class="input-group-text">Old Password:</span>
                </div>
                <b-form-input v-model="currentPass" :type="'password'"></b-form-input>
            </div>
            <div class="input-group">
                <div class="input-group-prepend">
                    <span class="input-group-text">New Password:</span>
                </div>
                <b-form-input v-if="passwordsMatch" v-model="newPassword" :type="'password'"></b-form-input>
                <b-form-input v-else class="is-invalid" v-model="newPassword" :type="'password'"></b-form-input>
            </div>
            <div class="input-group">
                <div class="input-group-prepend">
                    <span class="input-group-text">Confirm New Password:</span>
                </div>
                <b-form-input v-if="passwordsMatch" v-model="newPasswordConfirm" :type="'password'"></b-form-input>
                <b-form-input v-else class="is-invalid" v-model="newPasswordConfirm" :type="'password'"></b-form-input>
            </div>
            <b-button class="margin-10-px" variant="success" @click="changePassword()"><span v-if="!confirmChange">Change Password</span><span v-if="confirmChange">Really Change?</span></b-button>
            <br>
            <b-button class="margin-10-px" style="margin-top: 0px" variant="success" @click="changingPassword = !changingPassword">Go Back</b-button>
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
import Config from "../../config.json"
export default
{
    name: 'config',
    data: function()
    {
        return{
            configINIFields:
            {
                consumerKey: '',
                consumerSecret: '',
                accessToken: '',
                accessTokenSecret: '',
                seed: {},
                dbname: 'bev',
                user: 'bev',
                password: 'bev'
            },
        currentPass: '',
        correctPass: false,
        firstTime: false,
        oldPassword: '',
        newPassword: '',
        newPasswordConfirm: '',
        oldPasswordCorrect: false,
        changingPassword: false,
        confirmChange: false,
        invalidPassword: false,
        errorMessage: '',
        saving: false,
        saved: false,
        successfulChange: false,
        passwordsMatch: true
        }
    },
    methods:
    {
        changePasswordFirstTime: function()
        {
            let vm = this;

            if(vm.newPassword == vm.newPasswordConfirm)
            {
                vm.passwordsMatch = true;

                var changePassPromise = this.axios.get(Config.api_host + '/changePass?newPass=' + vm.newPassword,
                {
                    responseType: "text",
                });
                changePassPromise.then
                (
                    function(response)
                    {
                        console.log("Password successfully changed.");
                        vm.changingPassword = false;
                        vm.firstTime = false;
                    },
                    function(error)
                    {
                        console.warn("Couldn't change password.");
                    }
                )
            }
            else
            {
                vm.passwordsMatch = false;
            }
        },
        changePassword: function()
        {
            let vm = this;

            var checkPassPromise = this.axios.get(Config.api_host + '/checkPass?currentPass=' + vm.currentPass,
            {
                responseType: "text",
            });
            checkPassPromise.then
            (
                function(response)
                {
                    if(response.data == true)
                    {
                        vm.oldPasswordCorrect = true;
                        vm.confirmChange = true;
                    }
                    else
                    {
                        vm.oldPasswordCorrect = false;
                    }
                },
                function(error)
                {
                    console.warn("Couldn't verify password.");
                }
            )

            if(vm.oldPasswordCorrect)
            {
                console.log("Passed oldPasswordCorrect check.");
                if(vm.newPassword == vm.newPasswordConfirm)
                {
                    vm.passwordsMatch = true;
                    console.log("Passed newPass = newPassConf check.");
                    var changePassPromise = this.axios.get(Config.api_host + '/changePass?newPass=' + vm.newPassword,
                    {
                        responseType: "text",
                    });
                    changePassPromise.then
                    (
                        function(response)
                        {
                            console.log("Password successfully changed.");
                            vm.changingPassword = false;
                            vm.confirmChange = false;
                            vm.successfulChange = true;
                        },
                        function(error)
                        {
                            console.warn("Couldn't change password.");
                            vm.successfulChange = false;
                        }
                    )
                }
                else
                {
                    vm.passwordsMatch = false;
                }
            }
        },
        checkPass: function()
        {
            let vm = this;

            var checkPassPromise = this.axios.get(Config.api_host + '/checkPass?currentPass=' + vm.currentPass,
            {
                responseType: "text",
            });
            checkPassPromise.then
            (
                function(response)
                {
                    if(response.data == 'firstTime')
                    {
                        console.log('First time setup.');
                        vm.firstTime = true;
                        vm.errorMessage = ''; // Probably not necessary
                    }
                    else if(response.data == true)
                    {
                        vm.invalidPassword = false;
                        vm.correctPass = true;
                        vm.firstTime = false;
                        vm.successfulChange = false;
                        vm.errorMessage = '';
                        // Sometimes Vue loads the page before the fields get set
                        if(vm.configINIFields.seed.toString() == '[object Object]')
                        {
                            vm.$set(vm, "configINIFields", vm.configINI);
                        }
                    }
                    else
                    {
                        if(vm.currentPass != '')
                        {
                            vm.invalidPassword = true;
                            vm.successfulChange = false;
                            vm.errorMessage = 'Invalid password.';
                        }
                        else
                        {
                            vm.errorMessage = '';
                        }
                        vm.correctPass = false;
                        vm.firstTime = false;
                    }
                },
                function(error)
                {
                    console.warn("Couldn't verify password.");
                }
            )
        },
        saveConfig: function()
        {
            let vm = this;

            vm.saving = true;
            vm.saved = false;

            var seedAsStr = this.configINIFields.seed.toString();
            seedAsStr = seedAsStr.replace(/\s*,\s*/g, ",");
            seedAsStr = seedAsStr.replace("http://", "");
            seedAsStr = seedAsStr.replace("https://", "");
            if(seedAsStr.substr(0,4) == "www.")
            {
                seedAsStr = seedAsStr.substr(4,seedAsStr.length - 1);
            }
            if(seedAsStr.substr(seedAsStr.length - 1) == "/")
            {
                seedAsStr = seedAsStr.substr(0, seedAsStr.length - 1);
            }
            seedAsStr = encodeURIComponent(seedAsStr);

            // Strip https, http, ://, www., etc.
            var consumerKeyStr = "consumerKey=" + (this.configINIFields.consumerKey);
            var consumerSecretStr = "&consumerSecret=" + (this.configINIFields.consumerSecret);
            var accessTokenStr = "&accessToken=" + (this.configINIFields.accessToken);
            var accessTokenSecretStr = "&accessTokenSecret=" + (this.configINIFields.accessTokenSecret);
            var seedStr = "&seed=" + (seedAsStr);
            var dbnameStr = "&dbname=" + (this.configINIFields.dbname);
            var userStr = "&user=" + (this.configINIFields.user);
            var passwordStr = "&password=" + (this.configINIFields.password);
            
            var configParameters = consumerKeyStr + consumerSecretStr + accessTokenStr + accessTokenSecretStr + seedStr + dbnameStr + userStr + passwordStr;

            var saveConfigPromise = this.axios.get(Config.api_host + '/configSave?' + configParameters,
            {
                responseType: "json",
            });
            saveConfigPromise.then
            (
                function(response)
                {
                    vm.$emit("sendConfig", vm.configINIFields)
                    vm.saving = false;
                    vm.saved = true;
                },
                function(error)
                {
                    console.warn("No JSON retrieved by Vue. Check that Flask received parameters.");
                }
            )
        }
    },
    mounted: function()
    {
        this.$set(this, "configINIFields", this.configINI);
    },
    created: function()
    {
        this.checkPass();
    },
    props:
    {
        configINI: Object
    }
}
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
    .margin-30-px
    {
        margin: 30px;
    }
    .input-group>.input-group-prepend 
    {
        flex: 0 0 15%;
    }
    .input-group .input-group-text 
    {
        width: 100%;
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