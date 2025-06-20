--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9 (Ubuntu 16.9-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.9 (Ubuntu 16.9-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: postgres_fdw; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgres_fdw WITH SCHEMA public;


--
-- Name: EXTENSION postgres_fdw; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgres_fdw IS 'foreign-data wrapper for remote PostgreSQL servers';


--
-- Name: usp_event_log_add(text, integer, integer, numeric, text, timestamp with time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_event_log_add(p_entity_id text, p_event_type_id integer, p_reason_id integer, p_value numeric, p_unit text, p_ts timestamp with time zone) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO public.event_log (
        entity_id,
        event_type_id,
        reason_id,
        value,
        unit,
        ts,
        inserted_at,
        inserted_by
    ) VALUES (
        p_entity_id,
        p_event_type_id,
        p_reason_id,
        p_value,
        p_unit,
        p_ts,
        NOW(),
        current_user
    );

    RETURN 'Event logged successfully';
END;
$$;


ALTER FUNCTION public.usp_event_log_add(p_entity_id text, p_event_type_id integer, p_reason_id integer, p_value numeric, p_unit text, p_ts timestamp with time zone) OWNER TO postgres;

--
-- Name: usp_textdata_add(character varying, text, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_textdata_add(x_id_dev character varying, x_dat text, d_ts timestamp without time zone) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_i_dat INTEGER;  -- Renamed the variable to avoid ambiguity
    d_crt TIMESTAMP := NOW();
BEGIN
    INSERT INTO TextData (X_ID_DEV, X_DAT, D_TS, D_CRT)
    VALUES (x_id_dev, x_dat, d_ts, d_crt)
    RETURNING I_DAT INTO v_i_dat;

    RETURN v_i_dat::TEXT;
EXCEPTION WHEN OTHERS THEN
    RETURN SQLERRM;  -- Return the actual error message
END;
$$;


ALTER FUNCTION public.usp_textdata_add(x_id_dev character varying, x_dat text, d_ts timestamp without time zone) OWNER TO postgres;

--
-- Name: usp_textdata_all_by_device(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_textdata_all_by_device(p_x_id_dev character varying) RETURNS TABLE(i_dat integer, x_id_dev character varying, x_dat text, d_ts timestamp without time zone, d_crt timestamp without time zone)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY 
    SELECT TextData.I_DAT, TextData.X_ID_DEV, TextData.X_DAT, TextData.D_TS, TextData.D_CRT
    FROM TextData
    WHERE TextData.X_ID_DEV = p_x_id_dev;
END;
$$;


ALTER FUNCTION public.usp_textdata_all_by_device(p_x_id_dev character varying) OWNER TO postgres;

--
-- Name: usp_textdata_by_date(timestamp without time zone, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_textdata_by_date(p_start_date timestamp without time zone, p_end_date timestamp without time zone) RETURNS TABLE(i_dat integer, x_id_dev character varying, x_dat text, d_ts timestamp without time zone, d_crt timestamp without time zone)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY 
    SELECT 
        TextData.I_DAT AS i_dat, 
        TextData.X_ID_DEV AS x_id_dev, 
        TextData.X_DAT AS x_dat, 
        TextData.D_TS AS d_ts, 
        TextData.D_CRT AS d_crt
    FROM TextData
    WHERE TextData.D_TS BETWEEN p_start_date AND p_end_date;  -- Added table alias here
END;
$$;


ALTER FUNCTION public.usp_textdata_by_date(p_start_date timestamp without time zone, p_end_date timestamp without time zone) OWNER TO postgres;

--
-- Name: usp_textdata_by_id(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_textdata_by_id(p_id integer) RETURNS TABLE(i_dat integer, x_id_dev character varying, x_dat text, d_ts timestamp without time zone, d_crt timestamp without time zone)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        TextData.I_DAT AS i_dat,
        TextData.X_ID_DEV AS x_id_dev,
        TextData.X_DAT AS x_dat,
        TextData.D_TS AS d_ts,
        TextData.D_CRT AS d_crt
    FROM TextData
    WHERE TextData.I_DAT = p_id;
END;
$$;


ALTER FUNCTION public.usp_textdata_by_id(p_id integer) OWNER TO postgres;

--
-- Name: usp_textdata_delete_all(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_textdata_delete_all() RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM TextData;
    RETURN 'All records deleted successfully';
EXCEPTION WHEN OTHERS THEN
    RETURN SQLERRM;  -- Return the actual error message if something goes wrong
END;
$$;


ALTER FUNCTION public.usp_textdata_delete_all() OWNER TO postgres;

--
-- Name: usp_textdata_delete_by_device(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_textdata_delete_by_device(p_x_id_dev character varying) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM TextData
    WHERE X_ID_DEV = p_x_id_dev;
    
    RETURN 'Records for device deleted successfully';
EXCEPTION WHEN OTHERS THEN
    RETURN SQLERRM;  -- Return the actual error message if something goes wrong
END;
$$;


ALTER FUNCTION public.usp_textdata_delete_by_device(p_x_id_dev character varying) OWNER TO postgres;

--
-- Name: usp_textdata_delete_by_id(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_textdata_delete_by_id(p_i_dat integer) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM TextData
    WHERE I_DAT = p_i_dat;
    
    RETURN 'Record deleted successfully';
EXCEPTION WHEN OTHERS THEN
    RETURN SQLERRM;  -- Return the actual error message if something goes wrong
END;
$$;


ALTER FUNCTION public.usp_textdata_delete_by_id(p_i_dat integer) OWNER TO postgres;

--
-- Name: usp_textdata_edit(integer, character varying, text, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_textdata_edit(p_i_dat integer, p_x_id_dev character varying, p_x_dat text, p_d_ts timestamp without time zone) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE TextData
    SET 
        X_ID_DEV = p_x_id_dev,
        X_DAT = p_x_dat,
        D_TS = p_d_ts
    WHERE I_DAT = p_i_dat;
    
    IF FOUND THEN
        RETURN 'Record updated successfully';
    ELSE
        RETURN 'No record found to update';
    END IF;
EXCEPTION WHEN OTHERS THEN
    RETURN SQLERRM;  -- Return error message if something goes wrong
END;
$$;


ALTER FUNCTION public.usp_textdata_edit(p_i_dat integer, p_x_id_dev character varying, p_x_dat text, p_d_ts timestamp without time zone) OWNER TO postgres;

--
-- Name: parcortlsmaint_server; Type: SERVER; Schema: -; Owner: postgres
--

CREATE SERVER parcortlsmaint_server FOREIGN DATA WRAPPER postgres_fdw OPTIONS (
    dbname 'ParcoRTLSMaint',
    host 'localhost',
    port '5432'
);


ALTER SERVER parcortlsmaint_server OWNER TO postgres;

--
-- Name: USER MAPPING parcoadmin SERVER parcortlsmaint_server; Type: USER MAPPING; Schema: -; Owner: postgres
--

CREATE USER MAPPING FOR parcoadmin SERVER parcortlsmaint_server OPTIONS (
    password 'parcoMCSE04106!',
    "user" 'parcoadmin'
);


--
-- Name: USER MAPPING postgres SERVER parcortlsmaint_server; Type: USER MAPPING; Schema: -; Owner: postgres
--

CREATE USER MAPPING FOR postgres SERVER parcortlsmaint_server OPTIONS (
    password 'parcoMCSE04106!',
    "user" 'postgres'
);


--
-- Name: devices; Type: FOREIGN TABLE; Schema: public; Owner: postgres
--

CREATE FOREIGN TABLE public.devices (
    x_id_dev character varying(200) NOT NULL,
    i_typ_dev integer NOT NULL,
    x_nm_dev character varying(200),
    d_srv_bgn timestamp without time zone,
    d_srv_end timestamp without time zone,
    n_moe_x real,
    n_moe_y real,
    n_moe_z real,
    f_log boolean NOT NULL
)
SERVER parcortlsmaint_server
OPTIONS (
    schema_name 'public',
    table_name 'devices'
);
ALTER FOREIGN TABLE public.devices ALTER COLUMN x_id_dev OPTIONS (
    column_name 'x_id_dev'
);
ALTER FOREIGN TABLE public.devices ALTER COLUMN i_typ_dev OPTIONS (
    column_name 'i_typ_dev'
);
ALTER FOREIGN TABLE public.devices ALTER COLUMN x_nm_dev OPTIONS (
    column_name 'x_nm_dev'
);
ALTER FOREIGN TABLE public.devices ALTER COLUMN d_srv_bgn OPTIONS (
    column_name 'd_srv_bgn'
);
ALTER FOREIGN TABLE public.devices ALTER COLUMN d_srv_end OPTIONS (
    column_name 'd_srv_end'
);
ALTER FOREIGN TABLE public.devices ALTER COLUMN n_moe_x OPTIONS (
    column_name 'n_moe_x'
);
ALTER FOREIGN TABLE public.devices ALTER COLUMN n_moe_y OPTIONS (
    column_name 'n_moe_y'
);
ALTER FOREIGN TABLE public.devices ALTER COLUMN n_moe_z OPTIONS (
    column_name 'n_moe_z'
);
ALTER FOREIGN TABLE public.devices ALTER COLUMN f_log OPTIONS (
    column_name 'f_log'
);


ALTER FOREIGN TABLE public.devices OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: dtproperties; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dtproperties (
    id integer NOT NULL,
    objectid integer,
    property character varying(64) NOT NULL,
    value character varying(255),
    uvalue character varying(255),
    lvalue bytea,
    version integer NOT NULL
);


ALTER TABLE public.dtproperties OWNER TO postgres;

--
-- Name: dtproperties_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dtproperties_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.dtproperties_id_seq OWNER TO postgres;

--
-- Name: dtproperties_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dtproperties_id_seq OWNED BY public.dtproperties.id;


--
-- Name: event_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.event_log (
    id integer NOT NULL,
    entity_id text NOT NULL,
    event_type_id integer NOT NULL,
    reason_id integer,
    value numeric(12,4),
    unit text,
    ts timestamp with time zone DEFAULT now() NOT NULL,
    inserted_at timestamp with time zone DEFAULT now(),
    inserted_by text DEFAULT CURRENT_USER
);


ALTER TABLE public.event_log OWNER TO postgres;

--
-- Name: event_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.event_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.event_log_id_seq OWNER TO postgres;

--
-- Name: event_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.event_log_id_seq OWNED BY public.event_log.id;


--
-- Name: textdata; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.textdata (
    i_dat integer NOT NULL,
    x_id_dev character varying(200) NOT NULL,
    x_dat text NOT NULL,
    d_ts timestamp without time zone NOT NULL,
    d_crt timestamp without time zone NOT NULL
);


ALTER TABLE public.textdata OWNER TO postgres;

--
-- Name: textdata_i_dat_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.textdata_i_dat_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.textdata_i_dat_seq OWNER TO postgres;

--
-- Name: textdata_i_dat_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.textdata_i_dat_seq OWNED BY public.textdata.i_dat;


--
-- Name: tlk_event_reason; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tlk_event_reason (
    id integer NOT NULL,
    description text NOT NULL
);


ALTER TABLE public.tlk_event_reason OWNER TO postgres;

--
-- Name: tlk_event_reason_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tlk_event_reason_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tlk_event_reason_id_seq OWNER TO postgres;

--
-- Name: tlk_event_reason_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tlk_event_reason_id_seq OWNED BY public.tlk_event_reason.id;


--
-- Name: tlk_event_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tlk_event_type (
    id integer NOT NULL,
    name text NOT NULL
);


ALTER TABLE public.tlk_event_type OWNER TO postgres;

--
-- Name: tlk_event_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tlk_event_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tlk_event_type_id_seq OWNER TO postgres;

--
-- Name: tlk_event_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tlk_event_type_id_seq OWNED BY public.tlk_event_type.id;


--
-- Name: tlk_rules; Type: TABLE; Schema: public; Owner: parcoadmin
--

CREATE TABLE public.tlk_rules (
    id integer NOT NULL,
    name text NOT NULL,
    is_enabled boolean DEFAULT true NOT NULL,
    priority integer DEFAULT 1 NOT NULL,
    conditions jsonb NOT NULL,
    actions jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    created_by text DEFAULT CURRENT_USER,
    updated_by text DEFAULT CURRENT_USER
);


ALTER TABLE public.tlk_rules OWNER TO parcoadmin;

--
-- Name: TABLE tlk_rules; Type: COMMENT; Schema: public; Owner: parcoadmin
--

COMMENT ON TABLE public.tlk_rules IS 'Stores rules for TETSE to evaluate events and trigger actions';


--
-- Name: COLUMN tlk_rules.conditions; Type: COMMENT; Schema: public; Owner: parcoadmin
--

COMMENT ON COLUMN public.tlk_rules.conditions IS 'JSONB object specifying conditions (e.g., trigger, zone, entity_status)';


--
-- Name: COLUMN tlk_rules.actions; Type: COMMENT; Schema: public; Owner: parcoadmin
--

COMMENT ON COLUMN public.tlk_rules.actions IS 'JSONB array of actions (e.g., mqtt_publish with topic and payload)';


--
-- Name: tlk_rules_id_seq; Type: SEQUENCE; Schema: public; Owner: parcoadmin
--

CREATE SEQUENCE public.tlk_rules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tlk_rules_id_seq OWNER TO parcoadmin;

--
-- Name: tlk_rules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: parcoadmin
--

ALTER SEQUENCE public.tlk_rules_id_seq OWNED BY public.tlk_rules.id;


--
-- Name: dtproperties id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dtproperties ALTER COLUMN id SET DEFAULT nextval('public.dtproperties_id_seq'::regclass);


--
-- Name: event_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_log ALTER COLUMN id SET DEFAULT nextval('public.event_log_id_seq'::regclass);


--
-- Name: textdata i_dat; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.textdata ALTER COLUMN i_dat SET DEFAULT nextval('public.textdata_i_dat_seq'::regclass);


--
-- Name: tlk_event_reason id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tlk_event_reason ALTER COLUMN id SET DEFAULT nextval('public.tlk_event_reason_id_seq'::regclass);


--
-- Name: tlk_event_type id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tlk_event_type ALTER COLUMN id SET DEFAULT nextval('public.tlk_event_type_id_seq'::regclass);


--
-- Name: tlk_rules id; Type: DEFAULT; Schema: public; Owner: parcoadmin
--

ALTER TABLE ONLY public.tlk_rules ALTER COLUMN id SET DEFAULT nextval('public.tlk_rules_id_seq'::regclass);


--
-- Data for Name: dtproperties; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dtproperties (id, objectid, property, value, uvalue, lvalue, version) FROM stdin;
1	\N	DtgSchemaOBJECT	\N	\N	\N	0
2	1	DtgSchemaGUID	{EA3E6268-D998-11CE-9454-00AA00A3F36E}	{EA3E6268-D998-11CE-9454-00AA00A3F36E}	\N	0
3	1	DtgSchemaNAME	DIAGRAM1	DIAGRAM1	\N	0
4	1	DtgDSRefBYTES	388	388	\N	0
5	1	DtgDSRefDATA	\N	\N	\\xdb6e80e9c1b10d11ad5100ac90f5739000002050153d	0
\.


--
-- Data for Name: event_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.event_log (id, entity_id, event_type_id, reason_id, value, unit, ts, inserted_at, inserted_by) FROM stdin;
2	Strategy-BOT-42	2	4	-3.4000	percent	2025-05-25 15:26:32.402384+00	2025-05-25 15:26:32.402384+00	postgres
4	Strategy-BOT-42	1	\N	\N	\N	2025-05-25 22:52:30.092932+00	2025-05-25 22:52:30.093598+00	parcoadmin
5	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 00:04:48.030252+00	2025-05-26 00:04:48.033089+00	parcoadmin
6	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 00:55:06.745639+00	2025-05-26 00:55:06.746244+00	parcoadmin
7	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 00:55:28.466438+00	2025-05-26 00:55:28.470034+00	parcoadmin
8	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 01:23:47.37485+00	2025-05-26 01:23:47.375128+00	parcoadmin
9	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 03:18:13.477167+00	2025-05-26 03:18:13.480052+00	parcoadmin
10	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 03:51:00.459517+00	2025-05-26 03:51:00.460032+00	parcoadmin
11	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 03:58:13.713893+00	2025-05-26 03:58:13.717878+00	parcoadmin
12	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 03:59:44.413406+00	2025-05-26 03:59:44.415888+00	parcoadmin
13	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 04:23:43.714829+00	2025-05-26 04:23:43.719977+00	parcoadmin
14	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 04:23:59.122926+00	2025-05-26 04:23:59.124054+00	parcoadmin
15	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 04:24:36.715493+00	2025-05-26 04:24:36.716163+00	parcoadmin
16	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 04:25:46.92836+00	2025-05-26 04:25:46.92865+00	parcoadmin
17	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 04:26:22.612352+00	2025-05-26 04:26:22.613424+00	parcoadmin
18	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 05:02:54.687663+00	2025-05-26 05:02:54.688137+00	parcoadmin
19	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 05:03:15.813623+00	2025-05-26 05:03:15.815214+00	parcoadmin
20	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 14:04:16.04256+00	2025-05-26 14:04:16.042896+00	parcoadmin
21	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 14:04:26.469997+00	2025-05-26 14:04:26.472018+00	parcoadmin
22	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 14:04:27.845453+00	2025-05-26 14:04:27.846387+00	parcoadmin
23	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 14:04:28.714354+00	2025-05-26 14:04:28.714864+00	parcoadmin
24	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 14:04:29.476498+00	2025-05-26 14:04:29.476825+00	parcoadmin
25	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 14:04:30.217054+00	2025-05-26 14:04:30.2214+00	parcoadmin
26	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 14:04:30.906504+00	2025-05-26 14:04:30.9075+00	parcoadmin
27	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 14:04:31.625375+00	2025-05-26 14:04:31.625682+00	parcoadmin
28	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 14:04:32.362745+00	2025-05-26 14:04:32.363053+00	parcoadmin
29	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 14:04:43.527256+00	2025-05-26 14:04:43.527602+00	parcoadmin
30	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 14:04:44.134893+00	2025-05-26 14:04:44.137356+00	parcoadmin
31	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 14:04:44.741113+00	2025-05-26 14:04:44.743209+00	parcoadmin
32	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 14:04:45.283971+00	2025-05-26 14:04:45.284407+00	parcoadmin
33	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 14:04:45.861075+00	2025-05-26 14:04:45.86338+00	parcoadmin
34	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 14:04:46.418956+00	2025-05-26 14:04:46.420007+00	parcoadmin
35	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 14:04:46.951223+00	2025-05-26 14:04:46.951632+00	parcoadmin
36	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 14:04:47.554978+00	2025-05-26 14:04:47.555397+00	parcoadmin
37	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 14:04:48.100793+00	2025-05-26 14:04:48.101076+00	parcoadmin
38	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 14:04:48.645816+00	2025-05-26 14:04:48.646963+00	parcoadmin
39	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 14:04:49.208533+00	2025-05-26 14:04:49.211558+00	parcoadmin
40	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 14:04:49.771731+00	2025-05-26 14:04:49.772086+00	parcoadmin
41	Strategy-BOT-42	1	\N	\N	\N	2025-05-26 14:12:48.457276+00	2025-05-26 14:12:48.507216+00	parcoadmin
42	Strategy-BOT-42	5	4	1.0000	percent	2025-05-27 08:21:00+00	2025-05-28 00:50:02.075829+00	parcoadmin
43	Strategy-BOT-42	5	4	1.0000	percent	2025-05-28 01:23:23.042596+00	2025-05-28 01:23:23.043513+00	parcoadmin
44	Strategy-BOT-42	5	4	1.0000	percent	2025-05-28 01:44:33.955847+00	2025-05-28 01:44:33.956202+00	parcoadmin
45	Strategy-BOT-42	5	4	1.0000	percent	2025-05-28 01:30:00+00	2025-05-28 01:56:24.928984+00	parcoadmin
46	Strategy-BOT-42	5	4	1.0000	percent	2025-05-28 01:57:36.95548+00	2025-05-28 01:57:36.955879+00	parcoadmin
47	Strategy-BOT-42	5	4	1.0000	percent	2025-05-28 01:30:00+00	2025-05-28 01:59:32.693982+00	parcoadmin
48	Strategy-BOT-42	5	4	1.0000	percent	2025-05-28 02:00:41.357564+00	2025-05-28 02:00:41.362123+00	parcoadmin
49	Strategy-BOT-42	5	4	1.0000	percent	2025-05-28 01:30:00+00	2025-05-28 02:23:17.822221+00	parcoadmin
50	Strategy-BOT-42	5	4	1.0000	percent	2025-05-28 02:30:00+00	2025-05-28 05:41:47.950747+00	parcoadmin
51	Strategy-BOT-42	5	4	1.0000	percent	2025-05-28 03:30:00+00	2025-05-28 05:57:59.469311+00	parcoadmin
52	Strategy-BOT-42	5	4	1.0000	percent	2025-05-28 05:59:52.226136+00	2025-05-28 05:59:52.227066+00	parcoadmin
53	Strategy-BOT-42	5	4	1.0000	percent	2025-05-28 03:30:00+00	2025-05-28 06:08:42.743723+00	parcoadmin
54	Strategy-BOT-42	5	4	1.0000	percent	2025-05-28 06:09:22.146786+00	2025-05-28 06:09:22.147086+00	parcoadmin
56	Eddy123	5	4	1.0000	presence	2025-06-01 12:00:00+00	2025-06-01 15:47:31.437168+00	parcoadmin
57	Eddy123	6	4	1.0000	presence	2025-06-01 12:00:00+00	2025-06-01 16:16:44.346774+00	parcoadmin
62	Eddy	7	4	1.0000	zone:Living Room	2025-06-01 11:17:00+00	2025-06-01 19:24:12.025304+00	parcoadmin
\.


--
-- Data for Name: textdata; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.textdata (i_dat, x_id_dev, x_dat, d_ts, d_crt) FROM stdin;
3	Device456	Sample Data 2	2025-02-05 15:46:08.851376	2025-02-05 15:46:08.851376
5	Device789	Updated Data	2025-02-05 15:52:15.396309	2025-02-05 15:48:26.658966
6	1	Test event	2025-03-05 04:32:31.333394	2025-03-05 04:32:31.454054
7	1		2025-03-05 04:32:31.489125	2025-03-05 04:32:31.607794
8	1	Test event	2025-03-05 04:36:05.319603	2025-03-05 04:36:05.441245
9	1	Test event	2025-03-05 05:12:53.790053	2025-03-05 05:12:53.849447
10	1	Test event	2025-03-05 05:17:42.220623	2025-03-05 05:17:42.283087
11	1	Test event	2025-03-05 05:35:19.52082	2025-03-05 05:35:19.581922
12	1	Test event	2025-03-05 05:41:17.391549	2025-03-05 05:41:17.453215
13	1	Test event	2025-03-05 05:45:38.975995	2025-03-05 05:45:39.033358
\.


--
-- Data for Name: tlk_event_reason; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tlk_event_reason (id, description) FROM stdin;
1	Triggered by volatility spike
2	API lag from ExecutionAPI-X
3	Risk control threshold breached
4	Analyst override via dashboard
\.


--
-- Data for Name: tlk_event_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tlk_event_type (id, name) FROM stdin;
1	profit_drop
2	latency_spike
3	stop_loss
4	manual_override
5	TestEvent
6	entered restricted zone
7	ZoneEntry
8	ZoneExit
\.


--
-- Data for Name: tlk_rules; Type: TABLE DATA; Schema: public; Owner: parcoadmin
--

COPY public.tlk_rules (id, name, is_enabled, priority, conditions, actions, created_at, updated_at, created_by, updated_by) FROM stdin;
1	Backyard_Animal_Deterrent	t	1	{"zone": "Backyard", "trigger": "AnimalDetected", "entity_status": "indoors"}	[{"parameters": {"topic": "homeassistant/switch/deterrent/backyard/set", "payload": "ON"}, "action_type": "mqtt_publish"}]	2025-06-01 18:29:44.253275+00	2025-06-01 18:29:44.253275+00	parcoadmin	parcoadmin
2	Rule for SIM1 in 2303251508CL1 20250610060046	t	1	{}	{"parameters": {"zone": "2303251508CL1", "action": "alert", "priority": 1, "entity_id": "SIM1", "conditions": {}, "duration_sec": 60}, "action_type": "alert"}	2025-06-10 06:00:46.336737+00	2025-06-10 06:00:46.336737+00	parcoadmin	parcoadmin
3	Rule for SIM1 in 2303251508CL1 20250610060351	t	1	{}	{"parameters": {"zone": "2303251508CL1", "action": "alert", "priority": 1, "entity_id": "SIM1", "conditions": {}, "duration_sec": 30}, "action_type": "alert"}	2025-06-10 06:03:51.750519+00	2025-06-10 06:03:51.750519+00	parcoadmin	parcoadmin
4	Rule for SIM1 in 2303251508CL1 20250610062642	t	1	{}	{"parameters": {"zone": "2303251508CL1", "action": "alert", "priority": 1, "entity_id": "SIM1", "conditions": {}, "duration_sec": 60}, "action_type": "alert"}	2025-06-10 06:26:42.485062+00	2025-06-10 06:26:42.485062+00	parcoadmin	parcoadmin
5	Rule for SIM1 in 2303251508CL1 20250610062826	t	1	{}	{"parameters": {"zone": "2303251508CL1", "action": "alert", "priority": 1, "entity_id": "SIM1", "conditions": {}, "duration_sec": 60}, "action_type": "alert"}	2025-06-10 06:28:26.286027+00	2025-06-10 06:28:26.286027+00	parcoadmin	parcoadmin
6	Rule for SIM2 in 2303251508CL1 20250610062955	t	1	{}	{"parameters": {"zone": "2303251508CL1", "action": "alert", "priority": 1, "entity_id": "SIM2", "conditions": {}, "duration_sec": 60}, "action_type": "alert"}	2025-06-10 06:29:55.963016+00	2025-06-10 06:29:55.963016+00	parcoadmin	parcoadmin
7	Rule for SIM1 in 2303251508CL1 20250610063122	t	1	{}	{"parameters": {"zone": "2303251508CL1", "action": "alert", "priority": 1, "entity_id": "SIM1", "conditions": {}, "duration_sec": 60}, "action_type": "alert"}	2025-06-10 06:31:22.733019+00	2025-06-10 06:31:22.733019+00	parcoadmin	parcoadmin
8	Rule for SIM1 in 2303251508CL1 20250610063227	t	1	{}	{"parameters": {"zone": "2303251508CL1", "action": "alert", "priority": 1, "entity_id": "SIM1", "conditions": {}, "duration_sec": 60}, "action_type": "alert"}	2025-06-10 06:32:27.645377+00	2025-06-10 06:32:27.645377+00	parcoadmin	parcoadmin
9	Rule for Case Carts in the 20250611000202	t	1	{}	{"parameters": {"zone": "the", "action": "alert", "priority": 1, "entity_id": "Case Carts", "conditions": {}, "duration_sec": 60}, "action_type": "alert"}	2025-06-11 00:02:02.733441+00	2025-06-11 00:02:02.733441+00	parcoadmin	parcoadmin
10	Rule for eddy in the 20250611224746	t	1	{}	{"parameters": {"zone": "the", "action": "alert", "priority": 1, "entity_id": "eddy", "conditions": {}, "duration_sec": 60}, "action_type": "alert"}	2025-06-11 22:47:46.946434+00	2025-06-11 22:47:46.946434+00	parcoadmin	parcoadmin
11	Rule for eddy in the 20250611225251	t	1	{}	{"parameters": {"zone": "the", "action": "mqtt", "priority": 1, "entity_id": "eddy", "conditions": {}, "duration_sec": 60}, "action_type": "mqtt"}	2025-06-11 22:52:51.983022+00	2025-06-11 22:52:51.983022+00	parcoadmin	parcoadmin
12	Rule for Eddy in 422 20250615160039	t	1	{}	{"parameters": {"zone": "422", "action": "alert", "priority": 1, "entity_id": "Eddy", "conditions": {}, "duration_sec": 600}, "action_type": "alert"}	2025-06-15 16:00:39.456623+00	2025-06-15 16:00:39.456623+00	parcoadmin	parcoadmin
13	Rule for Eddy in zone 20250615160331	t	1	{}	{"parameters": {"zone": "zone", "action": "alert", "priority": 1, "entity_id": "Eddy", "conditions": {}, "duration_sec": 600}, "action_type": "alert"}	2025-06-15 16:03:31.810576+00	2025-06-15 16:03:31.810576+00	parcoadmin	parcoadmin
14	Rule for Eddy in zone 20250615163008	t	1	{}	{"parameters": {"zone": "zone", "action": "alert", "priority": 1, "entity_id": "Eddy", "conditions": {}, "duration_sec": 600}, "action_type": "alert"}	2025-06-15 16:30:08.292437+00	2025-06-15 16:30:08.292437+00	parcoadmin	parcoadmin
15	Rule for Eddy in zone 20250615163014	t	1	{}	{"parameters": {"zone": "zone", "action": "alert", "priority": 1, "entity_id": "Eddy", "conditions": {}, "duration_sec": 600}, "action_type": "alert"}	2025-06-15 16:30:14.992449+00	2025-06-15 16:30:14.992449+00	parcoadmin	parcoadmin
\.


--
-- Name: dtproperties_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dtproperties_id_seq', 1, false);


--
-- Name: event_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.event_log_id_seq', 63, true);


--
-- Name: textdata_i_dat_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.textdata_i_dat_seq', 13, true);


--
-- Name: tlk_event_reason_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tlk_event_reason_id_seq', 4, true);


--
-- Name: tlk_event_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tlk_event_type_id_seq', 8, true);


--
-- Name: tlk_rules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: parcoadmin
--

SELECT pg_catalog.setval('public.tlk_rules_id_seq', 15, true);


--
-- Name: dtproperties dtproperties_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dtproperties
    ADD CONSTRAINT dtproperties_pkey PRIMARY KEY (id);


--
-- Name: event_log event_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_log
    ADD CONSTRAINT event_log_pkey PRIMARY KEY (id);


--
-- Name: textdata textdata_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.textdata
    ADD CONSTRAINT textdata_pkey PRIMARY KEY (i_dat);


--
-- Name: tlk_event_reason tlk_event_reason_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tlk_event_reason
    ADD CONSTRAINT tlk_event_reason_pkey PRIMARY KEY (id);


--
-- Name: tlk_event_type tlk_event_type_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tlk_event_type
    ADD CONSTRAINT tlk_event_type_name_key UNIQUE (name);


--
-- Name: tlk_event_type tlk_event_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tlk_event_type
    ADD CONSTRAINT tlk_event_type_pkey PRIMARY KEY (id);


--
-- Name: tlk_rules tlk_rules_name_key; Type: CONSTRAINT; Schema: public; Owner: parcoadmin
--

ALTER TABLE ONLY public.tlk_rules
    ADD CONSTRAINT tlk_rules_name_key UNIQUE (name);


--
-- Name: tlk_rules tlk_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: parcoadmin
--

ALTER TABLE ONLY public.tlk_rules
    ADD CONSTRAINT tlk_rules_pkey PRIMARY KEY (id);


--
-- Name: idx_eventlog_entity_ts; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_eventlog_entity_ts ON public.event_log USING btree (entity_id, ts DESC);


--
-- Name: idx_eventlog_type_ts; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_eventlog_type_ts ON public.event_log USING btree (event_type_id, ts DESC);


--
-- Name: idx_tlk_rules_is_enabled_priority; Type: INDEX; Schema: public; Owner: parcoadmin
--

CREATE INDEX idx_tlk_rules_is_enabled_priority ON public.tlk_rules USING btree (is_enabled, priority DESC);


--
-- Name: event_log fk_event_reason; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_log
    ADD CONSTRAINT fk_event_reason FOREIGN KEY (reason_id) REFERENCES public.tlk_event_reason(id);


--
-- Name: event_log fk_event_type; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_log
    ADD CONSTRAINT fk_event_type FOREIGN KEY (event_type_id) REFERENCES public.tlk_event_type(id);


--
-- Name: TABLE event_log; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.event_log TO parcoadmin;


--
-- PostgreSQL database dump complete
--

