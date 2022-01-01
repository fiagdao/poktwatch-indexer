CREATE TABLE IF NOT EXISTS public.transactions (                                        
     id integer DEFAULT nextval('transactions_id_seq'::regclass) NOT NULL,
     hash character varying(64)  NULL,
     receiver character varying(40)  NULL,
     sender character varying(40)  NULL,
     value bigint  NULL,
     type character varying(24)  NULL,
     fee bigint  NULL,
     height integer  NULL,
     index integer  NULL,
     code integer  NULL,
     memo text  NULL,
     chain character varying(4)  NULL,
     timestamp timestamp without time zone  NULL);

 CREATE TABLE IF NOT EXISTS public.blocks (
     height integer  NULL,
     producer character(40)  NULL,
     relays integer  NULL,
     txs integer  NULL,
     id integer DEFAULT nextval('blocks_id_seq'::regclass) NOT NULL);

 CREATE TABLE IF NOT EXISTS public.state (
     height integer  NULL,
     id integer DEFAULT nextval('state_id_seq'::regclass) NOT NULL);

 CREATE TABLE IF NOT EXISTS public.pulse (
     id integer DEFAULT nextval('pulse_id_seq'::regclass) NOT NULL,
     relays integer  NULL,
     apps integer  NULL,
     nodes integer  NULL);

IF EXISTS (SELECT * FROM STATE)
	BEGIN
		INSERT INTO state VALUES (0)
	END

IF EXISTS (SELECT * FROM pulse)
	BEGIN
		INSERT INTO pulse VALUES (0,0,0)
	END
