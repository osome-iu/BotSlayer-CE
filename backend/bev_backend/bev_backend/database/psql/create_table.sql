CREATE TABLE public.entity
(
  entity_id serial PRIMARY KEY NOT NULL,
  entity_type varchar(20),
  entity_text varchar(2083),
  created_at timestamp without time zone DEFAULT now(),
  unique(entity_type, entity_text)
)
WITH (
  OIDS=FALSE
);



CREATE TABLE public.twtjson
(
  tid bigint PRIMARY KEY NOT NULL,
  tweet jsonb,
  created_at timestamp without time zone DEFAULT now()
) 
WITH (
  OIDS=FALSE
);

CREATE INDEX twtjson_ix_created_at
  ON public.twtjson
  USING BTREE
  (created_at);



CREATE TABLE public.entitytwt
(
  tid bigint NOT NULL,
  entity_id INTEGER,
  user_id bigint NOT NULL,
  bot_score real NOT NULL,
  tweet_date timestamp without time zone NOT NULL,
  created_at timestamp without time zone DEFAULT now(),
  FOREIGN KEY (tid) REFERENCES twtjson (tid) ON DELETE CASCADE,
  FOREIGN KEY (entity_id) REFERENCES entity (entity_id) ON DELETE RESTRICT
)
WITH (
  OIDS=FALSE
);
CREATE INDEX entitytwt_ix_tid
  ON public.entitytwt
  USING HASH
  (tid);

CREATE INDEX entitytwt_ix_userid
  ON public.entitytwt
  USING HASH
  (user_id);

CREATE INDEX entitytwt_ix_tweetdate
  ON public.entitytwt
  USING BTREE
  (tweet_date);

CREATE INDEX entitytwt_ix_bot_score
  ON public.entitytwt
  USING BTREE
  (bot_score);



CREATE TABLE public.config
(
    name varchar(40) PRIMARY KEY NOT NULL,
    valstr varchar(2083) DEFAULT ''
);

INSERT INTO public.config(name) VALUES
  ('consumerKey'),
  ('consumerSecret'),
  ('accessToken'),
  ('accessTokenSecret'),
  ('seed'),
  ('user'),
  ('location'),
  ('pinned');

INSERT INTO public.config(name, valstr) VALUES
  ('cfgpass', 'password_not_set');

SELECT * FROM public.config;
