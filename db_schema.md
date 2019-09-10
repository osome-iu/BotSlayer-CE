# Database Schema

## `twtjson` table

`twtjson` table stores the raw tweets in JSON format.

| column | type | note |
|--------|------|------|
| tid | bigint | Tweet id of the tweet |
| tweet | jsonb | Tweet JSON object |
| created\_at | timestamp | Tweet JSON object |

## `entity` table

`entity` table contains the entities and their types.

| column | type | note |
|--------|------|------|
| entity\_id | integer | ID of the entity, used for joining with other tables |
| entity\_type | string | Type of the entity: hashtag, mentions, etc. |
| entity\_text | string | Entity itself|
| created\_at | timestamp | When the entity was first added |

## `entitytwt` table

`entitytwt` table connects the raw tweet and the entities.
It also stores the botscores accociated with each entity. 

| column | type | note |
|--------|------|------|
| tid | bigint | Tweet id of the tweet in `twtjson` table |
| entity\_id | integer | Entity ID in `entity` table |
| user\_id | bigint | User ID |
| bot\_score  | real | Botscores associated with the entity |
| tweet\_date | timestamp | Creation time of the tweet |
| created\_at | timestamp | Insertion time of the entity |
