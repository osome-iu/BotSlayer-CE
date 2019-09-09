#              BotSlayer-CE API Documentation             #

##               Password Settings               ##

Function:   |     change_password()
------------|-----------------------
Route:      | /api/changePass                           
Parameters: | none                                      
Returns:    | none                                      
Result:     | changes password for config page          

### Extra notes:
Changes the password used in the Config page: `Config.vue`.\
Assuming the user entered their old password correctly twice 
and that they pressed the "Change Password" button twice, 
the frontend will pass that argument (new password) here.

The password is then set in:\
**backend\bev_backend\bev_backend\database\psql\user_setting.py**

### Code:
```python
@application.route("/api/changePass")
def change_password():
    new_pass = request.args.get('newPass', default=' ', type = str)
    set_password_setting(new_pass, loop=loop)
    return "All clear"
```

------------------------------------------

Function:   | check_password()
------------|----------------------
Route:      | /api/checkPass                            
Parameters: | none                                     
Returns:    | boolean OR str (first time setup)         
Result:     | permits/denies access to config page

### Extra notes:
Checks the password attempted in the frontend against the one stored in:\
**backend\bev_backend\bev_backend\database\psql\user_setting.py**

### Code:
```python
@application.route("/api/checkPass")
def check_password():
    pass_attempt = request.args.get('currentPass', default=' ', type = str)
    correct_pass = get_password_setting(loop=loop)

    # Before even attempting to enter a password, the frontend will check anyway.
    # If it receives 'firstTime' because the password's never been sent,
    # it will do a first-time password setup.
    # This is also useful if you choose to not have a password.
    # It will take you straight to the config page since it checks instantly.
    if(correct_pass == 'password_not_set'):
        return 'firstTime'

    if(pass_attempt == correct_pass):
        return 'true'
    else:
        return 'false'
```

------------------------------------------

## User Settings

Function:   | jsonify_user_settings()     
------------|--------------------------
Route:      | none                                      
Parameters: | none                                      
Returns:    | json                                      
Result:     | jsonifies config settings                 

### Extra notes:
Used in `config_read_ep()`

```python
def jsonify_user_settings():
    output = jsonify(get_user_settings(loop=loop))
    return output
```

------------------------------------------

Function:   | config_read_ep()
------------|------------------
Route:      | /api/configRead                           
Parameters: | none                                      
Returns:    | json                                     
Result:     | sends config data to frontend             

### Extra notes:
The config is read and sent to the frontend so that 
the `DataPage` and `Config` pages can display the query and other user settings.

```python
@application.route("/api/configRead")
def config_read_ep():
    return jsonify_user_settings()
```

------------------------------------------

Function:   | config_ini_save()  
------------|-------------------
Route:      | /api/configSave                           
Parameters: | none                                      
Returns:    | none                                      
Result:     | user changes to config saved              

### Extra notes:
This is used to save changes made to the config on the `Config` page.\
It stores the settings in:\
**backend\bev_backend\bev_backend\database\psql\user_setting.py**

Then, it restarts the crawler/streaming supervisor.\
This is so that changed queries (or less likely, changed keys)
are now tracked without having to restart the instance.

```python
@application.route("/api/configSave")
def config_ini_save():
    user_settings = get_user_settings(loop=loop)
    set_user_settings({
        setting_key : request.args.get(setting_key, default="", type=str)
        for setting_key in user_settings.keys()
    }, loop=loop)

    subprocess.run("circusctl restart python3 &", shell=True)
    return "All quiet on the western front"
```


## Backend Callbacks

Function:   | get_disk_space()
------------|------------------
Route:      | /api/diskSpace                            
Parameters: | none                                      
Returns:    | str                                       
Result:     | lets frontend/user know disk space left   

## Extra notes:
This is checked every time before the data is refreshed on the frontend.\
It simply sends a floating point number, like `45.66`,
which represents the disk space remaining on the server/instance.\
If it's below `20`, a warning message is displayed to the user.\
The backend is also using a similar function and
will automatically delete data if it goes below `10`.

```python
@application.route("/api/diskSpace")
def get_disk_space():
    st = statvfs('/')
    avail = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    percent = avail * 1.0 / total * 100.0
    return str(percent)
```

------------------------------------------

Function:   | score_demo()
------------|--------------
Route:      | /api/scoreDemo                            
Parameters: | none                                      
Returns:    | json                                      
Result:     | sends entity statistics to frontend       

## Extra notes:
`score_demo()` is the main function that calls `get_coord_score_report()`
so that all of the necessary information on botness, etc. can
be reported to the frontend.

```python
# Entities are stored in the database without prefixes like the ones below.
# This is because they're stored with a table column
# that lists what type of entity they are (e.g., hashtags).
# These are necessary for display on the frontend, however.
MAIN_ENTITY_PREFIX = {'#', '@', '$'}

@application.route("/api/scoreDemo")
def score_demo():
    # One can pass exclusions from the frontend so that
    # they get results that don't include the items they
    # searched for while retaining the cooccurrences.
    exclusion = request.args.get('exclusion', default=' ', type = str)
    exclusion_set = {
        # remember to strip #, @, or $ to search the DB
        entity[1:].lower() if entity[0] in MAIN_ENTITY_PREFIX
            else entity
        for entity in exclusion.strip(', ').split(",")
        if len(entity) > 0
    }

    try:
        records = get_coord_score_report(loop=loop)
    # If there is any data, the middleware will try to send it,
    # but if there's not enough data to make calculations on
    # the BS Level, the equation may end up dividing by zero.
    # If that happens, this error is passed along to the frontend
    # to let the user know to wait it out or try a different query.
    except asyncpg.exceptions.DivisionByZeroError as e:
        return jsonify([{"insufficient_data": True}])

    toJSONArray = []
    for row in records:
        # Ignore the entities in the exclusion_set.
        entity_text = row['entity_text']
        if entity_text in exclusion_set:
            continue

        # Append the appropriate prefix, if necessary
        entity_type = row['entity_type']
        symbol_prefix = ''
        if (entity_type == "hashtags"):
            symbol_prefix = '#'
        elif (entity_type == "user_mentions"):
            symbol_prefix = '@'
        elif (entity_type == "symbols"):
            symbol_prefix = '$'

        # Tweets with pictures or videos will have a link
        # to a picture or video thumbnail, which the frontend
        # will use to do a Google reverse image search.
        media_link = row['media_link']
        if media_link is None:
            media_link = ''

        # Prepares the database records to be used in the frontend.
        toJSONArray.append(
            {
                "Entity": symbol_prefix+entity_text,
                "Last_Seen": row['last_seen'],
                "Tweets": row['twt_cnt'],
                "Botness": '%.1f' % (float(row['mean_bs']) * 5.0),
                "BS_Level": '%.3f' % (row['coord_score']),
                "Type": entity_type,
                "Trendiness": '%d' % int((float(row['trend']) - 1.0) * 100),
                "Accounts": row['acc_cnt'],
                "MediaLink": media_link
            }
        )

    return jsonify(toJSONArray)
```
