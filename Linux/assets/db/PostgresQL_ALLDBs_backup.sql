--
-- PostgreSQL database cluster dump
--

SET default_transaction_read_only = off;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

--
-- Roles
--

CREATE ROLE adminparco;
ALTER ROLE adminparco WITH NOSUPERUSER INHERIT CREATEROLE CREATEDB LOGIN NOREPLICATION NOBYPASSRLS PASSWORD 'SCRAM-SHA-256$4096:Dja7q4PVRbGWcwvBCS1CIg==$0NNhAVfYAFW7q5v7JE7UcvhW7P51nZXowssLHCo3lX8=:gcjG/M6VzPx03rfdz6qjo/36Vszuaf944Dn/wQTuGQ4=';
CREATE ROLE parcoadmin;
ALTER ROLE parcoadmin WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN NOREPLICATION NOBYPASSRLS PASSWORD 'SCRAM-SHA-256$4096:PlzXYomNfUD1kBebmQjTAg==$+GQGHbd6XcTS45yRaKMsvHxyTA5NSyQtcNNmJ2u0xRs=:Fp+2jSLYCuVPejY8ULC1RKMXbmYKclvQEfI+Jww4CzM=';
CREATE ROLE postgres;
ALTER ROLE postgres WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN REPLICATION BYPASSRLS PASSWORD 'SCRAM-SHA-256$4096:VfULSnax1OLtKOwlO6uZ9w==$npI1uP5wfs+XMJ11nCkiNMa9pX8JbgOBmHejyuJtltw=:s6N6YCbxPUpa4l3vcaejFw48eqd5zslaRweaLgMWNHk=';

--
-- User Configurations
--








--
-- Databases
--

--
-- Database "template1" dump
--

\connect template1

--
-- PostgreSQL database dump
--

-- Dumped from database version 16.8 (Ubuntu 16.8-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.8 (Ubuntu 16.8-0ubuntu0.24.04.1)

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
-- PostgreSQL database dump complete
--

--
-- Database "ParcoRTLSData" dump
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 16.8 (Ubuntu 16.8-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.8 (Ubuntu 16.8-0ubuntu0.24.04.1)

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
-- Name: ParcoRTLSData; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE "ParcoRTLSData" WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.UTF-8';


ALTER DATABASE "ParcoRTLSData" OWNER TO postgres;

\connect "ParcoRTLSData"

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
-- Name: dtproperties id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dtproperties ALTER COLUMN id SET DEFAULT nextval('public.dtproperties_id_seq'::regclass);


--
-- Name: textdata i_dat; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.textdata ALTER COLUMN i_dat SET DEFAULT nextval('public.textdata_i_dat_seq'::regclass);


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
-- Name: dtproperties_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dtproperties_id_seq', 1, false);


--
-- Name: textdata_i_dat_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.textdata_i_dat_seq', 13, true);


--
-- Name: dtproperties dtproperties_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dtproperties
    ADD CONSTRAINT dtproperties_pkey PRIMARY KEY (id);


--
-- Name: textdata textdata_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.textdata
    ADD CONSTRAINT textdata_pkey PRIMARY KEY (i_dat);


--
-- PostgreSQL database dump complete
--

--
-- Database "ParcoRTLSHistO" dump
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 16.8 (Ubuntu 16.8-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.8 (Ubuntu 16.8-0ubuntu0.24.04.1)

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
-- Name: ParcoRTLSHistO; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE "ParcoRTLSHistO" WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.UTF-8';


ALTER DATABASE "ParcoRTLSHistO" OWNER TO postgres;

\connect "ParcoRTLSHistO"

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
-- Name: usp_delete_all(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_delete_all() RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM PositionHistory;
    RETURN 'All records deleted successfully';
EXCEPTION WHEN OTHERS THEN
    RETURN SQLERRM; -- Return the actual error message if something goes wrong
END;
$$;


ALTER FUNCTION public.usp_delete_all() OWNER TO postgres;

--
-- Name: usp_delete_by_id(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_delete_by_id(p_x_id_dev character varying) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM PositionHistory WHERE X_ID_DEV = p_x_id_dev;
    RETURN 'Record deleted successfully';
EXCEPTION WHEN OTHERS THEN
    RETURN SQLERRM;
END;
$$;


ALTER FUNCTION public.usp_delete_by_id(p_x_id_dev character varying) OWNER TO postgres;

--
-- Name: usp_history_by_id(character varying, timestamp without time zone, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_history_by_id(p_x_id_dev character varying, p_d_pos_bgn timestamp without time zone, p_d_pos_end timestamp without time zone) RETURNS TABLE(i_ph integer, x_id_dev character varying, d_pos_bgn timestamp without time zone, d_pos_end timestamp without time zone, n_x real, n_y real, n_z real)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        PositionHistory.I_PH, PositionHistory.X_ID_DEV, PositionHistory.D_POS_BGN, 
        PositionHistory.D_POS_END, PositionHistory.N_X, PositionHistory.N_Y, PositionHistory.N_Z
    FROM PositionHistory
    WHERE X_ID_DEV = p_x_id_dev 
        AND D_POS_BGN >= p_d_pos_bgn 
        AND D_POS_END <= p_d_pos_end;
END;
$$;


ALTER FUNCTION public.usp_history_by_id(p_x_id_dev character varying, p_d_pos_bgn timestamp without time zone, p_d_pos_end timestamp without time zone) OWNER TO postgres;

--
-- Name: usp_history_by_location(real, real, real, real, real, real, timestamp without time zone, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_history_by_location(p_xmin real, p_xmax real, p_ymin real, p_ymax real, p_zmin real, p_zmax real, p_d_pos_bgn timestamp without time zone, p_d_pos_end timestamp without time zone) RETURNS TABLE(i_ph integer, x_id_dev character varying, d_pos_bgn timestamp without time zone, d_pos_end timestamp without time zone, n_x real, n_y real, n_z real)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ph.I_PH,
        ph.X_ID_DEV,
        ph.D_POS_BGN,
        ph.D_POS_END,
        ph.N_X,
        ph.N_Y,
        ph.N_Z
    FROM PositionHistory ph
    WHERE 
        ph.N_X BETWEEN p_xmin AND p_xmax AND
        ph.N_Y BETWEEN p_ymin AND p_ymax AND
        ph.N_Z BETWEEN p_zmin AND p_zmax AND
        ph.D_POS_BGN >= p_d_pos_bgn AND
        ph.D_POS_END <= p_d_pos_end;
END;
$$;


ALTER FUNCTION public.usp_history_by_location(p_xmin real, p_xmax real, p_ymin real, p_ymax real, p_zmin real, p_zmax real, p_d_pos_bgn timestamp without time zone, p_d_pos_end timestamp without time zone) OWNER TO postgres;

--
-- Name: usp_location_by_id(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_location_by_id(p_x_id_dev character varying) RETURNS TABLE(i_ph integer, x_id_dev character varying, d_pos_bgn timestamp without time zone, d_pos_end timestamp without time zone, n_x real, n_y real, n_z real)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        PositionHistory.I_PH,
        PositionHistory.X_ID_DEV,
        PositionHistory.D_POS_BGN,
        PositionHistory.D_POS_END,
        PositionHistory.N_X,
        PositionHistory.N_Y,
        PositionHistory.N_Z
    FROM PositionHistory
    WHERE PositionHistory.X_ID_DEV = p_x_id_dev;
END;
$$;


ALTER FUNCTION public.usp_location_by_id(p_x_id_dev character varying) OWNER TO postgres;

--
-- Name: usp_position_insert(character varying, timestamp without time zone, timestamp without time zone, real, real, real); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_position_insert(p_x_id_dev character varying, p_d_pos_bgn timestamp without time zone, p_d_pos_end timestamp without time zone, p_n_x real, p_n_y real, p_n_z real) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_i_ph INTEGER;
BEGIN
    INSERT INTO PositionHistory (X_ID_DEV, D_POS_BGN, D_POS_END, N_X, N_Y, N_Z)
    VALUES (p_x_id_dev, p_d_pos_bgn, p_d_pos_end, p_n_x, p_n_y, p_n_z)
    RETURNING I_PH INTO v_i_ph;

    RETURN v_i_ph;
EXCEPTION WHEN OTHERS THEN
    RETURN -1;  -- Return -1 if there's an error
END;
$$;


ALTER FUNCTION public.usp_position_insert(p_x_id_dev character varying, p_d_pos_bgn timestamp without time zone, p_d_pos_end timestamp without time zone, p_n_x real, p_n_y real, p_n_z real) OWNER TO postgres;

--
-- Name: usp_position_update(integer, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_position_update(p_i_ph integer, p_d_pos_end timestamp without time zone) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE PositionHistory
    SET D_POS_END = p_d_pos_end
    WHERE I_PH = p_i_ph;

    IF FOUND THEN
        RETURN 'Record updated successfully';
    ELSE
        RETURN 'No record found to update';
    END IF;
EXCEPTION WHEN OTHERS THEN
    RETURN SQLERRM;  -- Return the error message if something goes wrong
END;
$$;


ALTER FUNCTION public.usp_position_update(p_i_ph integer, p_d_pos_end timestamp without time zone) OWNER TO postgres;

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
-- Name: USER MAPPING postgres SERVER parcortlsmaint_server; Type: USER MAPPING; Schema: -; Owner: postgres
--

CREATE USER MAPPING FOR postgres SERVER parcortlsmaint_server OPTIONS (
    password 'parcoMCSE04106!',
    "user" 'postgres'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: devices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.devices (
    x_id_dev character varying(200) NOT NULL,
    i_typ_dev integer,
    x_nm_dev character varying(200),
    d_srv_bgn timestamp without time zone,
    d_srv_end timestamp without time zone,
    n_moe_x real,
    n_moe_y real,
    n_moe_z real,
    f_log boolean
);


ALTER TABLE public.devices OWNER TO postgres;

--
-- Name: entities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.entities (
    x_id_ent character varying(200) NOT NULL,
    i_typ_ent integer,
    x_nm_ent character varying(200),
    d_crt timestamp without time zone,
    d_udt timestamp without time zone
);


ALTER TABLE public.entities OWNER TO postgres;

--
-- Name: positionhistory; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.positionhistory (
    i_ph integer NOT NULL,
    x_id_dev character varying(200) NOT NULL,
    d_pos_bgn timestamp without time zone NOT NULL,
    d_pos_end timestamp without time zone NOT NULL,
    n_x real NOT NULL,
    n_y real NOT NULL,
    n_z real NOT NULL
);


ALTER TABLE public.positionhistory OWNER TO postgres;

--
-- Name: positionhistory_i_ph_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.positionhistory_i_ph_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.positionhistory_i_ph_seq OWNER TO postgres;

--
-- Name: positionhistory_i_ph_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.positionhistory_i_ph_seq OWNED BY public.positionhistory.i_ph;


--
-- Name: positionhistory i_ph; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.positionhistory ALTER COLUMN i_ph SET DEFAULT nextval('public.positionhistory_i_ph_seq'::regclass);


--
-- Data for Name: devices; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.devices (x_id_dev, i_typ_dev, x_nm_dev, d_srv_bgn, d_srv_end, n_moe_x, n_moe_y, n_moe_z, f_log) FROM stdin;
Device001	1	Test Device 1	2025-02-06 10:00:00	2025-02-06 12:00:00	1.1	2.2	3.3	t
1	1	Device 1	2025-02-06 05:20:14.912944	\N	\N	\N	\N	f
DEV001	1	Device 001	2025-02-06 00:06:20.448498	2025-02-07 12:00:00	\N	\N	\N	f
DeviceLoc2	0	Placeholder Device	2025-02-09 06:12:08.417286	\N	\N	\N	\N	f
DeviceLoc	0	Placeholder Device	2025-02-09 06:12:08.417286	\N	\N	\N	\N	f
NewDevice	0	Placeholder Device	2025-02-09 06:12:08.417286	\N	\N	\N	\N	f
\.


--
-- Data for Name: entities; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.entities (x_id_ent, i_typ_ent, x_nm_ent, d_crt, d_udt) FROM stdin;
Entity001	1	Test Entity 1	2025-02-05 09:00:00	2025-02-06 09:00:00
Entity003	3	Original Entity Name	2025-02-06 08:00:00	2025-02-06 09:00:00
ENT101	1	Entity 101	2025-02-06 00:08:49.617623	\N
Entity2	1	Entity 2	2025-02-06 05:20:59.393711	\N
ety	1	Entity ety	2025-02-06 05:20:59.393711	\N
ParentEntityID	1	Parent Entity	2025-02-06 05:42:42.970733	\N
ChildEntityID	1	Child Entity	2025-02-06 05:42:42.970733	\N
\.


--
-- Data for Name: positionhistory; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.positionhistory (i_ph, x_id_dev, d_pos_bgn, d_pos_end, n_x, n_y, n_z) FROM stdin;
3	DeviceLoc	2025-02-05 12:00:00	2025-02-05 12:10:00	1.5	2.5	3.5
4	DeviceLoc2	2025-02-05 13:00:00	2025-02-05 13:10:00	5	5	5
5	NewDevice	2025-02-06 10:00:00	2025-02-06 11:00:00	6	7	8
\.


--
-- Name: positionhistory_i_ph_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.positionhistory_i_ph_seq', 5, true);


--
-- Name: devices local_devices_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT local_devices_pkey PRIMARY KEY (x_id_dev);


--
-- Name: entities local_entities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entities
    ADD CONSTRAINT local_entities_pkey PRIMARY KEY (x_id_ent);


--
-- Name: positionhistory positionhistory_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.positionhistory
    ADD CONSTRAINT positionhistory_pkey PRIMARY KEY (i_ph);


--
-- Name: positionhistory fk_positionhistory_devices; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.positionhistory
    ADD CONSTRAINT fk_positionhistory_devices FOREIGN KEY (x_id_dev) REFERENCES public.devices(x_id_dev);


--
-- PostgreSQL database dump complete
--

--
-- Database "ParcoRTLSHistP" dump
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 16.8 (Ubuntu 16.8-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.8 (Ubuntu 16.8-0ubuntu0.24.04.1)

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
-- Name: ParcoRTLSHistP; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE "ParcoRTLSHistP" WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.UTF-8';


ALTER DATABASE "ParcoRTLSHistP" OWNER TO postgres;

\connect "ParcoRTLSHistP"

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
-- Name: usp_delete_all(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_delete_all() RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM PositionHistory;
    RETURN 'All records deleted successfully';
EXCEPTION WHEN OTHERS THEN
    RETURN SQLERRM;  -- Returns the actual error message if something goes wrong
END;
$$;


ALTER FUNCTION public.usp_delete_all() OWNER TO postgres;

--
-- Name: usp_delete_by_id(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_delete_by_id(p_x_id_dev character varying) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM PositionHistory 
    WHERE X_ID_DEV = p_x_id_dev;

    IF FOUND THEN
        RETURN 'Record(s) deleted successfully';
    ELSE
        RETURN 'No records found for deletion';
    END IF;
EXCEPTION WHEN OTHERS THEN
    RETURN SQLERRM;  -- Returns the actual error message if something goes wrong
END;
$$;


ALTER FUNCTION public.usp_delete_by_id(p_x_id_dev character varying) OWNER TO postgres;

--
-- Name: usp_history_by_id(character varying, timestamp without time zone, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_history_by_id(p_x_id_dev character varying, p_d_pos_bgn timestamp without time zone, p_d_pos_end timestamp without time zone) RETURNS TABLE(i_ph integer, x_id_dev character varying, d_pos_bgn timestamp without time zone, d_pos_end timestamp without time zone, n_x real, n_y real, n_z real)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        PositionHistory.I_PH, 
        PositionHistory.X_ID_DEV, 
        PositionHistory.D_POS_BGN, 
        PositionHistory.D_POS_END, 
        PositionHistory.N_X, 
        PositionHistory.N_Y, 
        PositionHistory.N_Z
    FROM PositionHistory
    WHERE PositionHistory.X_ID_DEV = p_x_id_dev
      AND PositionHistory.D_POS_BGN >= p_d_pos_bgn
      AND PositionHistory.D_POS_END <= p_d_pos_end;
END;
$$;


ALTER FUNCTION public.usp_history_by_id(p_x_id_dev character varying, p_d_pos_bgn timestamp without time zone, p_d_pos_end timestamp without time zone) OWNER TO postgres;

--
-- Name: usp_history_by_location(real, real, real, real, real, real, timestamp without time zone, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_history_by_location(p_x_min real, p_x_max real, p_y_min real, p_y_max real, p_z_min real, p_z_max real, p_d_pos_bgn timestamp without time zone, p_d_pos_end timestamp without time zone) RETURNS TABLE(i_ph integer, x_id_dev character varying, d_pos_bgn timestamp without time zone, d_pos_end timestamp without time zone, n_x real, n_y real, n_z real)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        PositionHistory.I_PH,
        PositionHistory.X_ID_DEV,
        PositionHistory.D_POS_BGN,
        PositionHistory.D_POS_END,
        PositionHistory.N_X,
        PositionHistory.N_Y,
        PositionHistory.N_Z
    FROM PositionHistory
    WHERE PositionHistory.N_X BETWEEN p_x_min AND p_x_max
      AND PositionHistory.N_Y BETWEEN p_y_min AND p_y_max
      AND PositionHistory.N_Z BETWEEN p_z_min AND p_z_max
      AND PositionHistory.D_POS_BGN >= p_d_pos_bgn
      AND PositionHistory.D_POS_END <= p_d_pos_end;
END;
$$;


ALTER FUNCTION public.usp_history_by_location(p_x_min real, p_x_max real, p_y_min real, p_y_max real, p_z_min real, p_z_max real, p_d_pos_bgn timestamp without time zone, p_d_pos_end timestamp without time zone) OWNER TO postgres;

--
-- Name: usp_location_by_id(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_location_by_id(p_x_id_dev character varying) RETURNS TABLE(i_ph integer, x_id_dev character varying, d_pos_bgn timestamp without time zone, d_pos_end timestamp without time zone, n_x real, n_y real, n_z real)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        PositionHistory.I_PH,
        PositionHistory.X_ID_DEV,
        PositionHistory.D_POS_BGN,
        PositionHistory.D_POS_END,
        PositionHistory.N_X,
        PositionHistory.N_Y,
        PositionHistory.N_Z
    FROM PositionHistory
    WHERE PositionHistory.X_ID_DEV = p_x_id_dev;
END;
$$;


ALTER FUNCTION public.usp_location_by_id(p_x_id_dev character varying) OWNER TO postgres;

--
-- Name: usp_position_insert(character varying, timestamp without time zone, timestamp without time zone, real, real, real); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_position_insert(p_x_id_dev character varying, p_d_pos_bgn timestamp without time zone, p_d_pos_end timestamp without time zone, p_n_x real, p_n_y real, p_n_z real) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_i_ph INTEGER;
BEGIN
    INSERT INTO PositionHistory (X_ID_DEV, D_POS_BGN, D_POS_END, N_X, N_Y, N_Z)
    VALUES (p_x_id_dev, p_d_pos_bgn, p_d_pos_end, p_n_x, p_n_y, p_n_z)
    RETURNING I_PH INTO v_i_ph;

    RETURN v_i_ph;  -- Return the ID of the inserted record
EXCEPTION WHEN OTHERS THEN
    RETURN -1;  -- Return -1 in case of an error
END;
$$;


ALTER FUNCTION public.usp_position_insert(p_x_id_dev character varying, p_d_pos_bgn timestamp without time zone, p_d_pos_end timestamp without time zone, p_n_x real, p_n_y real, p_n_z real) OWNER TO postgres;

--
-- Name: usp_position_update(integer, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_position_update(p_i_ph integer, p_d_pos_end timestamp without time zone) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE PositionHistory
    SET D_POS_END = p_d_pos_end
    WHERE I_PH = p_i_ph;

    IF FOUND THEN
        RETURN 'Record updated successfully';
    ELSE
        RETURN 'No record found to update';
    END IF;
EXCEPTION WHEN OTHERS THEN
    RETURN SQLERRM;  -- Return the error message if something goes wrong
END;
$$;


ALTER FUNCTION public.usp_position_update(p_i_ph integer, p_d_pos_end timestamp without time zone) OWNER TO postgres;

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
-- Name: USER MAPPING postgres SERVER parcortlsmaint_server; Type: USER MAPPING; Schema: -; Owner: postgres
--

CREATE USER MAPPING FOR postgres SERVER parcortlsmaint_server OPTIONS (
    password 'parcoMCSE04106!',
    "user" 'postgres'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: devices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.devices (
    x_id_dev character varying(200) NOT NULL,
    i_typ_dev integer,
    x_nm_dev character varying(200),
    d_srv_bgn timestamp without time zone,
    d_srv_end timestamp without time zone,
    n_moe_x real,
    n_moe_y real,
    n_moe_z real,
    f_log boolean
);


ALTER TABLE public.devices OWNER TO postgres;

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
-- Name: entities; Type: FOREIGN TABLE; Schema: public; Owner: postgres
--

CREATE FOREIGN TABLE public.entities (
    x_id_ent character varying(200) NOT NULL,
    i_typ_ent integer,
    x_nm_ent character varying(200),
    d_crt timestamp without time zone,
    d_udt timestamp without time zone
)
SERVER parcortlsmaint_server
OPTIONS (
    schema_name 'public',
    table_name 'entities'
);
ALTER FOREIGN TABLE public.entities ALTER COLUMN x_id_ent OPTIONS (
    column_name 'x_id_ent'
);
ALTER FOREIGN TABLE public.entities ALTER COLUMN i_typ_ent OPTIONS (
    column_name 'i_typ_ent'
);
ALTER FOREIGN TABLE public.entities ALTER COLUMN x_nm_ent OPTIONS (
    column_name 'x_nm_ent'
);
ALTER FOREIGN TABLE public.entities ALTER COLUMN d_crt OPTIONS (
    column_name 'd_crt'
);
ALTER FOREIGN TABLE public.entities ALTER COLUMN d_udt OPTIONS (
    column_name 'd_udt'
);


ALTER FOREIGN TABLE public.entities OWNER TO postgres;

--
-- Name: positionhistory; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.positionhistory (
    i_ph integer NOT NULL,
    x_id_dev character varying(200) NOT NULL,
    d_pos_bgn timestamp without time zone NOT NULL,
    d_pos_end timestamp without time zone NOT NULL,
    n_x real NOT NULL,
    n_y real NOT NULL,
    n_z real NOT NULL
);


ALTER TABLE public.positionhistory OWNER TO postgres;

--
-- Name: positionhistory_i_ph_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.positionhistory_i_ph_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.positionhistory_i_ph_seq OWNER TO postgres;

--
-- Name: positionhistory_i_ph_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.positionhistory_i_ph_seq OWNED BY public.positionhistory.i_ph;


--
-- Name: dtproperties id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dtproperties ALTER COLUMN id SET DEFAULT nextval('public.dtproperties_id_seq'::regclass);


--
-- Name: positionhistory i_ph; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.positionhistory ALTER COLUMN i_ph SET DEFAULT nextval('public.positionhistory_i_ph_seq'::regclass);


--
-- Data for Name: devices; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.devices (x_id_dev, i_typ_dev, x_nm_dev, d_srv_bgn, d_srv_end, n_moe_x, n_moe_y, n_moe_z, f_log) FROM stdin;
Device001	1	Test Device 1	2025-02-06 10:00:00	2025-02-06 12:00:00	1.1	2.2	3.3	t
1	1	Device 1	2025-02-06 05:20:14.912944	\N	\N	\N	\N	f
DEV001	1	Device 001	2025-02-06 00:06:20.448498	2025-02-07 12:00:00	\N	\N	\N	f
NewInsertDevice	0	Placeholder Device	2025-02-09 06:41:15.878224	\N	\N	\N	\N	f
DeviceKeep	0	Placeholder Device	2025-02-09 06:41:15.878224	\N	\N	\N	\N	f
DeviceToDelete	0	Placeholder Device	2025-02-09 06:41:15.878224	\N	\N	\N	\N	f
\.


--
-- Data for Name: dtproperties; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dtproperties (id, objectid, property, value, uvalue, lvalue, version) FROM stdin;
1	4	DtgDSRefDATA	\N	\N	\\x0db6e80e9c1b10d11ad5100ac90f5739000002050153d0	0
\.


--
-- Data for Name: positionhistory; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.positionhistory (i_ph, x_id_dev, d_pos_bgn, d_pos_end, n_x, n_y, n_z) FROM stdin;
3	DeviceToDelete	2025-02-06 12:00:00	2025-02-06 12:10:00	1.1	2.2	3.3
4	DeviceKeep	2025-02-06 12:15:00	2025-02-06 12:25:00	4.4	5.5	6.6
5	NewInsertDevice	2025-02-06 14:00:00	2025-02-06 15:00:00	7	8	9
\.


--
-- Name: dtproperties_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dtproperties_id_seq', 1, true);


--
-- Name: positionhistory_i_ph_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.positionhistory_i_ph_seq', 5, true);


--
-- Name: dtproperties dtproperties_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dtproperties
    ADD CONSTRAINT dtproperties_pkey PRIMARY KEY (id);


--
-- Name: devices local_devices_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT local_devices_pkey PRIMARY KEY (x_id_dev);


--
-- Name: positionhistory positionhistory_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.positionhistory
    ADD CONSTRAINT positionhistory_pkey PRIMARY KEY (i_ph);


--
-- Name: positionhistory fk_positionhistory_devices; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.positionhistory
    ADD CONSTRAINT fk_positionhistory_devices FOREIGN KEY (x_id_dev) REFERENCES public.devices(x_id_dev);


--
-- PostgreSQL database dump complete
--

--
-- Database "ParcoRTLSHistR" dump
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 16.8 (Ubuntu 16.8-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.8 (Ubuntu 16.8-0ubuntu0.24.04.1)

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
-- Name: ParcoRTLSHistR; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE "ParcoRTLSHistR" WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.UTF-8';


ALTER DATABASE "ParcoRTLSHistR" OWNER TO postgres;

\connect "ParcoRTLSHistR"

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
-- Name: usp_delete_all(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_delete_all() RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM PositionHistory;
    RETURN 'All records deleted successfully';
EXCEPTION WHEN OTHERS THEN
    RETURN SQLERRM; -- Return the actual error message if something goes wrong
END;
$$;


ALTER FUNCTION public.usp_delete_all() OWNER TO postgres;

--
-- Name: usp_delete_by_id(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_delete_by_id(p_x_id_dev character varying) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM PositionHistory WHERE X_ID_DEV = p_x_id_dev;
    
    IF FOUND THEN
        RETURN 'Record(s) deleted successfully';
    ELSE
        RETURN 'No records found for deletion';
    END IF;
EXCEPTION WHEN OTHERS THEN
    RETURN SQLERRM; -- Return error if deletion fails
END;
$$;


ALTER FUNCTION public.usp_delete_by_id(p_x_id_dev character varying) OWNER TO postgres;

--
-- Name: usp_history_by_id(character varying, timestamp without time zone, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_history_by_id(p_x_id_dev character varying, p_d_pos_bgn timestamp without time zone, p_d_pos_end timestamp without time zone) RETURNS TABLE(i_ph integer, x_id_dev character varying, d_pos_bgn timestamp without time zone, d_pos_end timestamp without time zone, n_x real, n_y real, n_z real)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        PositionHistory.I_PH,
        PositionHistory.X_ID_DEV,
        PositionHistory.D_POS_BGN,
        PositionHistory.D_POS_END,
        PositionHistory.N_X,
        PositionHistory.N_Y,
        PositionHistory.N_Z
    FROM PositionHistory
    WHERE PositionHistory.X_ID_DEV = p_x_id_dev
      AND PositionHistory.D_POS_BGN >= p_d_pos_bgn
      AND PositionHistory.D_POS_END <= p_d_pos_end;
END;
$$;


ALTER FUNCTION public.usp_history_by_id(p_x_id_dev character varying, p_d_pos_bgn timestamp without time zone, p_d_pos_end timestamp without time zone) OWNER TO postgres;

--
-- Name: usp_history_by_location(real, real, real, real, real, real, timestamp without time zone, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_history_by_location(p_x_min real, p_x_max real, p_y_min real, p_y_max real, p_z_min real, p_z_max real, p_d_pos_bgn timestamp without time zone, p_d_pos_end timestamp without time zone) RETURNS TABLE(i_ph integer, x_id_dev character varying, d_pos_bgn timestamp without time zone, d_pos_end timestamp without time zone, n_x real, n_y real, n_z real)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT
        PositionHistory.I_PH,
        PositionHistory.X_ID_DEV,
        PositionHistory.D_POS_BGN,
        PositionHistory.D_POS_END,
        PositionHistory.N_X,
        PositionHistory.N_Y,
        PositionHistory.N_Z
    FROM PositionHistory
    WHERE PositionHistory.N_X BETWEEN p_x_min AND p_x_max
      AND PositionHistory.N_Y BETWEEN p_y_min AND p_y_max
      AND PositionHistory.N_Z BETWEEN p_z_min AND p_z_max
      AND PositionHistory.D_POS_BGN >= p_d_pos_bgn
      AND PositionHistory.D_POS_END <= p_d_pos_end;
END;
$$;


ALTER FUNCTION public.usp_history_by_location(p_x_min real, p_x_max real, p_y_min real, p_y_max real, p_z_min real, p_z_max real, p_d_pos_bgn timestamp without time zone, p_d_pos_end timestamp without time zone) OWNER TO postgres;

--
-- Name: usp_location_by_id(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_location_by_id(p_x_id_dev character varying) RETURNS TABLE(i_ph integer, x_id_dev character varying, d_pos_bgn timestamp without time zone, d_pos_end timestamp without time zone, n_x real, n_y real, n_z real)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT
        PositionHistory.I_PH,
        PositionHistory.X_ID_DEV,
        PositionHistory.D_POS_BGN,
        PositionHistory.D_POS_END,
        PositionHistory.N_X,
        PositionHistory.N_Y,
        PositionHistory.N_Z
    FROM PositionHistory
    WHERE PositionHistory.X_ID_DEV = p_x_id_dev;
END;
$$;


ALTER FUNCTION public.usp_location_by_id(p_x_id_dev character varying) OWNER TO postgres;

--
-- Name: usp_position_insert(character varying, timestamp without time zone, timestamp without time zone, real, real, real); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_position_insert(p_x_id_dev character varying, p_d_pos_bgn timestamp without time zone, p_d_pos_end timestamp without time zone, p_n_x real, p_n_y real, p_n_z real) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_i_ph INTEGER;
BEGIN
    INSERT INTO PositionHistory (X_ID_DEV, D_POS_BGN, D_POS_END, N_X, N_Y, N_Z)
    VALUES (p_x_id_dev, p_d_pos_bgn, p_d_pos_end, p_n_x, p_n_y, p_n_z)
    RETURNING I_PH INTO v_i_ph;

    RETURN v_i_ph;  -- Return the ID of the inserted record
EXCEPTION WHEN OTHERS THEN
    RETURN -1;  -- Return -1 in case of an error
END;
$$;


ALTER FUNCTION public.usp_position_insert(p_x_id_dev character varying, p_d_pos_bgn timestamp without time zone, p_d_pos_end timestamp without time zone, p_n_x real, p_n_y real, p_n_z real) OWNER TO postgres;

--
-- Name: usp_position_update(integer, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_position_update(p_i_ph integer, p_d_pos_end timestamp without time zone) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE PositionHistory
    SET D_POS_END = p_d_pos_end
    WHERE I_PH = p_i_ph;

    IF FOUND THEN
        RETURN 'Record updated successfully';
    ELSE
        RETURN 'No record found to update';
    END IF;
EXCEPTION WHEN OTHERS THEN
    RETURN SQLERRM;  -- Return the error message if something goes wrong
END;
$$;


ALTER FUNCTION public.usp_position_update(p_i_ph integer, p_d_pos_end timestamp without time zone) OWNER TO postgres;

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
-- Name: USER MAPPING postgres SERVER parcortlsmaint_server; Type: USER MAPPING; Schema: -; Owner: postgres
--

CREATE USER MAPPING FOR postgres SERVER parcortlsmaint_server OPTIONS (
    password 'parcoMCSE04106!',
    "user" 'postgres'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: devices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.devices (
    x_id_dev character varying(200) NOT NULL,
    i_typ_dev integer,
    x_nm_dev character varying(200),
    d_srv_bgn timestamp without time zone,
    d_srv_end timestamp without time zone,
    n_moe_x real,
    n_moe_y real,
    n_moe_z real,
    f_log boolean
);


ALTER TABLE public.devices OWNER TO postgres;

--
-- Name: entities; Type: FOREIGN TABLE; Schema: public; Owner: postgres
--

CREATE FOREIGN TABLE public.entities (
    x_id_ent character varying(200) NOT NULL,
    i_typ_ent integer,
    x_nm_ent character varying(200),
    d_crt timestamp without time zone,
    d_udt timestamp without time zone
)
SERVER parcortlsmaint_server
OPTIONS (
    schema_name 'public',
    table_name 'entities'
);
ALTER FOREIGN TABLE public.entities ALTER COLUMN x_id_ent OPTIONS (
    column_name 'x_id_ent'
);
ALTER FOREIGN TABLE public.entities ALTER COLUMN i_typ_ent OPTIONS (
    column_name 'i_typ_ent'
);
ALTER FOREIGN TABLE public.entities ALTER COLUMN x_nm_ent OPTIONS (
    column_name 'x_nm_ent'
);
ALTER FOREIGN TABLE public.entities ALTER COLUMN d_crt OPTIONS (
    column_name 'd_crt'
);
ALTER FOREIGN TABLE public.entities ALTER COLUMN d_udt OPTIONS (
    column_name 'd_udt'
);


ALTER FOREIGN TABLE public.entities OWNER TO postgres;

--
-- Name: positionhistory; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.positionhistory (
    i_ph integer NOT NULL,
    x_id_dev character varying(200) NOT NULL,
    d_pos_bgn timestamp without time zone NOT NULL,
    d_pos_end timestamp without time zone NOT NULL,
    n_x real NOT NULL,
    n_y real NOT NULL,
    n_z real NOT NULL
);


ALTER TABLE public.positionhistory OWNER TO postgres;

--
-- Name: positionhistory_i_ph_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.positionhistory_i_ph_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.positionhistory_i_ph_seq OWNER TO postgres;

--
-- Name: positionhistory_i_ph_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.positionhistory_i_ph_seq OWNED BY public.positionhistory.i_ph;


--
-- Name: positionhistory i_ph; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.positionhistory ALTER COLUMN i_ph SET DEFAULT nextval('public.positionhistory_i_ph_seq'::regclass);


--
-- Data for Name: devices; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.devices (x_id_dev, i_typ_dev, x_nm_dev, d_srv_bgn, d_srv_end, n_moe_x, n_moe_y, n_moe_z, f_log) FROM stdin;
Device001	1	Test Device 1	2025-02-06 10:00:00	2025-02-06 12:00:00	1.1	2.2	3.3	t
1	1	Device 1	2025-02-06 05:20:14.912944	\N	\N	\N	\N	f
DEV001	1	Device 001	2025-02-06 00:06:20.448498	2025-02-07 12:00:00	\N	\N	\N	f
DeviceTest	0	Placeholder Device	2025-02-09 06:44:39.463367	\N	\N	\N	\N	f
OtherDevice	0	Placeholder Device	2025-02-09 06:44:39.463367	\N	\N	\N	\N	f
NewDeviceTest	0	Placeholder Device	2025-02-09 06:44:39.463367	\N	\N	\N	\N	f
DeviceTest2	0	Placeholder Device	2025-02-09 06:44:39.463367	\N	\N	\N	\N	f
\.


--
-- Data for Name: positionhistory; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.positionhistory (i_ph, x_id_dev, d_pos_bgn, d_pos_end, n_x, n_y, n_z) FROM stdin;
4	DeviceTest2	2025-02-06 12:15:00	2025-02-06 12:25:00	4.4	5.5	6.6
5	DeviceTest	2025-02-06 12:00:00	2025-02-06 12:10:00	1.1	2.2	3.3
6	DeviceTest	2025-02-06 12:15:00	2025-02-06 12:25:00	4.4	5.5	6.6
7	OtherDevice	2025-02-06 12:20:00	2025-02-06 12:30:00	7.7	8.8	9.9
8	DeviceTest	2025-02-06 12:00:00	2025-02-06 12:10:00	4	5	6
9	DeviceTest2	2025-02-06 12:15:00	2025-02-06 12:25:00	7	8	9
10	NewDeviceTest	2025-02-06 14:00:00	2025-02-06 15:00:00	7	8	9
11	1	2025-03-05 04:45:21.824805	2025-03-05 04:45:21.824813	0	0	0
12	1	2025-03-05 04:52:21.548376	2025-03-05 04:52:21.548387	0	0	0
13	1	2025-03-05 05:01:22.357849	2025-03-05 05:01:22.357858	0	0	0
14	1	2025-03-05 05:12:53.497971	2025-03-05 05:12:53.497982	0	0	0
15	1	2025-03-05 05:17:41.936101	2025-03-05 05:17:41.93611	0	0	0
16	1	2025-03-05 05:35:19.255627	2025-03-05 05:35:19.255635	0	0	0
17	1	2025-03-05 05:41:17.111779	2025-03-05 05:41:17.111787	0	0	0
18	1	2025-03-05 05:45:38.704448	2025-03-05 05:45:38.704456	0	0	0
\.


--
-- Name: positionhistory_i_ph_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.positionhistory_i_ph_seq', 18, true);


--
-- Name: devices local_devices_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT local_devices_pkey PRIMARY KEY (x_id_dev);


--
-- Name: positionhistory positionhistory_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.positionhistory
    ADD CONSTRAINT positionhistory_pkey PRIMARY KEY (i_ph);


--
-- Name: positionhistory fk_positionhistory_devices; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.positionhistory
    ADD CONSTRAINT fk_positionhistory_devices FOREIGN KEY (x_id_dev) REFERENCES public.devices(x_id_dev);


--
-- PostgreSQL database dump complete
--

--
-- Database "ParcoRTLSMaint" dump
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 16.8 (Ubuntu 16.8-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.8 (Ubuntu 16.8-0ubuntu0.24.04.1)

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
-- Name: ParcoRTLSMaint; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE "ParcoRTLSMaint" WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.UTF-8';


ALTER DATABASE "ParcoRTLSMaint" OWNER TO postgres;

\connect "ParcoRTLSMaint"

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
-- Name: usp_assign_dev_add(integer, integer, integer, timestamp without time zone, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_assign_dev_add(p_device_id integer, p_entity_id integer, p_reason_id integer, p_start_date timestamp without time zone, p_end_date timestamp without time zone DEFAULT NULL::timestamp without time zone) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO deviceassmts (
        device_id,
        entity_id,
        reason_id,
        start_date,
        end_date
    )
    VALUES (
        p_device_id,
        p_entity_id,
        p_reason_id,
        p_start_date,
        p_end_date
    );

    RETURN 'Assignment added successfully';
EXCEPTION
    WHEN OTHERS THEN
        RETURN SQLERRM;
END;
$$;


ALTER FUNCTION public.usp_assign_dev_add(p_device_id integer, p_entity_id integer, p_reason_id integer, p_start_date timestamp without time zone, p_end_date timestamp without time zone) OWNER TO postgres;

--
-- Name: usp_assign_dev_add(character varying, character varying, integer, timestamp without time zone, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_assign_dev_add(p_device_id character varying, p_entity_id character varying, p_reason_id integer, p_start_date timestamp without time zone, p_end_date timestamp without time zone DEFAULT NULL::timestamp without time zone) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO deviceassmts (
        x_id_dev,
        x_id_ent,
        i_rsn,
        d_asn_bgn,
        d_asn_end
    )
    VALUES (
        p_device_id,
        p_entity_id,
        p_reason_id,
        p_start_date,
        p_end_date
    );

    RETURN 'Assignment added successfully';
EXCEPTION
    WHEN OTHERS THEN
        RETURN SQLERRM;
END;
$$;


ALTER FUNCTION public.usp_assign_dev_add(p_device_id character varying, p_entity_id character varying, p_reason_id integer, p_start_date timestamp without time zone, p_end_date timestamp without time zone) OWNER TO postgres;

--
-- Name: usp_assign_dev_delete(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_assign_dev_delete(p_asn_dev integer) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE deviceassmts
    SET d_asn_end = NOW()
    WHERE i_asn_dev = p_asn_dev;

    IF FOUND THEN
        RETURN 'Assignment end date updated successfully';
    ELSE
        RETURN 'No matching record found';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RETURN SQLERRM;
END;
$$;


ALTER FUNCTION public.usp_assign_dev_delete(p_asn_dev integer) OWNER TO postgres;

--
-- Name: usp_assign_dev_delete_all(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_assign_dev_delete_all() RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE deviceassmts
    SET d_asn_end = NOW()
    WHERE d_asn_end IS NULL;

    IF FOUND THEN
        RETURN 'All assignment end dates updated successfully';
    ELSE
        RETURN 'No open assignments found';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RETURN SQLERRM;
END;
$$;


ALTER FUNCTION public.usp_assign_dev_delete_all() OWNER TO postgres;

--
-- Name: usp_assign_dev_delete_all_by_ent(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_assign_dev_delete_all_by_ent(p_entity_id character varying) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM deviceassmts
    WHERE x_id_ent = p_entity_id;

    IF FOUND THEN
        RETURN 'All assignments for the entity deleted successfully';
    ELSE
        RETURN 'No assignments found for the entity';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RETURN SQLERRM;
END;
$$;


ALTER FUNCTION public.usp_assign_dev_delete_all_by_ent(p_entity_id character varying) OWNER TO postgres;

--
-- Name: usp_assign_dev_edit(integer, character varying, character varying, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_assign_dev_edit(p_asn_dev integer, p_device_id character varying, p_entity_id character varying, p_reason_id integer) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE deviceassmts
    SET 
        x_id_dev = p_device_id,
        x_id_ent = p_entity_id,
        i_rsn = p_reason_id
    WHERE i_asn_dev = p_asn_dev;

    IF FOUND THEN
        RETURN 'Assignment updated successfully';
    ELSE
        RETURN 'No matching assignment found';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RETURN SQLERRM;
END;
$$;


ALTER FUNCTION public.usp_assign_dev_edit(p_asn_dev integer, p_device_id character varying, p_entity_id character varying, p_reason_id integer) OWNER TO postgres;

--
-- Name: usp_assign_dev_end(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_assign_dev_end(p_asn_dev integer) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE deviceassmts
    SET d_asn_end = NOW()
    WHERE i_asn_dev = p_asn_dev AND d_asn_end IS NULL;

    IF FOUND THEN
        RETURN 'Assignment ended successfully';
    ELSE
        RETURN 'No open assignment found for the given ID';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RETURN SQLERRM;
END;
$$;


ALTER FUNCTION public.usp_assign_dev_end(p_asn_dev integer) OWNER TO postgres;

--
-- Name: usp_assign_dev_end_all(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_assign_dev_end_all() RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE deviceassmts
    SET d_asn_end = NOW()
    WHERE d_asn_end IS NULL;

    IF FOUND THEN
        RETURN 'All open assignments ended successfully';
    ELSE
        RETURN 'No open assignments found';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RETURN SQLERRM;
END;
$$;


ALTER FUNCTION public.usp_assign_dev_end_all() OWNER TO postgres;

--
-- Name: usp_assign_dev_list(boolean); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_assign_dev_list(p_f_end boolean) RETURNS TABLE(i_asn_dev integer, x_id_dev character varying, x_id_ent character varying, d_asn_bgn timestamp without time zone, d_asn_end timestamp without time zone, i_rsn integer, x_rsn character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF p_f_end THEN
        RETURN QUERY
        SELECT 
            d.i_asn_dev, 
            d.x_id_dev, 
            d.x_id_ent, 
            d.d_asn_bgn, 
            d.d_asn_end, 
            d.i_rsn, 
            r.x_rsn
        FROM 
            deviceassmts d
        LEFT JOIN 
            tlkassmtreasons r ON d.i_rsn = r.i_rsn;
    ELSE
        RETURN QUERY
        SELECT 
            d.i_asn_dev, 
            d.x_id_dev, 
            d.x_id_ent, 
            d.d_asn_bgn, 
            d.d_asn_end, 
            d.i_rsn, 
            r.x_rsn
        FROM 
            deviceassmts d
        LEFT JOIN 
            tlkassmtreasons r ON d.i_rsn = r.i_rsn
        WHERE 
            d.d_asn_end IS NULL;
    END IF;
END;
$$;


ALTER FUNCTION public.usp_assign_dev_list(p_f_end boolean) OWNER TO postgres;

--
-- Name: usp_assign_dev_list_by_entity(character varying, boolean); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_assign_dev_list_by_entity(p_entity_id character varying, p_f_end boolean) RETURNS TABLE(i_asn_dev integer, x_id_dev character varying, x_id_ent character varying, d_asn_bgn timestamp without time zone, d_asn_end timestamp without time zone, i_rsn integer, x_rsn character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF p_f_end THEN
        -- Include all assignments, even those with an end date
        RETURN QUERY
        SELECT
            d.i_asn_dev,
            d.x_id_dev,
            d.x_id_ent,
            d.d_asn_bgn,
            d.d_asn_end,
            d.i_rsn,
            r.x_rsn
        FROM
            deviceassmts d
        LEFT JOIN
            tlkassmtreasons r ON d.i_rsn = r.i_rsn
        WHERE
            d.x_id_ent = p_entity_id;
    ELSE
        -- Only include assignments that have not ended
        RETURN QUERY
        SELECT
            d.i_asn_dev,
            d.x_id_dev,
            d.x_id_ent,
            d.d_asn_bgn,
            d.d_asn_end,
            d.i_rsn,
            r.x_rsn
        FROM
            deviceassmts d
        LEFT JOIN
            tlkassmtreasons r ON d.i_rsn = r.i_rsn
        WHERE
            d.x_id_ent = p_entity_id AND d.d_asn_end IS NULL;
    END IF;
END;
$$;


ALTER FUNCTION public.usp_assign_dev_list_by_entity(p_entity_id character varying, p_f_end boolean) OWNER TO postgres;

--
-- Name: usp_assign_dev_list_by_id(character varying, boolean); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_assign_dev_list_by_id(p_device_id character varying, p_f_end boolean) RETURNS TABLE(i_asn_dev integer, x_id_dev character varying, x_id_ent character varying, d_asn_bgn timestamp without time zone, d_asn_end timestamp without time zone, i_rsn integer, x_rsn character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF p_f_end THEN
        -- Include all assignments for the given device, even those with an end date
        RETURN QUERY
        SELECT
            d.i_asn_dev,
            d.x_id_dev,
            d.x_id_ent,
            d.d_asn_bgn,
            d.d_asn_end,
            d.i_rsn,
            r.x_rsn
        FROM
            deviceassmts d
        LEFT JOIN
            tlkassmtreasons r ON d.i_rsn = r.i_rsn
        WHERE
            d.x_id_dev = p_device_id;
    ELSE
        -- Only include assignments that have not ended
        RETURN QUERY
        SELECT
            d.i_asn_dev,
            d.x_id_dev,
            d.x_id_ent,
            d.d_asn_bgn,
            d.d_asn_end,
            d.i_rsn,
            r.x_rsn
        FROM
            deviceassmts d
        LEFT JOIN
            tlkassmtreasons r ON d.i_rsn = r.i_rsn
        WHERE
            d.x_id_dev = p_device_id AND d.d_asn_end IS NULL;
    END IF;
END;
$$;


ALTER FUNCTION public.usp_assign_dev_list_by_id(p_device_id character varying, p_f_end boolean) OWNER TO postgres;

--
-- Name: usp_assign_dev_list_by_reason(integer, boolean); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_assign_dev_list_by_reason(p_reason_id integer, p_f_end boolean) RETURNS TABLE(i_asn_dev integer, x_id_dev character varying, x_id_ent character varying, d_asn_bgn timestamp without time zone, d_asn_end timestamp without time zone, i_rsn integer, x_rsn character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF p_f_end THEN
        -- Include all assignments with the specified reason, even those with an end date
        RETURN QUERY
        SELECT
            d.i_asn_dev,
            d.x_id_dev,
            d.x_id_ent,
            d.d_asn_bgn,
            d.d_asn_end,
            d.i_rsn,
            r.x_rsn
        FROM
            deviceassmts d
        LEFT JOIN
            tlkassmtreasons r ON d.i_rsn = r.i_rsn
        WHERE
            d.i_rsn = p_reason_id;
    ELSE
        -- Only include active assignments with the specified reason
        RETURN QUERY
        SELECT
            d.i_asn_dev,
            d.x_id_dev,
            d.x_id_ent,
            d.d_asn_bgn,
            d.d_asn_end,
            d.i_rsn,
            r.x_rsn
        FROM
            deviceassmts d
        LEFT JOIN
            tlkassmtreasons r ON d.i_rsn = r.i_rsn
        WHERE
            d.i_rsn = p_reason_id AND d.d_asn_end IS NULL;
    END IF;
END;
$$;


ALTER FUNCTION public.usp_assign_dev_list_by_reason(p_reason_id integer, p_f_end boolean) OWNER TO postgres;

--
-- Name: usp_assign_entity_add(character varying, character varying, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_assign_entity_add(p_x_id_pnt character varying, p_x_id_chd character varying, p_i_rsn integer) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_i_asn_ent INTEGER;
BEGIN
    IF p_i_rsn = -1 THEN
        INSERT INTO entityassmts (x_id_pnt, x_id_chd, d_ent_asn_bgn)
        VALUES (p_x_id_pnt, p_x_id_chd, NOW())
        RETURNING i_asn_ent INTO v_i_asn_ent;
    ELSE
        INSERT INTO entityassmts (x_id_pnt, x_id_chd, i_rsn, d_ent_asn_bgn)
        VALUES (p_x_id_pnt, p_x_id_chd, p_i_rsn, NOW())
        RETURNING i_asn_ent INTO v_i_asn_ent;
    END IF;

    RETURN v_i_asn_ent;

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error: %', SQLERRM;
        RETURN -1;
END;
$$;


ALTER FUNCTION public.usp_assign_entity_add(p_x_id_pnt character varying, p_x_id_chd character varying, p_i_rsn integer) OWNER TO postgres;

--
-- Name: usp_assign_entity_delete(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_assign_entity_delete(p_i_asn_ent integer) RETURNS integer
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM entityassmts
    WHERE i_asn_ent = p_i_asn_ent;

    IF FOUND THEN
        RETURN 0;  -- Success
    ELSE
        RETURN 1;  -- No matching record found
    END IF;

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error: %', SQLERRM;
        RETURN -1;  -- Error occurred
END;
$$;


ALTER FUNCTION public.usp_assign_entity_delete(p_i_asn_ent integer) OWNER TO postgres;

--
-- Name: usp_assign_entity_delete_all(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_assign_entity_delete_all(p_x_id_ent character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM entityassmts
    WHERE x_id_pnt = p_x_id_ent OR x_id_chd = p_x_id_ent;

    IF FOUND THEN
        RETURN 0;  -- Success
    ELSE
        RETURN 1;  -- No records found
    END IF;

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error: %', SQLERRM;
        RETURN -1;  -- Error occurred
END;
$$;


ALTER FUNCTION public.usp_assign_entity_delete_all(p_x_id_ent character varying) OWNER TO postgres;

--
-- Name: usp_assign_entity_edit(integer, character varying, character varying, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_assign_entity_edit(p_i_asn_ent integer, p_x_id_pnt character varying, p_x_id_chd character varying, p_i_rsn integer) RETURNS integer
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF p_i_rsn = -1 THEN
        UPDATE entityassmts
        SET 
            x_id_pnt = p_x_id_pnt,
            x_id_chd = p_x_id_chd,
            i_rsn = NULL
        WHERE i_asn_ent = p_i_asn_ent;
    ELSE
        UPDATE entityassmts
        SET 
            x_id_pnt = p_x_id_pnt,
            x_id_chd = p_x_id_chd,
            i_rsn = p_i_rsn
        WHERE i_asn_ent = p_i_asn_ent;
    END IF;

    IF FOUND THEN
        RETURN 0;  -- Success
    ELSE
        RETURN 1;  -- No matching record found
    END IF;

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error: %', SQLERRM;
        RETURN -1;  -- Error occurred
END;
$$;


ALTER FUNCTION public.usp_assign_entity_edit(p_i_asn_ent integer, p_x_id_pnt character varying, p_x_id_chd character varying, p_i_rsn integer) OWNER TO postgres;

--
-- Name: usp_assign_entity_end(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_assign_entity_end(p_i_asn_ent integer) RETURNS integer
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE entityassmts
    SET d_ent_asn_end = NOW()
    WHERE i_asn_ent = p_i_asn_ent;

    IF FOUND THEN
        RETURN 0;  -- Success
    ELSE
        RETURN 1;  -- No matching record found
    END IF;

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error: %', SQLERRM;
        RETURN -1;  -- Error occurred
END;
$$;


ALTER FUNCTION public.usp_assign_entity_end(p_i_asn_ent integer) OWNER TO postgres;

--
-- Name: usp_assign_entity_end_all(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_assign_entity_end_all(p_x_id_ent character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE entityassmts
    SET d_ent_asn_end = NOW()
    WHERE x_id_pnt = p_x_id_ent OR x_id_chd = p_x_id_ent;

    IF FOUND THEN
        RETURN 0;  -- Success: Assignments ended for specified entity
    ELSE
        RETURN 1;  -- No matching assignments found
    END IF;

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error: %', SQLERRM;
        RETURN -1;  -- Error occurred
END;
$$;


ALTER FUNCTION public.usp_assign_entity_end_all(p_x_id_ent character varying) OWNER TO postgres;

--
-- Name: usp_assign_entity_list(boolean); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_assign_entity_list(p_f_end boolean) RETURNS TABLE(i_asn_ent integer, x_id_pnt character varying, x_id_chd character varying, d_ent_asn_bgn timestamp without time zone, d_ent_asn_end timestamp without time zone, i_rsn integer, x_rsn character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF p_f_end THEN
        RETURN QUERY
        SELECT
            e.i_asn_ent,
            e.x_id_pnt,
            e.x_id_chd,
            e.d_ent_asn_bgn,
            e.d_ent_asn_end,
            e.i_rsn,
            r.x_rsn
        FROM
            entityassmts e
        LEFT JOIN
            tlkassmtreasons r ON e.i_rsn = r.i_rsn;
    ELSE
        RETURN QUERY
        SELECT
            e.i_asn_ent,
            e.x_id_pnt,
            e.x_id_chd,
            e.d_ent_asn_bgn,
            e.d_ent_asn_end,
            e.i_rsn,
            r.x_rsn
        FROM
            entityassmts e
        LEFT JOIN
            tlkassmtreasons r ON e.i_rsn = r.i_rsn
        WHERE
            e.d_ent_asn_end IS NULL;
    END IF;
END;
$$;


ALTER FUNCTION public.usp_assign_entity_list(p_f_end boolean) OWNER TO postgres;

--
-- Name: usp_assign_entity_list_by_child(character varying, boolean); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_assign_entity_list_by_child(p_x_id_chd character varying, p_f_end boolean) RETURNS TABLE(i_asn_ent integer, x_id_pnt character varying, x_id_chd character varying, d_ent_asn_bgn timestamp without time zone, d_ent_asn_end timestamp without time zone, i_rsn integer, x_rsn character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF p_f_end THEN
        -- Retrieve all assignments for the specified child entity
        RETURN QUERY
        SELECT
            e.i_asn_ent,
            e.x_id_pnt,
            e.x_id_chd,
            e.d_ent_asn_bgn,
            e.d_ent_asn_end,
            e.i_rsn,
            r.x_rsn
        FROM
            entityassmts e
        LEFT JOIN
            tlkassmtreasons r ON e.i_rsn = r.i_rsn
        WHERE
            e.x_id_chd = p_x_id_chd;
    ELSE
        -- Retrieve only active assignments (those without an end date)
        RETURN QUERY
        SELECT
            e.i_asn_ent,
            e.x_id_pnt,
            e.x_id_chd,
            e.d_ent_asn_bgn,
            e.d_ent_asn_end,
            e.i_rsn,
            r.x_rsn
        FROM
            entityassmts e
        LEFT JOIN
            tlkassmtreasons r ON e.i_rsn = r.i_rsn
        WHERE
            e.x_id_chd = p_x_id_chd
            AND e.d_ent_asn_end IS NULL;
    END IF;
END;
$$;


ALTER FUNCTION public.usp_assign_entity_list_by_child(p_x_id_chd character varying, p_f_end boolean) OWNER TO postgres;

--
-- Name: usp_assign_entity_list_by_id(character varying, boolean); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_assign_entity_list_by_id(p_x_id_ent character varying, p_f_end boolean) RETURNS TABLE(i_asn_ent integer, x_id_pnt character varying, x_id_chd character varying, d_ent_asn_bgn timestamp without time zone, d_ent_asn_end timestamp without time zone, i_rsn integer, x_rsn character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF p_f_end THEN
        RETURN QUERY
        SELECT
            e.i_asn_ent,
            e.x_id_pnt,
            e.x_id_chd,
            e.d_ent_asn_bgn,
            e.d_ent_asn_end,
            e.i_rsn,
            r.x_rsn
        FROM
            entityassmts e
        LEFT JOIN
            tlkassmtreasons r ON e.i_rsn = r.i_rsn
        WHERE
            e.x_id_pnt = p_x_id_ent OR e.x_id_chd = p_x_id_ent;
    ELSE
        RETURN QUERY
        SELECT
            e.i_asn_ent,
            e.x_id_pnt,
            e.x_id_chd,
            e.d_ent_asn_bgn,
            e.d_ent_asn_end,
            e.i_rsn,
            r.x_rsn
        FROM
            entityassmts e
        LEFT JOIN
            tlkassmtreasons r ON e.i_rsn = r.i_rsn
        WHERE
            (e.x_id_pnt = p_x_id_ent OR e.x_id_chd = p_x_id_ent)
            AND e.d_ent_asn_end IS NULL;
    END IF;
END;
$$;


ALTER FUNCTION public.usp_assign_entity_list_by_id(p_x_id_ent character varying, p_f_end boolean) OWNER TO postgres;

--
-- Name: usp_assign_entity_list_by_key(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_assign_entity_list_by_key(p_i_asn_ent integer) RETURNS TABLE(i_asn_ent integer, x_id_pnt character varying, x_id_chd character varying, d_ent_asn_bgn timestamp without time zone, d_ent_asn_end timestamp without time zone, i_rsn integer, x_rsn character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.i_asn_ent,
        e.x_id_pnt,
        e.x_id_chd,
        e.d_ent_asn_bgn,
        e.d_ent_asn_end,
        e.i_rsn,
        r.x_rsn
    FROM
        entityassmts e
    LEFT JOIN
        tlkassmtreasons r ON e.i_rsn = r.i_rsn
    WHERE
        e.i_asn_ent = p_i_asn_ent;
END;
$$;


ALTER FUNCTION public.usp_assign_entity_list_by_key(p_i_asn_ent integer) OWNER TO postgres;

--
-- Name: usp_assign_entity_list_by_parent(character varying, boolean); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_assign_entity_list_by_parent(p_x_id_pnt character varying, p_f_end boolean) RETURNS TABLE(i_asn_ent integer, x_id_pnt character varying, x_id_chd character varying, d_ent_asn_bgn timestamp without time zone, d_ent_asn_end timestamp without time zone, i_rsn integer, x_rsn character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF p_f_end THEN
        -- Retrieve all assignments for the specified parent entity
        RETURN QUERY
        SELECT
            e.i_asn_ent,
            e.x_id_pnt,
            e.x_id_chd,
            e.d_ent_asn_bgn,
            e.d_ent_asn_end,
            e.i_rsn,
            r.x_rsn
        FROM
            entityassmts e
        LEFT JOIN
            tlkassmtreasons r ON e.i_rsn = r.i_rsn
        WHERE
            e.x_id_pnt = p_x_id_pnt;
    ELSE
        -- Retrieve only active assignments (those without an end date)
        RETURN QUERY
        SELECT
            e.i_asn_ent,
            e.x_id_pnt,
            e.x_id_chd,
            e.d_ent_asn_bgn,
            e.d_ent_asn_end,
            e.i_rsn,
            r.x_rsn
        FROM
            entityassmts e
        LEFT JOIN
            tlkassmtreasons r ON e.i_rsn = r.i_rsn
        WHERE
            e.x_id_pnt = p_x_id_pnt
            AND e.d_ent_asn_end IS NULL;
    END IF;
END;
$$;


ALTER FUNCTION public.usp_assign_entity_list_by_parent(p_x_id_pnt character varying, p_f_end boolean) OWNER TO postgres;

--
-- Name: usp_assign_entity_list_by_reason(integer, boolean); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_assign_entity_list_by_reason(p_i_rsn integer, p_f_end boolean) RETURNS TABLE(i_asn_ent integer, x_id_pnt character varying, x_id_chd character varying, d_ent_asn_bgn timestamp without time zone, d_ent_asn_end timestamp without time zone, i_rsn integer, x_rsn character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF p_f_end THEN
        RETURN QUERY
        SELECT
            e.i_asn_ent,
            e.x_id_pnt,
            e.x_id_chd,
            e.d_ent_asn_bgn,
            e.d_ent_asn_end,
            e.i_rsn,
            r.x_rsn
        FROM
            entityassmts e
        LEFT JOIN
            tlkassmtreasons r ON e.i_rsn = r.i_rsn
        WHERE
            e.i_rsn = p_i_rsn;
    ELSE
        RETURN QUERY
        SELECT
            e.i_asn_ent,
            e.x_id_pnt,
            e.x_id_chd,
            e.d_ent_asn_bgn,
            e.d_ent_asn_end,
            e.i_rsn,
            r.x_rsn
        FROM
            entityassmts e
        LEFT JOIN
            tlkassmtreasons r ON e.i_rsn = r.i_rsn
        WHERE
            e.i_rsn = p_i_rsn
            AND e.d_ent_asn_end IS NULL;
    END IF;
END;
$$;


ALTER FUNCTION public.usp_assign_entity_list_by_reason(p_i_rsn integer, p_f_end boolean) OWNER TO postgres;

--
-- Name: usp_assmt_reason_add(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_assmt_reason_add(p_x_rsn character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_i_rsn INTEGER;
BEGIN
    INSERT INTO tlkassmtreasons (x_rsn)
    VALUES (p_x_rsn)
    RETURNING i_rsn INTO v_i_rsn;

    RETURN v_i_rsn;  -- Return the new ID
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error: %', SQLERRM;
        RETURN -1;  -- Return -1 if an error occurs
END;
$$;


ALTER FUNCTION public.usp_assmt_reason_add(p_x_rsn character varying) OWNER TO postgres;

--
-- Name: usp_assmt_reason_delete(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_assmt_reason_delete(p_i_rsn integer) RETURNS integer
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM tlkassmtreasons
    WHERE i_rsn = p_i_rsn;

    IF FOUND THEN
        RETURN 0;  -- Success
    ELSE
        RETURN 1;  -- No matching record found
    END IF;

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error: %', SQLERRM;
        RETURN -1;  -- Error occurred
END;
$$;


ALTER FUNCTION public.usp_assmt_reason_delete(p_i_rsn integer) OWNER TO postgres;

--
-- Name: usp_assmt_reason_edit(integer, character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_assmt_reason_edit(p_i_rsn integer, p_x_rsn character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE tlkassmtreasons
    SET x_rsn = p_x_rsn
    WHERE i_rsn = p_i_rsn;

    IF FOUND THEN
        RETURN 0;  -- Success
    ELSE
        RETURN 1;  -- No matching record found
    END IF;

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error: %', SQLERRM;
        RETURN -1;  -- Error occurred
END;
$$;


ALTER FUNCTION public.usp_assmt_reason_edit(p_i_rsn integer, p_x_rsn character varying) OWNER TO postgres;

--
-- Name: usp_assmt_reason_list(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_assmt_reason_list() RETURNS TABLE(i_rsn integer, x_rsn character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT tlkassmtreasons.i_rsn, tlkassmtreasons.x_rsn FROM tlkassmtreasons;
END;
$$;


ALTER FUNCTION public.usp_assmt_reason_list() OWNER TO postgres;

--
-- Name: usp_device_add(character varying, integer, character varying, timestamp without time zone, real, real, real); Type: FUNCTION; Schema: public; Owner: parcoadmin
--

CREATE FUNCTION public.usp_device_add(p_x_id_dev character varying, p_i_typ_dev integer, p_x_nm_dev character varying, p_d_srv_bgn timestamp without time zone, p_n_moe_x real DEFAULT NULL::real, p_n_moe_y real DEFAULT NULL::real, p_n_moe_z real DEFAULT NULL::real) RETURNS integer
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO public.devices (
        x_id_dev, i_typ_dev, x_nm_dev, d_srv_bgn, n_moe_x, n_moe_y, n_moe_z, f_log
    ) VALUES (
        p_x_id_dev, p_i_typ_dev, p_x_nm_dev, p_d_srv_bgn, p_n_moe_x, p_n_moe_y, p_n_moe_z, false
    );
    RETURN 1;
EXCEPTION WHEN OTHERS THEN
    RETURN -1;
END;
$$;


ALTER FUNCTION public.usp_device_add(p_x_id_dev character varying, p_i_typ_dev integer, p_x_nm_dev character varying, p_d_srv_bgn timestamp without time zone, p_n_moe_x real, p_n_moe_y real, p_n_moe_z real) OWNER TO parcoadmin;

--
-- Name: usp_device_delete(character varying); Type: FUNCTION; Schema: public; Owner: parcoadmin
--

CREATE FUNCTION public.usp_device_delete(p_x_id_dev character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM public.devices WHERE x_id_dev = p_x_id_dev;
    IF FOUND THEN
        RETURN 1; -- Success: row deleted
    ELSE
        RETURN 0; -- No row found
    END IF;
EXCEPTION WHEN OTHERS THEN
    RETURN -1; -- Error
END;
$$;


ALTER FUNCTION public.usp_device_delete(p_x_id_dev character varying) OWNER TO parcoadmin;

--
-- Name: usp_device_edit(character varying, character varying, real, real, real); Type: FUNCTION; Schema: public; Owner: parcoadmin
--

CREATE FUNCTION public.usp_device_edit(p_x_id_dev character varying, p_x_nm_dev character varying, p_n_moe_x real DEFAULT NULL::real, p_n_moe_y real DEFAULT NULL::real, p_n_moe_z real DEFAULT NULL::real) RETURNS integer
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE public.devices
    SET x_nm_dev = COALESCE(p_x_nm_dev, x_nm_dev),
        n_moe_x = COALESCE(p_n_moe_x, n_moe_x),
        n_moe_y = COALESCE(p_n_moe_y, n_moe_y),
        n_moe_z = COALESCE(p_n_moe_z, n_moe_z)
    WHERE x_id_dev = p_x_id_dev;
    IF FOUND THEN
        RETURN 1;
    ELSE
        RETURN 0;
    END IF;
EXCEPTION WHEN OTHERS THEN
    RETURN -1;
END;
$$;


ALTER FUNCTION public.usp_device_edit(p_x_id_dev character varying, p_x_nm_dev character varying, p_n_moe_x real, p_n_moe_y real, p_n_moe_z real) OWNER TO parcoadmin;

--
-- Name: usp_device_remove_end_date(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_device_remove_end_date(p_x_id_dev character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE devices
    SET d_srv_end = NULL
    WHERE x_id_dev = p_x_id_dev;

    IF FOUND THEN
        RETURN 0;  -- Success
    ELSE
        RETURN 1;  -- No matching record found
    END IF;

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error: %', SQLERRM;
        RETURN -1;  -- Error occurred
END;
$$;


ALTER FUNCTION public.usp_device_remove_end_date(p_x_id_dev character varying) OWNER TO postgres;

--
-- Name: usp_device_select_all(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_device_select_all() RETURNS TABLE(x_id_dev character varying, i_typ_dev integer, x_nm_dev character varying, d_srv_bgn timestamp without time zone, d_srv_end timestamp without time zone, n_moe_x real, n_moe_y real, n_moe_z real, f_log boolean)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT devices.x_id_dev, devices.i_typ_dev, devices.x_nm_dev, 
           devices.d_srv_bgn, devices.d_srv_end, 
           devices.n_moe_x, devices.n_moe_y, devices.n_moe_z, devices.f_log
    FROM devices;
END;
$$;


ALTER FUNCTION public.usp_device_select_all() OWNER TO postgres;

--
-- Name: usp_device_select_by_id(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_device_select_by_id(input_device_id character varying) RETURNS TABLE(x_id_dev character varying, i_typ_dev integer, x_nm_dev character varying, d_srv_bgn timestamp without time zone, d_srv_end timestamp without time zone, n_moe_x real, n_moe_y real, n_moe_z real, f_log boolean)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM public.devices WHERE public.devices.x_id_dev = input_device_id;
END;
$$;


ALTER FUNCTION public.usp_device_select_by_id(input_device_id character varying) OWNER TO postgres;

--
-- Name: usp_device_select_by_type(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_device_select_by_type(p_i_typ_dev integer) RETURNS TABLE(x_id_dev character varying, i_typ_dev integer, x_nm_dev character varying, d_srv_bgn timestamp without time zone, d_srv_end timestamp without time zone, n_moe_x real, n_moe_y real, n_moe_z real, f_log boolean)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT devices.x_id_dev, devices.i_typ_dev, devices.x_nm_dev, 
           devices.d_srv_bgn, devices.d_srv_end, 
           devices.n_moe_x, devices.n_moe_y, devices.n_moe_z, devices.f_log
    FROM devices
    WHERE devices.i_typ_dev = p_i_typ_dev;
END;
$$;


ALTER FUNCTION public.usp_device_select_by_type(p_i_typ_dev integer) OWNER TO postgres;

--
-- Name: usp_device_select_outofservice(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_device_select_outofservice() RETURNS TABLE(x_id_dev character varying, i_typ_dev integer, x_nm_dev character varying, d_srv_bgn timestamp without time zone, d_srv_end timestamp without time zone, n_moe_x real, n_moe_y real, n_moe_z real, f_log boolean)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT devices.x_id_dev, devices.i_typ_dev, devices.x_nm_dev, 
           devices.d_srv_bgn, devices.d_srv_end, 
           devices.n_moe_x, devices.n_moe_y, devices.n_moe_z, devices.f_log
    FROM devices
    WHERE devices.d_srv_end IS NOT NULL;
END;
$$;


ALTER FUNCTION public.usp_device_select_outofservice() OWNER TO postgres;

--
-- Name: usp_device_set_end_date(character varying, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_device_set_end_date(p_x_id_dev character varying, p_d_srv_end timestamp without time zone) RETURNS integer
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE devices
    SET d_srv_end = p_d_srv_end
    WHERE x_id_dev = p_x_id_dev;

    IF FOUND THEN
        RETURN 0;  -- Success
    ELSE
        RETURN 1;  -- No matching record found
    END IF;

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error: %', SQLERRM;
        RETURN -1;  -- Error occurred
END;
$$;


ALTER FUNCTION public.usp_device_set_end_date(p_x_id_dev character varying, p_d_srv_end timestamp without time zone) OWNER TO postgres;

--
-- Name: usp_device_type_add(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_device_type_add(p_x_dsc_dev character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_i_typ_dev INTEGER;
BEGIN
    INSERT INTO tlkdevicetypes (x_dsc_dev)
    VALUES (p_x_dsc_dev)
    RETURNING i_typ_dev INTO v_i_typ_dev;

    RETURN v_i_typ_dev;  -- Return the new ID
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error: %', SQLERRM;
        RETURN -1;  -- Error occurred
END;
$$;


ALTER FUNCTION public.usp_device_type_add(p_x_dsc_dev character varying) OWNER TO postgres;

--
-- Name: usp_device_type_delete(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_device_type_delete(p_i_typ_dev integer) RETURNS integer
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM tlkdevicetypes
    WHERE i_typ_dev = p_i_typ_dev;

    IF FOUND THEN
        RETURN 0;  -- Success
    ELSE
        RETURN 1;  -- No matching record found
    END IF;

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error: %', SQLERRM;
        RETURN -1;  -- Error occurred
END;
$$;


ALTER FUNCTION public.usp_device_type_delete(p_i_typ_dev integer) OWNER TO postgres;

--
-- Name: usp_device_type_edit(integer, character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_device_type_edit(p_i_typ_dev integer, p_x_dsc_dev character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE tlkdevicetypes
    SET x_dsc_dev = p_x_dsc_dev
    WHERE i_typ_dev = p_i_typ_dev;

    IF FOUND THEN
        RETURN 0;  -- Success
    ELSE
        RETURN 1;  -- No matching record found
    END IF;

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error: %', SQLERRM;
        RETURN -1;  -- Error occurred
END;
$$;


ALTER FUNCTION public.usp_device_type_edit(p_i_typ_dev integer, p_x_dsc_dev character varying) OWNER TO postgres;

--
-- Name: usp_device_type_list(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_device_type_list() RETURNS TABLE(i_typ_dev integer, x_dsc_dev character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT tlkdevicetypes.i_typ_dev, tlkdevicetypes.x_dsc_dev
    FROM tlkdevicetypes;
END;
$$;


ALTER FUNCTION public.usp_device_type_list() OWNER TO postgres;

--
-- Name: usp_entity_add(character varying, integer, character varying, timestamp without time zone, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_entity_add(p_x_id_ent character varying, p_i_typ_ent integer, p_x_nm_ent character varying, p_d_crt timestamp without time zone, p_d_udt timestamp without time zone) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    new_entity_id INTEGER;
BEGIN
    -- Insert the entity and return the new ID
    INSERT INTO public.entities (X_ID_ENT, I_TYP_ENT, X_NM_ENT, D_CRT, D_UDT)
    VALUES (p_x_id_ent, p_i_typ_ent, p_x_nm_ent, p_d_crt, p_d_udt)
    RETURNING I_TYP_ENT INTO new_entity_id;

    -- Return the newly created entity ID
    RETURN new_entity_id;
END;
$$;


ALTER FUNCTION public.usp_entity_add(p_x_id_ent character varying, p_i_typ_ent integer, p_x_nm_ent character varying, p_d_crt timestamp without time zone, p_d_udt timestamp without time zone) OWNER TO postgres;

--
-- Name: usp_entity_all(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_entity_all() RETURNS TABLE(x_id_ent character varying, i_typ_ent integer, x_nm_ent character varying, d_crt timestamp without time zone, d_udt timestamp without time zone)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.X_ID_ENT,
        e.I_TYP_ENT,
        e.X_NM_ENT,
        e.D_CRT,
        e.D_UDT
    FROM Entities e;

END;
$$;


ALTER FUNCTION public.usp_entity_all() OWNER TO postgres;

--
-- Name: usp_entity_by_id(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_entity_by_id(p_x_id_ent character varying) RETURNS TABLE(x_id_ent character varying, i_typ_ent integer, x_nm_ent character varying, d_crt timestamp without time zone, d_udt timestamp without time zone)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.X_ID_ENT,
        e.I_TYP_ENT,
        e.X_NM_ENT,
        e.D_CRT,
        e.D_UDT
    FROM Entities e
    WHERE e.X_ID_ENT = p_x_id_ent;

END;
$$;


ALTER FUNCTION public.usp_entity_by_id(p_x_id_ent character varying) OWNER TO postgres;

--
-- Name: usp_entity_by_type(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_entity_by_type(p_i_typ_ent integer) RETURNS TABLE(x_id_ent character varying, i_typ_ent integer, x_nm_ent character varying, d_crt timestamp without time zone, d_udt timestamp without time zone)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.X_ID_ENT,
        e.I_TYP_ENT,
        e.X_NM_ENT,
        e.D_CRT,
        e.D_UDT
    FROM Entities e
    WHERE e.I_TYP_ENT = p_i_typ_ent;
END;
$$;


ALTER FUNCTION public.usp_entity_by_type(p_i_typ_ent integer) OWNER TO postgres;

--
-- Name: usp_entity_delete(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_entity_delete(p_x_id_ent character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    delete_error INTEGER := 0;
BEGIN
    -- Delete the entity
    DELETE FROM public.entities WHERE X_ID_ENT = p_x_id_ent;

    -- Capture error code (0 means success, 1 means failure)
    GET DIAGNOSTICS delete_error = ROW_COUNT;

    -- If no rows were deleted, return 1 (similar to @@ERROR in MSSQL)
    IF delete_error = 0 THEN
        RETURN 1;
    END IF;

    -- Otherwise, return success
    RETURN 0;

END;
$$;


ALTER FUNCTION public.usp_entity_delete(p_x_id_ent character varying) OWNER TO postgres;

--
-- Name: usp_entity_edit(character varying, integer, character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_entity_edit(p_x_id_ent character varying, p_i_typ_ent integer, p_x_nm_ent character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_d_udt TIMESTAMP WITHOUT TIME ZONE := NOW();
    entity_exists INT;
BEGIN
    -- Check if the entity exists
    SELECT COUNT(*) INTO entity_exists FROM public.entities WHERE X_ID_ENT = p_x_id_ent;

    IF entity_exists = 0 THEN
        RAISE EXCEPTION 'Entity ID % not found.', p_x_id_ent;
    END IF;

    -- Update the entity
    UPDATE public.entities
    SET
        I_TYP_ENT = p_i_typ_ent,
        X_NM_ENT = p_x_nm_ent,
        D_UDT = v_d_udt
    WHERE X_ID_ENT = p_x_id_ent;

    -- Return 0 for success
    RETURN 0;
END;
$$;


ALTER FUNCTION public.usp_entity_edit(p_x_id_ent character varying, p_i_typ_ent integer, p_x_nm_ent character varying) OWNER TO postgres;

--
-- Name: usp_entity_type_add(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_entity_type_add(p_x_nm_typ character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_i_typ_ent INTEGER;
BEGIN
    INSERT INTO entitytypes (x_nm_typ)
    VALUES (p_x_nm_typ)
    RETURNING x_id_typ INTO v_i_typ_ent;

    RETURN v_i_typ_ent;  -- Return the new ID
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error: %', SQLERRM;
        RETURN -1;  -- Return -1 if an error occurs
END;
$$;


ALTER FUNCTION public.usp_entity_type_add(p_x_nm_typ character varying) OWNER TO postgres;

--
-- Name: usp_entity_type_add(character varying, character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_entity_type_add(p_x_id_typ character varying, p_x_nm_typ character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO entitytypes (x_id_typ, x_nm_typ, d_crt)
    VALUES (p_x_id_typ, p_x_nm_typ, NOW());

    RETURN p_x_id_typ;  -- Return the new key
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error: %', SQLERRM;
        RETURN NULL;  -- Return NULL if an error occurs
END;
$$;


ALTER FUNCTION public.usp_entity_type_add(p_x_id_typ character varying, p_x_nm_typ character varying) OWNER TO postgres;

--
-- Name: usp_entity_type_add(character varying, character varying, timestamp without time zone, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_entity_type_add(p_x_id_typ character varying, p_x_nm_typ character varying, p_d_crt timestamp without time zone, p_d_udt timestamp without time zone) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO EntityTypes (X_ID_TYP, X_NM_TYP, D_CRT, D_UDT)
    VALUES (p_x_id_typ, p_x_nm_typ, p_d_crt, p_d_udt);

    RETURN 'Entity type added successfully';
EXCEPTION WHEN OTHERS THEN
    RETURN 'Error: ' || SQLERRM;
END;
$$;


ALTER FUNCTION public.usp_entity_type_add(p_x_id_typ character varying, p_x_nm_typ character varying, p_d_crt timestamp without time zone, p_d_udt timestamp without time zone) OWNER TO postgres;

--
-- Name: usp_entity_type_delete(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_entity_type_delete(p_x_id_typ character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM entitytypes
    WHERE x_id_typ = p_x_id_typ;

    IF FOUND THEN
        RETURN 0;  -- Success
    ELSE
        RETURN 1;  -- No matching record found
    END IF;

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error: %', SQLERRM;
        RETURN -1;  -- Error occurred
END;
$$;


ALTER FUNCTION public.usp_entity_type_delete(p_x_id_typ character varying) OWNER TO postgres;

--
-- Name: usp_entity_type_edit(character varying, character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_entity_type_edit(p_x_id_typ character varying, p_x_nm_typ character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE entitytypes
    SET x_nm_typ = p_x_nm_typ,
        d_udt = NOW()  -- Update timestamp
    WHERE x_id_typ = p_x_id_typ;

    IF FOUND THEN
        RETURN 0;  -- Success
    ELSE
        RETURN 1;  -- No matching record found
    END IF;

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error: %', SQLERRM;
        RETURN -1;  -- Error occurred
END;
$$;


ALTER FUNCTION public.usp_entity_type_edit(p_x_id_typ character varying, p_x_nm_typ character varying) OWNER TO postgres;

--
-- Name: usp_entity_type_list(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_entity_type_list() RETURNS TABLE(i_typ_ent character varying, x_dsc_ent character varying, d_crt timestamp without time zone, d_udt timestamp without time zone)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.i_typ_ent,
        t.x_dsc_ent,
        t.d_crt,
        t.d_udt
    FROM public.tlkentitytypes t; -- ✅ Explicit alias to prevent ambiguity
END;
$$;


ALTER FUNCTION public.usp_entity_type_list() OWNER TO postgres;

--
-- Name: usp_getallzonesforcampus(integer); Type: FUNCTION; Schema: public; Owner: parcoadmin
--

CREATE FUNCTION public.usp_getallzonesforcampus(in_campus_id integer) RETURNS jsonb
    LANGUAGE plpgsql
    AS $$
DECLARE
    campus_exists BOOLEAN;
BEGIN
    -- Check if the input campus_id exists and is a Campus L1 zone
    SELECT EXISTS(SELECT 1 FROM zones WHERE i_zn = in_campus_id AND i_typ_zn = 1)
    INTO campus_exists;

    IF NOT campus_exists THEN
        RAISE NOTICE 'Invalid campus_id: %', in_campus_id;
        RETURN jsonb_build_object('error', 'Invalid Campus ID or not a Campus L1 zone');
    END IF;

    -- Recursive query to retrieve all child zones
    RETURN (
        WITH RECURSIVE zone_hierarchy AS (
            -- Base Case: Start with the specified Campus L1 zone
            SELECT 
                z.i_zn, 
                z.x_nm_zn AS name, 
                z.i_typ_zn AS zone_type, 
                z.i_pnt_zn AS parent_zone_id, 
                z.i_map AS map_id
            FROM zones z
            WHERE z.i_zn = in_campus_id
            AND z.i_typ_zn = 1

            UNION ALL

            -- Recursive Case: Fetch child zones based on parent relationships
            SELECT 
                z.i_zn, 
                z.x_nm_zn AS name, 
                z.i_typ_zn AS zone_type, 
                z.i_pnt_zn AS parent_zone_id, 
                z.i_map AS map_id
            FROM zones z
            JOIN zone_hierarchy zh ON z.i_pnt_zn = zh.i_zn
            WHERE z.i_typ_zn IN (1, 2, 3, 4, 5, 10)  -- Include all zone types
              AND z.i_pnt_zn IS NOT NULL
              AND z.i_zn IS NOT NULL
              AND z.i_pnt_zn != 0
        )

        -- Construct JSON output with full recursive children
        SELECT jsonb_build_object(
            'zones', 
            jsonb_agg(
                jsonb_build_object(
                    'zone_id', zh.i_zn,
                    'name', COALESCE(zh.name, 'Unnamed'),
                    'zone_type', zh.zone_type,
                    'parent_zone_id', zh.parent_zone_id,
                    'map_id', zh.map_id,
                    'children', (
                        -- Fetch children recursively using a separate WITH clause
                        WITH RECURSIVE recursive_children AS (
                            SELECT 
                                child.i_zn, 
                                child.x_nm_zn AS name, 
                                child.i_typ_zn AS zone_type, 
                                child.i_pnt_zn AS parent_zone_id, 
                                child.i_map AS map_id
                            FROM zones child
                            WHERE child.i_pnt_zn = zh.i_zn
                            
                            UNION ALL
                            
                            SELECT 
                                grandchild.i_zn, 
                                grandchild.x_nm_zn AS name, 
                                grandchild.i_typ_zn AS zone_type, 
                                grandchild.i_pnt_zn AS parent_zone_id, 
                                grandchild.i_map AS map_id
                            FROM zones grandchild
                            JOIN recursive_children rc ON grandchild.i_pnt_zn = rc.i_zn
                        )
                        SELECT COALESCE(jsonb_agg(
                            jsonb_build_object(
                                'zone_id', i_zn,
                                'name', COALESCE(name, 'Unnamed'),
                                'zone_type', zone_type,
                                'parent_zone_id', parent_zone_id,
                                'map_id', map_id
                            )
                        ), '[]'::jsonb)
                        FROM recursive_children
                    )
                )
            )
        )
        FROM zone_hierarchy zh
        WHERE zh.i_zn = in_campus_id
    );
END;
$$;


ALTER FUNCTION public.usp_getallzonesforcampus(in_campus_id integer) OWNER TO parcoadmin;

--
-- Name: usp_history_insert(integer, real, real, real, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_history_insert(entity_id integer, location_x real, location_y real, location_z real, timestamp_utc timestamp without time zone) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE 
    entity_exists INT;
BEGIN
    -- Check if the entity exists
    SELECT COUNT(*) INTO entity_exists FROM public.entities WHERE i_ent = entity_id;

    IF entity_exists = 0 THEN
        RAISE EXCEPTION 'Entity ID % not found.', entity_id;
    END IF;

    -- Insert the new history record
    INSERT INTO public.history (i_ent, n_x, n_y, n_z, d_timestamp)
    VALUES (entity_id, location_x, location_y, location_z, timestamp_utc);
END;
$$;


ALTER FUNCTION public.usp_history_insert(entity_id integer, location_x real, location_y real, location_z real, timestamp_utc timestamp without time zone) OWNER TO postgres;

--
-- Name: usp_map_delete(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_map_delete(map_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE 
    map_exists INT;
BEGIN
    -- Check if the map exists
    SELECT COUNT(*) INTO map_exists FROM public.maps WHERE i_map = map_id;

    IF map_exists = 0 THEN
        RAISE EXCEPTION 'Map ID % not found.', map_id;
    END IF;

    -- Perform the delete operation
    DELETE FROM public.maps WHERE i_map = map_id;
END;
$$;


ALTER FUNCTION public.usp_map_delete(map_id integer) OWNER TO postgres;

--
-- Name: usp_map_insert(character varying, character varying, character varying, real, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_map_insert(map_name character varying, map_path character varying, map_format character varying, map_scale real, zone_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    zone_exists INT;
BEGIN
    -- Check if the zone exists
    SELECT COUNT(*) INTO zone_exists FROM public.zones WHERE i_zn = zone_id;

    IF zone_exists = 0 THEN
        RAISE EXCEPTION 'Zone ID % not found.', zone_id;
    END IF;

    -- Validate format
    IF map_format NOT IN ('GIF', 'PNG', 'JPG', 'JPEG', 'BMP') THEN
        RAISE EXCEPTION 'Invalid map format. Allowed: GIF, PNG, JPG, JPEG, BMP.';
    END IF;

    -- Insert the new map
    INSERT INTO public.maps (x_nm_map, x_path, x_format, n_scale, i_zn, d_uploaded)
    VALUES (map_name, map_path, map_format, map_scale, zone_id, NOW());
END;
$$;


ALTER FUNCTION public.usp_map_insert(map_name character varying, map_path character varying, map_format character varying, map_scale real, zone_id integer) OWNER TO postgres;

--
-- Name: usp_map_list(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_map_list() RETURNS TABLE(i_map integer, x_nm_map character varying, x_path character varying, n_scale real, i_zn integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY 
    SELECT 
        m.i_map, 
        m.x_nm_map, 
        m.x_path, 
        m.n_scale, 
        m.i_zn
    FROM public.maps m;
END;
$$;


ALTER FUNCTION public.usp_map_list() OWNER TO postgres;

--
-- Name: usp_region_add(integer, integer, character varying, real, real, real, real, real, real, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_region_add(p_i_rgn integer, p_i_zn integer, p_x_nm_rgn character varying, p_n_max_x real, p_n_max_y real, p_n_max_z real, p_n_min_x real, p_n_min_y real, p_n_min_z real, p_i_trg integer) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_i_rgn integer;
BEGIN
    -- Insert into regions table
    INSERT INTO public.regions (i_zn, x_nm_rgn, n_max_x, n_max_y, n_max_z, n_min_x, n_min_y, n_min_z, i_trg)
    VALUES (p_i_zn, p_x_nm_rgn, p_n_max_x, p_n_max_y, p_n_max_z, p_n_min_x, p_n_min_y, p_n_min_z, p_i_trg)
    RETURNING i_rgn INTO v_i_rgn;
    RETURN v_i_rgn;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error in usp_region_add: %', SQLERRM;
        RETURN -1;  -- Error indicator
END;
$$;


ALTER FUNCTION public.usp_region_add(p_i_rgn integer, p_i_zn integer, p_x_nm_rgn character varying, p_n_max_x real, p_n_max_y real, p_n_max_z real, p_n_min_x real, p_n_min_y real, p_n_min_z real, p_i_trg integer) OWNER TO postgres;

--
-- Name: usp_region_delete(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_region_delete(region_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE 
    region_exists INT;
BEGIN
    -- Check if the region exists
    SELECT COUNT(*) INTO region_exists FROM public.regions WHERE i_rgn = region_id;

    IF region_exists = 0 THEN
        RAISE EXCEPTION 'Region ID % not found.', region_id;
    END IF;

    -- Perform the delete operation
    DELETE FROM public.regions WHERE i_rgn = region_id;
END;
$$;


ALTER FUNCTION public.usp_region_delete(region_id integer) OWNER TO postgres;

--
-- Name: usp_region_edit(integer, integer, character varying, integer, integer, integer, integer, integer, integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_region_edit(region_id integer, zone_id integer, region_name character varying, max_x integer, max_y integer, max_z integer, min_x integer, min_y integer, min_z integer, trigger_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE 
    region_exists INT;
BEGIN
    -- Check if the region exists
    SELECT COUNT(*) INTO region_exists FROM public.regions WHERE i_rgn = region_id;

    IF region_exists = 0 THEN
        RAISE EXCEPTION 'Region ID % not found.', region_id;
    END IF;

    -- Update the region
    UPDATE public.regions
    SET 
        i_zn = zone_id,
        x_nm_rgn = region_name,
        n_max_x = max_x,
        n_max_y = max_y,
        n_max_z = max_z,
        n_min_x = min_x,
        n_min_y = min_y,
        n_min_z = min_z,
        i_trg = trigger_id
    WHERE i_rgn = region_id;
END;
$$;


ALTER FUNCTION public.usp_region_edit(region_id integer, zone_id integer, region_name character varying, max_x integer, max_y integer, max_z integer, min_x integer, min_y integer, min_z integer, trigger_id integer) OWNER TO postgres;

--
-- Name: usp_region_list(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_region_list() RETURNS TABLE(i_rgn integer, i_zn integer, x_nm_rgn character varying, n_max_x real, n_max_y real, n_max_z real, n_min_x real, n_min_y real, n_min_z real, i_trg integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY 
    SELECT 
        r.i_rgn, 
        r.i_zn, 
        r.x_nm_rgn, 
        r.n_max_x, 
        r.n_max_y, 
        r.n_max_z, 
        r.n_min_x, 
        r.n_min_y, 
        r.n_min_z, 
        r.i_trg
    FROM public.regions r;
END;
$$;


ALTER FUNCTION public.usp_region_list() OWNER TO postgres;

--
-- Name: usp_region_select_by_id(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_region_select_by_id(region_id integer) RETURNS TABLE(i_rgn integer, i_zn integer, x_nm_rgn character varying, n_max_x real, n_max_y real, n_max_z real, n_min_x real, n_min_y real, n_min_z real, i_trg integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY 
    SELECT 
        r.i_rgn, 
        r.i_zn, 
        r.x_nm_rgn, 
        r.n_max_x, 
        r.n_max_y, 
        r.n_max_z, 
        r.n_min_x, 
        r.n_min_y, 
        r.n_min_z, 
        r.i_trg
    FROM public.regions r 
    WHERE r.i_rgn = region_id;
END;
$$;


ALTER FUNCTION public.usp_region_select_by_id(region_id integer) OWNER TO postgres;

--
-- Name: usp_regions_select(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_regions_select() RETURNS TABLE(i_rgn integer, i_zn integer, x_nm_rgn character varying, n_max_x numeric, n_max_y numeric, n_max_z numeric, n_min_x numeric, n_min_y numeric, n_min_z numeric, i_trg integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT
        r.i_rgn,
        r.i_zn,
        r.x_nm_rgn,
        r.n_max_x::NUMERIC(18,2),
        r.n_max_y::NUMERIC(18,2),
        r.n_max_z::NUMERIC(18,2),
        r.n_min_x::NUMERIC(18,2),
        r.n_min_y::NUMERIC(18,2),
        r.n_min_z::NUMERIC(18,2),
        r.i_trg
    FROM public.regions r;  -- ✅ Explicit table alias
END;
$$;


ALTER FUNCTION public.usp_regions_select() OWNER TO postgres;

--
-- Name: usp_regions_select_by_trigger(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_regions_select_by_trigger(trigger_id integer) RETURNS TABLE(i_rgn integer, i_zn integer, x_nm_rgn character varying, n_max_x numeric, n_max_y numeric, n_max_z numeric, n_min_x numeric, n_min_y numeric, n_min_z numeric, i_trg integer, n_x numeric, n_y numeric, n_z numeric, n_ord integer, i_vtx integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT
        r.i_rgn, 
        r.i_zn, 
        r.x_nm_rgn,
        r.n_max_x::NUMERIC(18,2),  -- Explicit cast
        r.n_max_y::NUMERIC(18,2),  
        r.n_max_z::NUMERIC(18,2),
        r.n_min_x::NUMERIC(18,2),
        r.n_min_y::NUMERIC(18,2),
        r.n_min_z::NUMERIC(18,2),
        r.i_trg,
        v.n_x::NUMERIC(18,2),  -- Explicit cast
        v.n_y::NUMERIC(18,2),
        v.n_z::NUMERIC(18,2),
        v.n_ord, 
        v.i_vtx
    FROM public.regions r
    LEFT OUTER JOIN public.vertices v
    ON r.i_rgn = v.i_rgn
    WHERE r.i_trg = trigger_id;
END;
$$;


ALTER FUNCTION public.usp_regions_select_by_trigger(trigger_id integer) OWNER TO postgres;

--
-- Name: usp_regions_select_by_zone(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_regions_select_by_zone(zone_id integer) RETURNS TABLE(i_rgn integer, i_zn integer, x_nm_rgn character varying, n_max_x numeric, n_max_y numeric, n_max_z numeric, n_min_x numeric, n_min_y numeric, n_min_z numeric, i_trg integer, n_x numeric, n_y numeric, n_z numeric, n_ord integer, i_vtx integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT
        r.i_rgn,
        r.i_zn,
        r.x_nm_rgn,
        r.n_max_x::NUMERIC(18,2),
        r.n_max_y::NUMERIC(18,2),
        r.n_max_z::NUMERIC(18,2),
        r.n_min_x::NUMERIC(18,2),
        r.n_min_y::NUMERIC(18,2),
        r.n_min_z::NUMERIC(18,2),
        r.i_trg,
        v.n_x::NUMERIC(18,2),
        v.n_y::NUMERIC(18,2),
        v.n_z::NUMERIC(18,2),
        v.n_ord,
        v.i_vtx
    FROM public.regions r
    LEFT OUTER JOIN public.vertices v
    ON r.i_rgn = v.i_rgn
    WHERE r.i_zn = zone_id;
END;
$$;


ALTER FUNCTION public.usp_regions_select_by_zone(zone_id integer) OWNER TO postgres;

--
-- Name: usp_resource_delete(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_resource_delete(resource_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE 
    resource_exists INT;
BEGIN
    -- Check if the resource exists
    SELECT COUNT(*) INTO resource_exists FROM public.tlkresources WHERE i_res = resource_id;

    IF resource_exists = 0 THEN
        RAISE EXCEPTION 'Resource ID % not found.', resource_id;
    END IF;

    -- Perform the delete operation
    DELETE FROM public.tlkresources WHERE i_res = resource_id;
END;
$$;


ALTER FUNCTION public.usp_resource_delete(resource_id integer) OWNER TO postgres;

--
-- Name: usp_resource_edit(integer, integer, character varying, character varying, integer, integer, boolean, boolean); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_resource_edit(resource_id integer, resource_type integer, resource_name character varying, resource_ip character varying, resource_port integer, resource_rank integer, resource_fs boolean, resource_avg boolean) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE 
    resource_exists INT;
BEGIN
    -- Check if the resource exists
    SELECT COUNT(*) INTO resource_exists FROM public.tlkresources WHERE i_res = resource_id;

    IF resource_exists = 0 THEN
        RAISE EXCEPTION 'Resource ID % not found.', resource_id;
    END IF;

    -- Update the resource
    UPDATE public.tlkresources
    SET 
        i_typ_res = resource_type,
        x_nm_res = resource_name,
        x_ip = resource_ip,
        i_prt = resource_port,
        i_rnk = resource_rank,
        f_fs = resource_fs,
        f_avg = resource_avg
    WHERE i_res = resource_id;
END;
$$;


ALTER FUNCTION public.usp_resource_edit(resource_id integer, resource_type integer, resource_name character varying, resource_ip character varying, resource_port integer, resource_rank integer, resource_fs boolean, resource_avg boolean) OWNER TO postgres;

--
-- Name: usp_resource_list(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_resource_list() RETURNS TABLE(i_res integer, i_typ_res integer, x_nm_res character varying, x_ip character varying, i_prt integer, i_rnk integer, f_fs boolean, f_avg boolean)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY 
    SELECT 
        r.i_res, 
        r.i_typ_res, 
        r.x_nm_res, 
        r.x_ip, 
        r.i_prt, 
        r.i_rnk, 
        r.f_fs, 
        r.f_avg
    FROM public.tlkresources r;
END;
$$;


ALTER FUNCTION public.usp_resource_list() OWNER TO postgres;

--
-- Name: usp_resource_select_by_id(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_resource_select_by_id(resource_id integer) RETURNS TABLE(i_res integer, i_typ_res integer, x_nm_res character varying, x_ip character varying, i_prt integer, i_rnk integer, f_fs boolean, f_avg boolean)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY 
    SELECT 
        r.i_res, 
        r.i_typ_res, 
        r.x_nm_res, 
        r.x_ip, 
        r.i_prt, 
        r.i_rnk, 
        r.f_fs, 
        r.f_avg
    FROM public.tlkresources r 
    WHERE r.i_res = resource_id;
END;
$$;


ALTER FUNCTION public.usp_resource_select_by_id(resource_id integer) OWNER TO postgres;

--
-- Name: usp_resource_type_list(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_resource_type_list() RETURNS TABLE(i_typ_res integer, x_dsc_res character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.i_typ_res,
        t.x_dsc_res  -- Corrected column name
    FROM public.tlkresourcetypes t;
END;
$$;


ALTER FUNCTION public.usp_resource_type_list() OWNER TO postgres;

--
-- Name: usp_resources_add(integer, character varying, character varying, integer, integer, boolean, boolean); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_resources_add(resource_type integer, resource_name character varying, resource_ip character varying, resource_port integer, resource_rank integer, resource_fs boolean, resource_avg boolean) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    new_resource_id INT;
BEGIN
    -- Insert the resource and return the new ID
    INSERT INTO public.tlkresources (I_TYP_RES, X_NM_RES, X_IP, I_PRT, I_RNK, F_FS, F_AVG)
    VALUES (resource_type, resource_name, resource_ip, resource_port, resource_rank, resource_fs, resource_avg)
    RETURNING I_RES INTO new_resource_id;

    -- Return the newly created resource ID
    RETURN new_resource_id;
END;
$$;


ALTER FUNCTION public.usp_resources_add(resource_type integer, resource_name character varying, resource_ip character varying, resource_port integer, resource_rank integer, resource_fs boolean, resource_avg boolean) OWNER TO postgres;

--
-- Name: usp_resources_rank_down(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_resources_rank_down(resource_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Update the resource rank by increasing `i_rnk` by 1
    UPDATE public.tlkresources
    SET i_rnk = i_rnk + 1
    WHERE i_res = resource_id;
END;
$$;


ALTER FUNCTION public.usp_resources_rank_down(resource_id integer) OWNER TO postgres;

--
-- Name: usp_resources_rank_up(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_resources_rank_up(resource_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Update the resource rank by decreasing `i_rnk` by 1
    UPDATE public.tlkresources
    SET i_rnk = i_rnk - 1
    WHERE i_res = resource_id;
END;
$$;


ALTER FUNCTION public.usp_resources_rank_up(resource_id integer) OWNER TO postgres;

--
-- Name: usp_resources_select(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_resources_select(resource_id integer) RETURNS TABLE(i_res integer, i_typ_res integer, x_nm_res character varying, x_ip character varying, i_prt integer, i_rnk integer, f_fs boolean, f_avg boolean)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.i_res,
        r.i_typ_res,
        r.x_nm_res,
        r.x_ip,
        r.i_prt,
        r.i_rnk,
        r.f_fs,
        r.f_avg
    FROM public.tlkresources r
    WHERE r.i_res = resource_id;
END;
$$;


ALTER FUNCTION public.usp_resources_select(resource_id integer) OWNER TO postgres;

--
-- Name: usp_resources_select_all(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_resources_select_all() RETURNS TABLE(i_res integer, i_typ_res integer, x_nm_res character varying, x_ip character varying, i_prt integer, i_rnk integer, f_fs boolean, f_avg boolean)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.i_res,
        r.i_typ_res,
        r.x_nm_res,
        r.x_ip,
        r.i_prt,
        r.i_rnk,
        r.f_fs,
        r.f_avg
    FROM public.tlkresources r;
END;
$$;


ALTER FUNCTION public.usp_resources_select_all() OWNER TO postgres;

--
-- Name: usp_resources_select_by_type(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_resources_select_by_type(resource_type integer) RETURNS TABLE(i_res integer, i_typ_res integer, x_nm_res character varying, x_ip character varying, i_prt integer, i_rnk integer, f_fs boolean, f_avg boolean)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.i_res,
        r.i_typ_res,
        r.x_nm_res,
        r.x_ip,
        r.i_prt,
        r.i_rnk,
        r.f_fs,
        r.f_avg
    FROM public.tlkresources r
    WHERE r.i_typ_res = resource_type;
END;
$$;


ALTER FUNCTION public.usp_resources_select_by_type(resource_type integer) OWNER TO postgres;

--
-- Name: usp_trigger_add(integer, character varying, boolean); Type: FUNCTION; Schema: public; Owner: parcoadmin
--

CREATE FUNCTION public.usp_trigger_add(i_dir integer, x_nm_trg character varying, f_ign boolean) RETURNS integer
    LANGUAGE plpgsql
    AS $$

DECLARE new_trigger_id INT;

BEGIN
    -- Ensure the trigger name does not already exist
    IF EXISTS (SELECT 1 FROM public.triggers WHERE triggers.x_nm_trg = usp_trigger_add.x_nm_trg) THEN
        RAISE EXCEPTION 'Trigger name % already exists', x_nm_trg;
    END IF;

    -- Insert into triggers and return the new ID
    INSERT INTO public.triggers (X_NM_TRG, I_DIR, F_IGN)
    VALUES (usp_trigger_add.x_nm_trg, usp_trigger_add.i_dir, usp_trigger_add.f_ign)
    RETURNING I_TRG INTO new_trigger_id;

    -- Initialize state tracking in trigger_states table
    INSERT INTO public.trigger_states (i_trg, x_id_dev, last_state)
    SELECT new_trigger_id, d.x_id_dev, 0 FROM public.devices d;

    -- Log success
    RAISE NOTICE 'Trigger Added: ID = %, Name = %, Direction = %, Ignore = %',
        new_trigger_id, x_nm_trg, i_dir, f_ign;

    RETURN new_trigger_id;

EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'Trigger name % already exists', x_nm_trg;
    WHEN foreign_key_violation THEN
        RAISE EXCEPTION 'Direction ID % does not exist in tlktrigdirections', i_dir;
    WHEN others THEN
        RAISE EXCEPTION 'Unexpected error adding trigger: %', SQLERRM;
        RETURN -1;
END;
$$;


ALTER FUNCTION public.usp_trigger_add(i_dir integer, x_nm_trg character varying, f_ign boolean) OWNER TO parcoadmin;

--
-- Name: usp_trigger_delete(integer); Type: FUNCTION; Schema: public; Owner: parcoadmin
--

CREATE FUNCTION public.usp_trigger_delete(trigger_id integer) RETURNS boolean
    LANGUAGE plpgsql
    AS $$  -- Return TRUE if deleted, FALSE if not found
DECLARE
    deleted_count INT;
BEGIN
    -- Remove dependent entries in trigger_states first
    DELETE FROM public.trigger_states WHERE i_trg = trigger_id;

    -- Delete the trigger
    DELETE FROM public.triggers WHERE i_trg = trigger_id RETURNING i_trg INTO deleted_count;

    -- If nothing was deleted, return FALSE
    IF deleted_count IS NULL THEN
        RETURN FALSE;
    END IF;

    RETURN TRUE;
END;
$$;


ALTER FUNCTION public.usp_trigger_delete(trigger_id integer) OWNER TO parcoadmin;

--
-- Name: usp_trigger_direction_list(); Type: FUNCTION; Schema: public; Owner: parcoadmin
--

CREATE FUNCTION public.usp_trigger_direction_list() RETURNS TABLE(i_dir integer, x_dir character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT t.i_dir, t.x_dir
    FROM public.tlktrigdirections t;
END;
$$;


ALTER FUNCTION public.usp_trigger_direction_list() OWNER TO parcoadmin;

--
-- Name: usp_trigger_edit(integer, character varying, integer, boolean); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_trigger_edit(trigger_id integer, trigger_name character varying, trigger_dir integer, trigger_ignore boolean) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE 
    trigger_exists INT;
BEGIN
    -- Check if the trigger exists
    SELECT COUNT(*) INTO trigger_exists FROM public.triggers WHERE i_trg = trigger_id;

    IF trigger_exists = 0 THEN
        RAISE EXCEPTION 'Trigger ID % not found.', trigger_id;
    END IF;

    -- Update the trigger
    UPDATE public.triggers
    SET 
        x_nm_trg = trigger_name,
        i_dir = trigger_dir,
        f_ign = trigger_ignore
    WHERE i_trg = trigger_id;
END;
$$;


ALTER FUNCTION public.usp_trigger_edit(trigger_id integer, trigger_name character varying, trigger_dir integer, trigger_ignore boolean) OWNER TO postgres;

--
-- Name: usp_trigger_list(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_trigger_list() RETURNS TABLE(i_trg integer, x_nm_trg character varying, i_dir integer, f_ign boolean)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY 
    SELECT 
        t.i_trg, 
        t.x_nm_trg, 
        t.i_dir, 
        t.f_ign
    FROM public.triggers t;
END;
$$;


ALTER FUNCTION public.usp_trigger_list() OWNER TO postgres;

--
-- Name: usp_trigger_move(integer, numeric, numeric, numeric); Type: FUNCTION; Schema: public; Owner: parcoadmin
--

CREATE FUNCTION public.usp_trigger_move(trigger_id integer, new_x numeric, new_y numeric, new_z numeric) RETURNS void
    LANGUAGE plpgsql
    AS $$

BEGIN
    -- Ensure trigger exists
    IF NOT EXISTS (SELECT 1 FROM public.triggers WHERE i_trg = trigger_id) THEN
        RAISE EXCEPTION 'Trigger ID % does not exist', trigger_id;
    END IF;

    -- Move the trigger by updating all related vertices
    UPDATE public.vertices
    SET n_x = n_x + new_x, n_y = n_y + new_y, n_z = n_z + new_z
    WHERE i_rgn IN (SELECT i_rgn FROM public.regions WHERE i_trg = trigger_id);

    -- Log success
    RAISE NOTICE 'Trigger ID % moved by (%, %, %)', trigger_id, new_x, new_y, new_z;

END;
$$;


ALTER FUNCTION public.usp_trigger_move(trigger_id integer, new_x numeric, new_y numeric, new_z numeric) OWNER TO parcoadmin;

--
-- Name: usp_trigger_select(integer); Type: FUNCTION; Schema: public; Owner: parcoadmin
--

CREATE FUNCTION public.usp_trigger_select(trigger_id integer) RETURNS TABLE(i_trg integer, x_nm_trg character varying, i_dir integer, f_ign boolean, i_rgn integer, i_zn integer, x_nm_rgn character varying, n_x numeric, n_y numeric, n_z numeric, n_ord integer, i_vtx integer)
    LANGUAGE plpgsql
    AS $$

BEGIN
    RETURN QUERY
    SELECT 
        t.i_trg, t.x_nm_trg, t.i_dir, t.f_ign,
        r.i_rgn, r.i_zn, r.x_nm_rgn,
        v.n_x, v.n_y, v.n_z, v.n_ord, v.i_vtx
    FROM public.triggers t
    LEFT JOIN public.regions r ON t.i_trg = r.i_trg
    LEFT JOIN public.vertices v ON r.i_rgn = v.i_rgn
    WHERE t.i_trg = trigger_id;
END;
$$;


ALTER FUNCTION public.usp_trigger_select(trigger_id integer) OWNER TO parcoadmin;

--
-- Name: usp_trigger_select_all(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_trigger_select_all() RETURNS TABLE(i_trg integer, x_nm_trg character varying, i_dir integer, f_ign boolean, i_rgn integer, i_zn integer, x_nm_rgn character varying, n_x numeric, n_y numeric, n_z numeric, n_ord integer, i_vtx integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.i_trg,
        t.x_nm_trg,
        t.i_dir,
        t.f_ign,
        r.i_rgn,
        r.i_zn,
        r.x_nm_rgn,
        v.n_x::NUMERIC(18,2),
        v.n_y::NUMERIC(18,2),
        v.n_z::NUMERIC(18,2),
        v.n_ord,
        v.i_vtx
    FROM public.triggers t
    LEFT OUTER JOIN public.regions r ON t.i_trg = r.i_trg
    LEFT OUTER JOIN public.vertices v ON r.i_rgn = v.i_rgn;
END;
$$;


ALTER FUNCTION public.usp_trigger_select_all() OWNER TO postgres;

--
-- Name: usp_trigger_select_by_id(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_trigger_select_by_id(trigger_id integer) RETURNS TABLE(i_trg integer, x_nm_trg character varying, i_dir integer, f_ign boolean)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY 
    SELECT 
        t.i_trg, 
        t.x_nm_trg, 
        t.i_dir, 
        t.f_ign
    FROM public.triggers t 
    WHERE t.i_trg = trigger_id;
END;
$$;


ALTER FUNCTION public.usp_trigger_select_by_id(trigger_id integer) OWNER TO postgres;

--
-- Name: usp_trigger_select_by_point(numeric, numeric, numeric); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_trigger_select_by_point(point_x numeric, point_y numeric, point_z numeric) RETURNS TABLE(i_trg integer, x_nm_trg character varying, i_dir integer, f_ign boolean, i_rgn integer, i_zn integer, x_nm_rgn character varying, n_x numeric, n_y numeric, n_z numeric, n_ord integer, i_vtx integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.i_trg,
        t.x_nm_trg,
        t.i_dir,
        t.f_ign,
        r.i_rgn,
        r.i_zn,
        r.x_nm_rgn,
        v.n_x::NUMERIC(18,2),
        v.n_y::NUMERIC(18,2),
        v.n_z::NUMERIC(18,2),
        v.n_ord,
        v.i_vtx
    FROM public.triggers t
    LEFT OUTER JOIN public.regions r ON t.i_trg = r.i_trg
    LEFT OUTER JOIN public.vertices v ON r.i_rgn = v.i_rgn
    WHERE r.n_max_x >= point_x AND r.n_min_x <= point_x
    AND r.n_max_y >= point_y AND r.n_min_y <= point_y
    AND r.n_max_z >= point_z AND r.n_min_z <= point_z;
END;
$$;


ALTER FUNCTION public.usp_trigger_select_by_point(point_x numeric, point_y numeric, point_z numeric) OWNER TO postgres;

--
-- Name: usp_vertex_delete(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_vertex_delete(vertex_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE 
    vertex_exists INT;
BEGIN
    -- Check if the vertex exists
    SELECT COUNT(*) INTO vertex_exists FROM public.vertices WHERE i_vtx = vertex_id;

    IF vertex_exists = 0 THEN
        RAISE EXCEPTION 'Vertex ID % not found.', vertex_id;
    END IF;

    -- Perform the delete operation
    DELETE FROM public.vertices WHERE i_vtx = vertex_id;
END;
$$;


ALTER FUNCTION public.usp_vertex_delete(vertex_id integer) OWNER TO postgres;

--
-- Name: usp_vertex_edit(integer, real, real, real, integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_vertex_edit(vertex_id integer, coord_x real, coord_y real, coord_z real, order_num integer, region_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE 
    vertex_exists INT;
BEGIN
    -- Check if the vertex exists
    SELECT COUNT(*) INTO vertex_exists FROM public.vertices WHERE i_vtx = vertex_id;

    IF vertex_exists = 0 THEN
        RAISE EXCEPTION 'Vertex ID % not found.', vertex_id;
    END IF;

    -- Update the vertex
    UPDATE public.vertices
    SET 
        n_x = coord_x,
        n_y = coord_y,
        n_z = coord_z,
        n_ord = order_num,
        i_rgn = region_id
    WHERE i_vtx = vertex_id;
END;
$$;


ALTER FUNCTION public.usp_vertex_edit(vertex_id integer, coord_x real, coord_y real, coord_z real, order_num integer, region_id integer) OWNER TO postgres;

--
-- Name: usp_vertex_list(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_vertex_list() RETURNS TABLE(i_vtx integer, n_x real, n_y real, n_z real, n_ord integer, i_rgn integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY 
    SELECT 
        v.i_vtx, 
        v.n_x, 
        v.n_y, 
        v.n_z, 
        v.n_ord, 
        v.i_rgn
    FROM public.vertices v;
END;
$$;


ALTER FUNCTION public.usp_vertex_list() OWNER TO postgres;

--
-- Name: usp_vertex_select_by_id(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_vertex_select_by_id(vertex_id integer) RETURNS TABLE(i_vtx integer, n_x real, n_y real, n_z real, n_ord integer, i_rgn integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY 
    SELECT 
        v.i_vtx, 
        v.n_x, 
        v.n_y, 
        v.n_z, 
        v.n_ord, 
        v.i_rgn
    FROM public.vertices v 
    WHERE v.i_vtx = vertex_id;
END;
$$;


ALTER FUNCTION public.usp_vertex_select_by_id(vertex_id integer) OWNER TO postgres;

--
-- Name: usp_zone_add(integer, character varying, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_zone_add(i_typ_zn integer, x_nm_zn character varying, i_pnt_zn integer) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    new_zone_id INT;
BEGIN
    -- Insert into zones and return the new ID
    INSERT INTO public.zones (I_TYP_ZN, X_NM_ZN, I_PNT_ZN)
    VALUES (i_typ_zn, x_nm_zn, i_pnt_zn)
    RETURNING I_ZN INTO new_zone_id;

    -- Return the newly created zone ID
    RETURN new_zone_id;
END;
$$;


ALTER FUNCTION public.usp_zone_add(i_typ_zn integer, x_nm_zn character varying, i_pnt_zn integer) OWNER TO postgres;

--
-- Name: usp_zone_children_select(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_zone_children_select(parent_zone_id integer) RETURNS TABLE(i_zn integer, i_typ_zn integer, x_nm_zn character varying, i_pnt_zn integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT
        z.I_ZN,
        z.I_TYP_ZN,
        z.X_NM_ZN,
        z.I_PNT_ZN
    FROM public.zones z
    WHERE z.I_PNT_ZN = parent_zone_id;
END;
$$;


ALTER FUNCTION public.usp_zone_children_select(parent_zone_id integer) OWNER TO postgres;

--
-- Name: usp_zone_delete(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_zone_delete(i_zn integer) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    delete_error INT := 0;
BEGIN
    -- Perform the delete operation
    DELETE FROM public.zones WHERE public.zones.I_ZN = usp_zone_delete.i_zn;

    -- Capture error code (0 means success, 1 means failure)
    GET DIAGNOSTICS delete_error = ROW_COUNT;

    -- If no rows were deleted, return 1 (like MSSQL's @@ERROR)
    IF delete_error = 0 THEN
        RETURN 1;
    END IF;

    -- Otherwise, return success
    RETURN 0;
END;
$$;


ALTER FUNCTION public.usp_zone_delete(i_zn integer) OWNER TO postgres;

--
-- Name: usp_zone_edit(integer, integer, character varying, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_zone_edit(p_zn_id integer, p_typ_zn integer, p_nm_zn character varying, p_pnt_zn integer DEFAULT NULL::integer) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    zone_exists INT;
BEGIN
    -- Check if the zone exists
    SELECT COUNT(*) INTO zone_exists
    FROM public.zones r
    WHERE r.I_ZN = p_zn_id;  -- ✅ No ambiguity

    IF zone_exists = 0 THEN
        RAISE EXCEPTION 'Zone ID not found: %', p_zn_id;
    END IF;

    -- Check for a zone specifying itself as a parent
    IF p_zn_id = p_pnt_zn THEN
        RAISE EXCEPTION 'A Zone may not specify itself as its parent';
    END IF;

    -- Update the zone
    UPDATE public.zones
    SET
        I_TYP_ZN = p_typ_zn,
        X_NM_ZN = p_nm_zn,
        I_PNT_ZN = p_pnt_zn
    WHERE I_ZN = p_zn_id;  -- ✅ No ambiguity

    -- Return 0 for success
    RETURN 0;
END;
$$;


ALTER FUNCTION public.usp_zone_edit(p_zn_id integer, p_typ_zn integer, p_nm_zn character varying, p_pnt_zn integer) OWNER TO postgres;

--
-- Name: usp_zone_list(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_zone_list() RETURNS TABLE(i_zn integer, i_typ_zn integer, x_nm_zn character varying, i_pnt_zn integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        z.I_ZN, 
        z.I_TYP_ZN, 
        z.X_NM_ZN, 
        z.I_PNT_ZN
    FROM public.zones z;
END;
$$;


ALTER FUNCTION public.usp_zone_list() OWNER TO postgres;

--
-- Name: usp_zone_parent_select(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_zone_parent_select(child_zone_id integer) RETURNS TABLE(i_zn integer, i_typ_zn integer, x_nm_zn character varying, i_pnt_zn integer)
    LANGUAGE plpgsql
    AS $$
DECLARE
    parent_zone_id INT;
BEGIN
    -- Get the parent zone ID
    SELECT z.I_PNT_ZN INTO parent_zone_id 
    FROM public.zones z 
    WHERE z.I_ZN = child_zone_id;

    -- Ensure parent_zone_id is NOT NULL before querying
    IF parent_zone_id IS NOT NULL THEN
        RETURN QUERY
        SELECT 
            z.I_ZN, 
            z.I_TYP_ZN, 
            z.X_NM_ZN, 
            z.I_PNT_ZN
        FROM public.zones z
        WHERE z.I_ZN = parent_zone_id;
    END IF;
END;
$$;


ALTER FUNCTION public.usp_zone_parent_select(child_zone_id integer) OWNER TO postgres;

--
-- Name: usp_zone_select(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_zone_select(zone_id integer) RETURNS TABLE(i_zn integer, i_typ_zn integer, x_nm_zn character varying, i_pnt_zn integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT
        z.I_ZN,
        z.I_TYP_ZN,
        z.X_NM_ZN,
        z.I_PNT_ZN
    FROM public.zones z
    WHERE z.I_ZN = zone_id;
END;
$$;


ALTER FUNCTION public.usp_zone_select(zone_id integer) OWNER TO postgres;

--
-- Name: usp_zone_select_all(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_zone_select_all() RETURNS TABLE(i_zn integer, i_typ_zn integer, x_nm_zn character varying, i_pnt_zn integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT
        z.I_ZN,
        z.I_TYP_ZN,
        z.X_NM_ZN,
        z.I_PNT_ZN
    FROM public.zones z;
END;
$$;


ALTER FUNCTION public.usp_zone_select_all() OWNER TO postgres;

--
-- Name: usp_zone_select_by_id(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_zone_select_by_id(zone_id integer) RETURNS TABLE(i_zn integer, i_typ_zn integer, x_nm_zn character varying, i_pnt_zn integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY 
    SELECT 
        z.i_zn, 
        z.i_typ_zn, 
        z.x_nm_zn, 
        z.i_pnt_zn
    FROM public.zones z 
    WHERE z.i_zn = zone_id;
END;
$$;


ALTER FUNCTION public.usp_zone_select_by_id(zone_id integer) OWNER TO postgres;

--
-- Name: usp_zone_select_by_point(numeric, numeric, numeric); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_zone_select_by_point(point_x numeric, point_y numeric, point_z numeric) RETURNS TABLE(i_zn integer, i_typ_zn integer, x_nm_zn character varying, i_pnt_zn integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT
        z.I_ZN,
        z.I_TYP_ZN,
        z.X_NM_ZN,
        z.I_PNT_ZN
    FROM public.zones z
    JOIN public.regions r ON z.I_ZN = r.I_ZN
    WHERE r.n_max_x >= point_x AND r.n_min_x <= point_x
      AND r.n_max_y >= point_y AND r.n_min_y <= point_y
      AND r.n_max_z >= point_z AND r.n_min_z <= point_z;
END;
$$;


ALTER FUNCTION public.usp_zone_select_by_point(point_x numeric, point_y numeric, point_z numeric) OWNER TO postgres;

--
-- Name: usp_zone_type_add(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_zone_type_add(zone_type_name character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    new_zone_type_id INT;
BEGIN
    -- Insert new zone type and return its ID
    INSERT INTO public.tlkzonetypes (X_DSC_ZN)  -- ✅ Fixed column name
    VALUES (zone_type_name)
    RETURNING I_TYP_ZN INTO new_zone_type_id;

    -- Return the newly created zone type ID
    RETURN new_zone_type_id;
END;
$$;


ALTER FUNCTION public.usp_zone_type_add(zone_type_name character varying) OWNER TO postgres;

--
-- Name: usp_zone_vertices_add(integer, real, real, real, integer, integer); Type: FUNCTION; Schema: public; Owner: parcoadmin
--

CREATE FUNCTION public.usp_zone_vertices_add(vertex_id integer, coord_x real, coord_y real, coord_z real, order_num integer, region_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO public.vertices (i_vtx, n_x, n_y, n_z, n_ord, i_rgn)
    VALUES (
        COALESCE(vertex_id, nextval('vertices_i_vtx_seq'::regclass)),
        coord_x, coord_y, coord_z, order_num, region_id
    );
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error in usp_zone_vertices_add: %', SQLERRM;
END;
$$;


ALTER FUNCTION public.usp_zone_vertices_add(vertex_id integer, coord_x real, coord_y real, coord_z real, order_num integer, region_id integer) OWNER TO parcoadmin;

--
-- Name: usp_zone_vertices_delete(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_zone_vertices_delete(zone_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE 
    zone_exists INT;
BEGIN
    -- Check if the zone exists
    SELECT COUNT(*) INTO zone_exists FROM public.zones WHERE i_zn = zone_id;

    IF zone_exists = 0 THEN
        RAISE EXCEPTION 'Zone ID % not found.', zone_id;
    END IF;

    -- Perform the delete operation (delete all vertices tied to the zone)
    DELETE FROM public.vertices WHERE i_rgn = zone_id;
END;
$$;


ALTER FUNCTION public.usp_zone_vertices_delete(zone_id integer) OWNER TO postgres;

--
-- Name: usp_zone_vertices_list(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_zone_vertices_list(zone_id integer) RETURNS TABLE(i_vtx integer, n_x real, n_y real, n_z real, n_ord integer, i_rgn integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY 
    SELECT 
        v.i_vtx, 
        v.n_x, 
        v.n_y, 
        v.n_z, 
        v.n_ord, 
        v.i_rgn
    FROM public.vertices v 
    WHERE v.i_rgn = zone_id;
END;
$$;


ALTER FUNCTION public.usp_zone_vertices_list(zone_id integer) OWNER TO postgres;

--
-- Name: usp_zone_vertices_select_by_region(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_zone_vertices_select_by_region(region_id integer) RETURNS TABLE(i_vtx integer, n_x real, n_y real, n_z real, n_ord integer, i_rgn integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY 
    SELECT 
        v.i_vtx, 
        v.n_x, 
        v.n_y, 
        v.n_z, 
        v.n_ord, 
        v.i_rgn
    FROM public.vertices v 
    WHERE v.i_rgn = region_id;
END;
$$;


ALTER FUNCTION public.usp_zone_vertices_select_by_region(region_id integer) OWNER TO postgres;

--
-- Name: usp_zone_vertices_select_by_zone(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.usp_zone_vertices_select_by_zone(zone_id integer) RETURNS TABLE(i_vtx integer, n_x real, n_y real, n_z real, n_ord integer, i_rgn integer, i_zn integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY 
    SELECT 
        v.i_vtx, 
        v.n_x, 
        v.n_y, 
        v.n_z, 
        v.n_ord, 
        v.i_rgn,
        r.i_zn  -- Fetch the zone ID from regions
    FROM public.vertices v
    JOIN public.regions r ON v.i_rgn = r.i_rgn
    WHERE r.i_zn = zone_id;
END;
$$;


ALTER FUNCTION public.usp_zone_vertices_select_by_zone(zone_id integer) OWNER TO postgres;

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
-- Name: USER MAPPING postgres SERVER parcortlsmaint_server; Type: USER MAPPING; Schema: -; Owner: postgres
--

CREATE USER MAPPING FOR postgres SERVER parcortlsmaint_server OPTIONS (
    password 'parcoMCSE04106!',
    "user" 'postgres'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: deviceassmts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.deviceassmts (
    i_asn_dev integer NOT NULL,
    x_id_dev character varying(200) NOT NULL,
    x_id_ent character varying(200) NOT NULL,
    d_asn_bgn timestamp without time zone NOT NULL,
    d_asn_end timestamp without time zone,
    i_rsn integer
);


ALTER TABLE public.deviceassmts OWNER TO postgres;

--
-- Name: deviceassmts_i_asn_dev_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.deviceassmts_i_asn_dev_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.deviceassmts_i_asn_dev_seq OWNER TO postgres;

--
-- Name: deviceassmts_i_asn_dev_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.deviceassmts_i_asn_dev_seq OWNED BY public.deviceassmts.i_asn_dev;


--
-- Name: devices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.devices (
    x_id_dev character varying(200) NOT NULL,
    i_typ_dev integer NOT NULL,
    x_nm_dev character varying(200),
    d_srv_bgn timestamp without time zone,
    d_srv_end timestamp without time zone,
    n_moe_x real,
    n_moe_y real,
    n_moe_z real,
    f_log boolean NOT NULL
);


ALTER TABLE public.devices OWNER TO postgres;

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
-- Name: entities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.entities (
    x_id_ent character varying(200) NOT NULL,
    i_typ_ent integer,
    x_nm_ent character varying(200),
    d_crt timestamp without time zone,
    d_udt timestamp without time zone
);


ALTER TABLE public.entities OWNER TO postgres;

--
-- Name: entity_type_mapping; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.entity_type_mapping (
    old_i_typ_ent character varying NOT NULL,
    new_i_typ_ent integer NOT NULL
);


ALTER TABLE public.entity_type_mapping OWNER TO postgres;

--
-- Name: entity_type_mapping_new_i_typ_ent_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.entity_type_mapping_new_i_typ_ent_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.entity_type_mapping_new_i_typ_ent_seq OWNER TO postgres;

--
-- Name: entity_type_mapping_new_i_typ_ent_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.entity_type_mapping_new_i_typ_ent_seq OWNED BY public.entity_type_mapping.new_i_typ_ent;


--
-- Name: entityassmts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.entityassmts (
    i_asn_ent integer NOT NULL,
    x_id_pnt character varying(200) NOT NULL,
    x_id_chd character varying(200) NOT NULL,
    d_ent_asn_bgn timestamp without time zone NOT NULL,
    d_ent_asn_end timestamp without time zone,
    i_rsn integer
);


ALTER TABLE public.entityassmts OWNER TO postgres;

--
-- Name: entityassmts_i_asn_ent_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.entityassmts_i_asn_ent_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.entityassmts_i_asn_ent_seq OWNER TO postgres;

--
-- Name: entityassmts_i_asn_ent_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.entityassmts_i_asn_ent_seq OWNED BY public.entityassmts.i_asn_ent;


--
-- Name: map_scale; Type: TABLE; Schema: public; Owner: parcoadmin
--

CREATE TABLE public.map_scale (
    id integer NOT NULL,
    map_name character varying(255) NOT NULL,
    point1_x double precision NOT NULL,
    point1_y double precision NOT NULL,
    point2_x double precision NOT NULL,
    point2_y double precision NOT NULL,
    scale double precision NOT NULL
);


ALTER TABLE public.map_scale OWNER TO parcoadmin;

--
-- Name: map_scale_id_seq; Type: SEQUENCE; Schema: public; Owner: parcoadmin
--

CREATE SEQUENCE public.map_scale_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.map_scale_id_seq OWNER TO parcoadmin;

--
-- Name: map_scale_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: parcoadmin
--

ALTER SEQUENCE public.map_scale_id_seq OWNED BY public.map_scale.id;


--
-- Name: maps; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.maps (
    i_map integer NOT NULL,
    x_nm_map character varying(255) NOT NULL,
    x_path character varying(500),
    n_scale real,
    i_zn integer,
    x_format character varying(10) DEFAULT 'GIF'::character varying NOT NULL,
    d_uploaded timestamp without time zone DEFAULT now(),
    min_x real,
    min_y real,
    min_z real,
    max_x real,
    max_y real,
    max_z real,
    lat_origin real,
    lon_origin real,
    img_data bytea,
    is_default boolean DEFAULT false
);


ALTER TABLE public.maps OWNER TO postgres;

--
-- Name: maps_i_map_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.maps_i_map_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.maps_i_map_seq OWNER TO postgres;

--
-- Name: maps_i_map_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.maps_i_map_seq OWNED BY public.maps.i_map;


--
-- Name: regions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.regions (
    i_rgn integer NOT NULL,
    i_zn integer,
    x_nm_rgn character varying(200),
    n_max_x real NOT NULL,
    n_max_y real NOT NULL,
    n_max_z real NOT NULL,
    n_min_x real NOT NULL,
    n_min_y real NOT NULL,
    n_min_z real NOT NULL,
    i_trg integer
);


ALTER TABLE public.regions OWNER TO postgres;

--
-- Name: regions_i_rgn_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.regions_i_rgn_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.regions_i_rgn_seq OWNER TO postgres;

--
-- Name: regions_i_rgn_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.regions_i_rgn_seq OWNED BY public.regions.i_rgn;


--
-- Name: tlkassmtreasons_i_rsn_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tlkassmtreasons_i_rsn_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tlkassmtreasons_i_rsn_seq OWNER TO postgres;

--
-- Name: tlkassmtreasons; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tlkassmtreasons (
    i_rsn integer DEFAULT nextval('public.tlkassmtreasons_i_rsn_seq'::regclass) NOT NULL,
    x_rsn character varying(100) NOT NULL
);


ALTER TABLE public.tlkassmtreasons OWNER TO postgres;

--
-- Name: tlkdevicetypes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tlkdevicetypes (
    i_typ_dev integer NOT NULL,
    x_dsc_dev character varying(50) NOT NULL
);


ALTER TABLE public.tlkdevicetypes OWNER TO postgres;

--
-- Name: tlkdevicetypes_i_typ_dev_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tlkdevicetypes_i_typ_dev_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tlkdevicetypes_i_typ_dev_seq OWNER TO postgres;

--
-- Name: tlkdevicetypes_i_typ_dev_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tlkdevicetypes_i_typ_dev_seq OWNED BY public.tlkdevicetypes.i_typ_dev;


--
-- Name: tlkentitytypes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tlkentitytypes (
    x_dsc_ent character varying(200),
    d_crt timestamp without time zone,
    d_udt timestamp without time zone,
    i_typ_ent integer
);


ALTER TABLE public.tlkentitytypes OWNER TO postgres;

--
-- Name: tlkresources; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tlkresources (
    i_res integer NOT NULL,
    i_typ_res integer NOT NULL,
    x_nm_res character varying(50) NOT NULL,
    x_ip character varying(50) NOT NULL,
    i_prt integer NOT NULL,
    i_rnk integer NOT NULL,
    f_fs boolean,
    f_avg boolean
);


ALTER TABLE public.tlkresources OWNER TO postgres;

--
-- Name: tlkresources_i_res_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tlkresources_i_res_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tlkresources_i_res_seq OWNER TO postgres;

--
-- Name: tlkresources_i_res_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tlkresources_i_res_seq OWNED BY public.tlkresources.i_res;


--
-- Name: tlkresourcetypes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tlkresourcetypes (
    i_typ_res integer NOT NULL,
    x_dsc_res character varying(50) NOT NULL
);


ALTER TABLE public.tlkresourcetypes OWNER TO postgres;

--
-- Name: tlkresourcetypes_i_typ_res_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tlkresourcetypes_i_typ_res_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tlkresourcetypes_i_typ_res_seq OWNER TO postgres;

--
-- Name: tlkresourcetypes_i_typ_res_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tlkresourcetypes_i_typ_res_seq OWNED BY public.tlkresourcetypes.i_typ_res;


--
-- Name: tlktrigdirections; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tlktrigdirections (
    i_dir integer NOT NULL,
    x_dir character varying(50) NOT NULL
);


ALTER TABLE public.tlktrigdirections OWNER TO postgres;

--
-- Name: tlktrigdirections_i_dir_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tlktrigdirections_i_dir_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tlktrigdirections_i_dir_seq OWNER TO postgres;

--
-- Name: tlktrigdirections_i_dir_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tlktrigdirections_i_dir_seq OWNED BY public.tlktrigdirections.i_dir;


--
-- Name: tlkzonetypes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tlkzonetypes (
    i_typ_zn integer NOT NULL,
    x_dsc_zn character varying(50) NOT NULL
);


ALTER TABLE public.tlkzonetypes OWNER TO postgres;

--
-- Name: tlkzonetypes_i_typ_zn_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tlkzonetypes_i_typ_zn_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tlkzonetypes_i_typ_zn_seq OWNER TO postgres;

--
-- Name: tlkzonetypes_i_typ_zn_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tlkzonetypes_i_typ_zn_seq OWNED BY public.tlkzonetypes.i_typ_zn;


--
-- Name: trigger_states; Type: TABLE; Schema: public; Owner: parcoadmin
--

CREATE TABLE public.trigger_states (
    i_trg integer NOT NULL,
    x_id_dev character varying(50) NOT NULL,
    last_state integer DEFAULT 0
);


ALTER TABLE public.trigger_states OWNER TO parcoadmin;

--
-- Name: triggers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.triggers (
    i_trg integer NOT NULL,
    x_nm_trg character varying(200) NOT NULL,
    i_dir integer,
    f_ign boolean NOT NULL,
    ignore_unknowns boolean DEFAULT false
);


ALTER TABLE public.triggers OWNER TO postgres;

--
-- Name: triggers_i_trg_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.triggers_i_trg_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.triggers_i_trg_seq OWNER TO postgres;

--
-- Name: triggers_i_trg_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.triggers_i_trg_seq OWNED BY public.triggers.i_trg;


--
-- Name: vertices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vertices (
    i_vtx integer NOT NULL,
    n_x real NOT NULL,
    n_y real NOT NULL,
    n_z real,
    n_ord integer NOT NULL,
    i_rgn integer
);


ALTER TABLE public.vertices OWNER TO postgres;

--
-- Name: vertices_i_vtx_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.vertices_i_vtx_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vertices_i_vtx_seq OWNER TO postgres;

--
-- Name: vertices_i_vtx_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.vertices_i_vtx_seq OWNED BY public.vertices.i_vtx;


--
-- Name: zones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.zones (
    i_zn integer NOT NULL,
    i_typ_zn integer NOT NULL,
    x_nm_zn character varying(200) NOT NULL,
    i_pnt_zn integer,
    i_map integer
);


ALTER TABLE public.zones OWNER TO postgres;

--
-- Name: zones_i_zn_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.zones_i_zn_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.zones_i_zn_seq OWNER TO postgres;

--
-- Name: zones_i_zn_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.zones_i_zn_seq OWNED BY public.zones.i_zn;


--
-- Name: deviceassmts i_asn_dev; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deviceassmts ALTER COLUMN i_asn_dev SET DEFAULT nextval('public.deviceassmts_i_asn_dev_seq'::regclass);


--
-- Name: entity_type_mapping new_i_typ_ent; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entity_type_mapping ALTER COLUMN new_i_typ_ent SET DEFAULT nextval('public.entity_type_mapping_new_i_typ_ent_seq'::regclass);


--
-- Name: entityassmts i_asn_ent; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entityassmts ALTER COLUMN i_asn_ent SET DEFAULT nextval('public.entityassmts_i_asn_ent_seq'::regclass);


--
-- Name: map_scale id; Type: DEFAULT; Schema: public; Owner: parcoadmin
--

ALTER TABLE ONLY public.map_scale ALTER COLUMN id SET DEFAULT nextval('public.map_scale_id_seq'::regclass);


--
-- Name: maps i_map; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.maps ALTER COLUMN i_map SET DEFAULT nextval('public.maps_i_map_seq'::regclass);


--
-- Name: regions i_rgn; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.regions ALTER COLUMN i_rgn SET DEFAULT nextval('public.regions_i_rgn_seq'::regclass);


--
-- Name: tlkdevicetypes i_typ_dev; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tlkdevicetypes ALTER COLUMN i_typ_dev SET DEFAULT nextval('public.tlkdevicetypes_i_typ_dev_seq'::regclass);


--
-- Name: tlkresources i_res; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tlkresources ALTER COLUMN i_res SET DEFAULT nextval('public.tlkresources_i_res_seq'::regclass);


--
-- Name: tlkresourcetypes i_typ_res; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tlkresourcetypes ALTER COLUMN i_typ_res SET DEFAULT nextval('public.tlkresourcetypes_i_typ_res_seq'::regclass);


--
-- Name: tlktrigdirections i_dir; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tlktrigdirections ALTER COLUMN i_dir SET DEFAULT nextval('public.tlktrigdirections_i_dir_seq'::regclass);


--
-- Name: tlkzonetypes i_typ_zn; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tlkzonetypes ALTER COLUMN i_typ_zn SET DEFAULT nextval('public.tlkzonetypes_i_typ_zn_seq'::regclass);


--
-- Name: triggers i_trg; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.triggers ALTER COLUMN i_trg SET DEFAULT nextval('public.triggers_i_trg_seq'::regclass);


--
-- Name: vertices i_vtx; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vertices ALTER COLUMN i_vtx SET DEFAULT nextval('public.vertices_i_vtx_seq'::regclass);


--
-- Name: zones i_zn; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.zones ALTER COLUMN i_zn SET DEFAULT nextval('public.zones_i_zn_seq'::regclass);


--
-- Data for Name: deviceassmts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.deviceassmts (i_asn_dev, x_id_dev, x_id_ent, d_asn_bgn, d_asn_end, i_rsn) FROM stdin;
1	DEV001	ENT101	2025-02-06 10:30:00	2025-02-06 05:03:54.411254	1
4	DEV001	ENT101	2025-02-06 05:13:54.52593	2025-02-06 05:15:25.999246	1
10	1	Entity2	2004-02-04 14:30:36.63	2025-02-06 05:21:32.625513	1
11	1	ety	2004-02-04 14:30:42.05	2025-02-06 05:21:32.625513	1
5	DEV001	ENT101	2025-02-06 05:26:56.930931	\N	1
\.


--
-- Data for Name: devices; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.devices (x_id_dev, i_typ_dev, x_nm_dev, d_srv_bgn, d_srv_end, n_moe_x, n_moe_y, n_moe_z, f_log) FROM stdin;
DEV001	1	Device 001	2025-02-06 00:06:20.448498	2025-02-07 12:00:00	\N	\N	\N	f
1	1		infinity	\N	\N	\N	\N	f
T456987	6	AllTraqNRU	2025-03-16 21:58:58.189744	\N	55.375	48.80078	0	f
T00991	6	AllTraqNRU	2025-03-16 22:17:35.317209	\N	44.5	58.42578	0	f
\.


--
-- Data for Name: dtproperties; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dtproperties (id, objectid, property, value, uvalue, lvalue, version) FROM stdin;
\.


--
-- Data for Name: entities; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.entities (x_id_ent, i_typ_ent, x_nm_ent, d_crt, d_udt) FROM stdin;
Entity001	1	Test Entity 1	2025-02-05 09:00:00	2025-02-06 09:00:00
Entity003	3	Original Entity Name	2025-02-06 08:00:00	2025-02-06 09:00:00
ENT101	1	Entity 101	2025-02-06 00:08:49.617623	\N
Entity2	1	Entity 2	2025-02-06 05:20:59.393711	\N
ety	1	Entity ety	2025-02-06 05:20:59.393711	\N
ParentEntityID	1	Parent Entity	2025-02-06 05:42:42.970733	\N
ChildEntityID	1	Child Entity	2025-02-06 05:42:42.970733	\N
\.


--
-- Data for Name: entity_type_mapping; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.entity_type_mapping (old_i_typ_ent, new_i_typ_ent) FROM stdin;
Type001	1
\.


--
-- Data for Name: entityassmts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.entityassmts (i_asn_ent, x_id_pnt, x_id_chd, d_ent_asn_bgn, d_ent_asn_end, i_rsn) FROM stdin;
\.


--
-- Data for Name: map_scale; Type: TABLE DATA; Schema: public; Owner: parcoadmin
--

COPY public.map_scale (id, map_name, point1_x, point1_y, point2_x, point2_y, scale) FROM stdin;
\.


--
-- Data for Name: maps; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.maps (i_map, x_nm_map, x_path, n_scale, i_zn, x_format, d_uploaded, min_x, min_y, min_z, max_x, max_y, max_z, lat_origin, lon_origin, img_data, is_default) FROM stdin;
29	Blank for Boca	\N	\N	\N	PNG	2025-03-03 13:43:52.672571	-80	-40	0	160	160	24	0	0	\\x89504e470d0a1a0a0000000d49484452000002d10000025908060000006f2a69b2000000017352474200aece1ce90000000467414d410000b18f0bfc6105000000097048597300000ec400000ec401952b0e1b00003af149444154785eed9b018e248971edf6fe67d39dfc3b0b3bc268d4cb98c2b757e22b120ea0954bc9aa24020824ec3ffef18f7ffc4fb33bfff3c71fdf3e6f36a6bedb53dfeda9eff6d4777f5e47f43be433ff6dfeb3c4eff069efc7eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f05f4774b33bcf127ff7bcd998fa6e4f7db7a7bedb53dffde94bf481dd7f96f81d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320bfeeb886e76e759e2ef9e371b53dfeda9eff6d4777beabb3f7d893eb0fbcf12bfc3a7bd1fbb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c17f1dd1cdee3c4bfcddf36663eabb3df5dd9efa6e4f7df7a72fd10776ff59e277f8b4f763f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf8af23bad99d6789bf7bde6c4c7db7a7bedb53dfeda9effef425fac0ee3f4bfc0e9ff67eec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905ff754437bbf32cf177cf9b8da9eff6d4777beabb3df5dd9fbe441fd8fd6789dfe1d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e0bf8ee866779e25feee79b331f5dd9efa6e4f7db7a7befbd397e803bbff2cf13b7cdafbb1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fcd711ddecceb3c4df3d6f36a6bedb53dfeda9eff6d4777ffa127d60f79f257e874f7b3f76bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82ff3aa29bdd7996f8bbe7cdc6d4777beabb3df5dd9efaee4f5fa20fecfeb3c4eff069efc7eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f05f4774b33bcf127ff7bcd998fa6e4f7db7a7bedb53dffde94bf481dd7f96f81d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320bfe1fafc84dd3344dd3344dd3fcf6f425fac0eebf42bfc1a7bd1fbb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c17f1dd1cdee3c4bfcddf36663eabb3df5dd9efa6e4f7df7a72fd10776ff59e277f8b4f763f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf8af23bad99d6789bf7bde6c4c7db7a7bedb53dfeda9effef425fac0ee3f4bfc0e9ff67eec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905ff754437bbf32cf177cf9b8da9eff6d4777beabb3df5dd9fbe441fd8fd6789dfe1d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e0bf8ee866779e25feee79b331f5dd9efa6e4f7db7a7befbd397e803bbff2cf13b7cdafbb1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fcd711ddecceb3c4df3d6f36a6bedb53dfeda9eff6d4777ffa127d60f79f257e874f7b3f76bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82ff3aa29bdd7996f8bbe7cdc6d4777beabb3df5dd9efaee4f5fa20fecfeb3c4eff069efc7eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f05f4774b33bcf127ff7bcd998fa6e4f7db7a7bedb53dffde94bf481dd7f96f81d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320bfeeb886e76e759e2ef9e371b53dfeda9eff6d4777beabb3f7d893eb0fbcf12bfc3a7bd1fbb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c17f1dd1cdee3c4bfcddf36663eabb3df5dd9efa6e4f7df7a72fd10776ff59e277f8b4f763f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf87fbc22374dd3344dd3344df3dbd397e803bbff0afd069ff67eec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905ff754437bbf32cf177cf9b8da9eff6d4777beabb3df5dd9fbe441fd8fd6789dfe1d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e0bf8ee866779e25feee79b331f5dd9efa6e4f7db7a7befbd397e803bbff2cf13b7cdafbb1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fcd711ddecceb3c4df3d6f36a6bedb53dfeda9eff6d4777ffa127d60f79f257e874f7b3f76bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82ff3aa29bdd7996f8bbe7cdc6d4777beabb3df5dd9efaee4f5fa20fecfeb3c4eff069efc7eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f05f4774b33bcf127ff7bcd998fa6e4f7db7a7bedb53dffde94bf481dd7f96f81d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320bfeeb886e76e759e2ef9e371b53dfeda9eff6d4777beabb3f7d893eb0fbcf12bfc3a7bd1fbb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c17f1dd1cdee3c4bfcddf36663eabb3df5dd9efa6e4f7df7a72fd10776ff59e277f8b4f763f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf8af23bad99d6789bf7bde6c4c7db7a7bedb53dfeda9effef425fac0ee3f4bfc0e9ff67eec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905ff754437bbf32cf177cf9b8da9eff6d4777beabb3df5dd9fbe441fd8fd6789dfe1d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e0fff18adc344dd3344dd334cd6f4f5fa20fecfe2bf41b7cdafbb1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fcd711ddecceb3c4df3d6f36a6bedb53dfeda9eff6d4777ffa127d60f79f257e874f7b3f76bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82ff3aa29bdd7996f8bbe7cdc6d4777beabb3df5dd9efaee4f5fa20fecfeb3c4eff069efc7eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f05f4774b33bcf127ff7bcd998fa6e4f7db7a7bedb53dffde94bf481dd7f96f81d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320bfeeb886e76e759e2ef9e371b53dfeda9eff6d4777beabb3f7d893eb0fbcf12bfc3a7bd1fbb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c17f1dd1cdee3c4bfcddf36663eabb3df5dd9efa6e4f7df7a72fd10776ff59e277f8b4f763f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf8af23bad99d6789bf7bde6c4c7db7a7bedb53dfeda9effef425fac0ee3f4bfc0e9ff67eec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905ff754437bbf32cf177cf9b8da9eff6d4777beabb3df5dd9fbe441fd8fd6789dfe1d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e0bf8ee866779e25feee79b331f5dd9efa6e4f7db7a7befbd397e803bbff2cf13b7cdafbb1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fcd711ddecceb3c4df3d6f36a6bedb53dfeda9eff6d4777ffa127d60f79f257e874f7b3f76bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82ffc72b72d3344dd3344dd334bf3d7d893eb0fbafd06ff069efc7eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f05f4774b33bcf127ff7bcd998fa6e4f7db7a7bedb53dffde94bf481dd7f96f81d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320bfeeb886e76e759e2ef9e371b53dfeda9eff6d4777beabb3f7d893eb0fbcf12bfc3a7bd1fbb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c17f1dd1cdee3c4bfcddf36663eabb3df5dd9efa6e4f7df7a72fd10776ff59e277f8b4f763f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf8af23bad99d6789bf7bde6c4c7db7a7bedb53dfeda9effef425fac0ee3f4bfc0e9ff67eec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ffcb23fa8faff83fe6677ef6bffbe7bff277fc8877f834ff2bd09f7ffc1e9ff67eec7e7d19bb5f5fc6eed797b1fbf565167cfc12dd11edf75b62c6eed797b1fbf565ec7e7d19bb5f5f66c13fffcf397e3d947ff8bf73403ffc1d3fe21d3ecd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905ffb78fe81f07f3ebdff4cb33e2eff811eff069fe57a43ffff83d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf8bff5ff58f85747f4eff077fc8877f834bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fcb78ee8675effa63ffffe1dfe8e1ff10e9fe67f85faf38fdfe3d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82ff3aa27f677e3ea49ff9ce69fefbe659e2ef9e371b53dfeda9eff6d4777beabb3fbff525fa073f0ee87778e73fff219f79d77f96f81d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e0bf75443fe433ff6d7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905ff754437bbf32cf177cf9b8da9eff6d4777beabb3df5dd9fbe441fd8fd6789dfe1d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ffe38b3fffe5efb1f0a3dfc1eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82ff3aa29f79fe45b337cf127ff7bcd998fa6e4f7db7a7bedb53dffdf9e711fdcceff0fc9bde219ff9bff69f257e874f7b3f76bfbe8cddaf2f63f7ebcbd8fdfa320bfebf1cd1bf73482ffce877b0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e0ffdb11fd0cb1f0a3dfc1ee7f05fdf38fdfe3d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82ff7533fffb11fdcc5fb1f0a3dfc1ee7fc5fcf38fdfe3d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82ff752f7f7f443ff31d0b3ffa1decfe57c83ffff83d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf85fb7729109bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f05f47f4f347b339cf127ff7bcd998fa6e4f7db7a7bedb53dffde94bf481dd7f96f81d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d99057ffe887e7edf8f79f8d5fff59fff8aedf7fe1b7ff1bbfe0afbeffd34bfbe8cddaf2f63f7ebcbd8fdfa320bfed7edb81ff9e743f967ffe7e77f85f1f7fe0bf0dbbec3fe7b3fcdaf2f63f7ebcbd8fdfa3276bfbecc82ff753f7e46e41fc7f2cffe8f6784f5f7fe930fe9fb834ff3ebcbd8fdfa3276bfbe8cddaf2fb3e07fdd909f11f9c7c1fce3f7fefaafff0aebeffd27c7effb15fbeffd34bfbe8cddaf2f63f7ebcbd8fdfa320bfed70df939917f3e9a7ffe9b30ffde171fd4f7e1d3fcfa3276bfbe8cddaf2f63f7ebcb2cf85f77e46745fe713cffeeefb6ffde9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fecbfb72566ec7e7d19bb5f5fc6eed797b1fbf56516fcd711fdfcf129f3f311fddd3f5f9b6789bf7bde6c4c7db7a7bedb53dfeda9effebc8ee87778fe4deff0dfe4ff389e7ffd9b30ffde171fd4f7e1d3fcfa3276bfbe8cddaf2f63f7ebcb2cf85f77e46744fe7134fff8bdbffeebbfc2fa7bffc9f1fb7ec5fe7b3fcdaf2f63f7ebcbd8fdfa3276bfbecc82ff7543ee47fef960fed9fff9f95f61fcbdff02fcb6efb0ffde4ff3ebcbd8fdfa3276bfbe8cddaf2fb3e07fdd8ffb917f3e947ff57ffe67df61fcbdffc207f4fd994ff3ebcbd8fdfa3276bfbe8cddaf2fb3e07fdd8fdb917f1cc93f7ee7affeaffffc576cbff7dff88bdff557d87fefa7f9f565ec7e7d19bb5f5fc6eed79759f0bf6ec7ff5ce4effe77ff6fffe7ff981f7ce7ffeafcccffe67f9feff8bff6bf7ed89f7ffc1ef6dffb697e7d19bb5f5fc6eed797b1fbf56516fcafdbf13f17f9bbe3f5eff8d1ef60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ffaf38a27ffeeff077fce877b0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e0ffd71cd13ffe7bfc1d3ffa1decfed78bfdf38fdfe3d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82ff75bbfee722ff7c40ff98bfe347bf83ddff7aa97ffef17b7cdafbb1fbf565ec7e7d19bb5f5fc6eed79759f0bfeed6ff5ce49f8fe79fe71dfe8e97f40eff6dfed70bfdf38fdfe3d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82ff5cad5ffff3df37cf7fb9e6ff7fbe5ee6b7cf9b8da9eff6d4777beabb3df55d9f7ffccfff032b871b57c016dcf80000000049454e44ae426082	f
36	FastAPI2Blank	\N	\N	\N	PNG	2025-03-10 04:43:56.22091	-80	-40	0	160	160	160	0	0	\\x89504e470d0a1a0a0000000d49484452000002d10000025908060000006f2a69b2000000017352474200aece1ce90000000467414d410000b18f0bfc6105000000097048597300000ec400000ec401952b0e1b00003af149444154785eed9b018e248971edf6fe67d39dfc3b0b3bc268d4cb98c2b757e22b120ea0954bc9aa24020824ec3ffef18f7ffc4fb33bfff3c71fdf3e6f36a6bedb53dfeda9eff6d4777f5e47f43be433ff6dfeb3c4eff069efc7eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f05f4774b33bcf127ff7bcd998fa6e4f7db7a7bedb53dffde94bf481dd7f96f81d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320bfeeb886e76e759e2ef9e371b53dfeda9eff6d4777beabb3f7d893eb0fbcf12bfc3a7bd1fbb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c17f1dd1cdee3c4bfcddf36663eabb3df5dd9efa6e4f7df7a72fd10776ff59e277f8b4f763f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf8af23bad99d6789bf7bde6c4c7db7a7bedb53dfeda9effef425fac0ee3f4bfc0e9ff67eec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905ff754437bbf32cf177cf9b8da9eff6d4777beabb3df5dd9fbe441fd8fd6789dfe1d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e0bf8ee866779e25feee79b331f5dd9efa6e4f7db7a7befbd397e803bbff2cf13b7cdafbb1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fcd711ddecceb3c4df3d6f36a6bedb53dfeda9eff6d4777ffa127d60f79f257e874f7b3f76bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82ff3aa29bdd7996f8bbe7cdc6d4777beabb3df5dd9efaee4f5fa20fecfeb3c4eff069efc7eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f05f4774b33bcf127ff7bcd998fa6e4f7db7a7bedb53dffde94bf481dd7f96f81d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320bfe1fafc84dd3344dd3344dd3fcf6f425fac0eebf42bfc1a7bd1fbb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c17f1dd1cdee3c4bfcddf36663eabb3df5dd9efa6e4f7df7a72fd10776ff59e277f8b4f763f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf8af23bad99d6789bf7bde6c4c7db7a7bedb53dfeda9effef425fac0ee3f4bfc0e9ff67eec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905ff754437bbf32cf177cf9b8da9eff6d4777beabb3df5dd9fbe441fd8fd6789dfe1d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e0bf8ee866779e25feee79b331f5dd9efa6e4f7db7a7befbd397e803bbff2cf13b7cdafbb1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fcd711ddecceb3c4df3d6f36a6bedb53dfeda9eff6d4777ffa127d60f79f257e874f7b3f76bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82ff3aa29bdd7996f8bbe7cdc6d4777beabb3df5dd9efaee4f5fa20fecfeb3c4eff069efc7eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f05f4774b33bcf127ff7bcd998fa6e4f7db7a7bedb53dffde94bf481dd7f96f81d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320bfeeb886e76e759e2ef9e371b53dfeda9eff6d4777beabb3f7d893eb0fbcf12bfc3a7bd1fbb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c17f1dd1cdee3c4bfcddf36663eabb3df5dd9efa6e4f7df7a72fd10776ff59e277f8b4f763f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf87fbc22374dd3344dd3344df3dbd397e803bbff0afd069ff67eec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905ff754437bbf32cf177cf9b8da9eff6d4777beabb3df5dd9fbe441fd8fd6789dfe1d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e0bf8ee866779e25feee79b331f5dd9efa6e4f7db7a7befbd397e803bbff2cf13b7cdafbb1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fcd711ddecceb3c4df3d6f36a6bedb53dfeda9eff6d4777ffa127d60f79f257e874f7b3f76bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82ff3aa29bdd7996f8bbe7cdc6d4777beabb3df5dd9efaee4f5fa20fecfeb3c4eff069efc7eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f05f4774b33bcf127ff7bcd998fa6e4f7db7a7bedb53dffde94bf481dd7f96f81d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320bfeeb886e76e759e2ef9e371b53dfeda9eff6d4777beabb3f7d893eb0fbcf12bfc3a7bd1fbb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c17f1dd1cdee3c4bfcddf36663eabb3df5dd9efa6e4f7df7a72fd10776ff59e277f8b4f763f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf8af23bad99d6789bf7bde6c4c7db7a7bedb53dfeda9effef425fac0ee3f4bfc0e9ff67eec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905ff754437bbf32cf177cf9b8da9eff6d4777beabb3df5dd9fbe441fd8fd6789dfe1d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e0fff18adc344dd3344dd334cd6f4f5fa20fecfe2bf41b7cdafbb1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fcd711ddecceb3c4df3d6f36a6bedb53dfeda9eff6d4777ffa127d60f79f257e874f7b3f76bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82ff3aa29bdd7996f8bbe7cdc6d4777beabb3df5dd9efaee4f5fa20fecfeb3c4eff069efc7eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f05f4774b33bcf127ff7bcd998fa6e4f7db7a7bedb53dffde94bf481dd7f96f81d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320bfeeb886e76e759e2ef9e371b53dfeda9eff6d4777beabb3f7d893eb0fbcf12bfc3a7bd1fbb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c17f1dd1cdee3c4bfcddf36663eabb3df5dd9efa6e4f7df7a72fd10776ff59e277f8b4f763f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf8af23bad99d6789bf7bde6c4c7db7a7bedb53dfeda9effef425fac0ee3f4bfc0e9ff67eec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905ff754437bbf32cf177cf9b8da9eff6d4777beabb3df5dd9fbe441fd8fd6789dfe1d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e0bf8ee866779e25feee79b331f5dd9efa6e4f7db7a7befbd397e803bbff2cf13b7cdafbb1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fcd711ddecceb3c4df3d6f36a6bedb53dfeda9eff6d4777ffa127d60f79f257e874f7b3f76bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82ffc72b72d3344dd3344dd334bf3d7d893eb0fbafd06ff069efc7eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f05f4774b33bcf127ff7bcd998fa6e4f7db7a7bedb53dffde94bf481dd7f96f81d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320bfeeb886e76e759e2ef9e371b53dfeda9eff6d4777beabb3f7d893eb0fbcf12bfc3a7bd1fbb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c17f1dd1cdee3c4bfcddf36663eabb3df5dd9efa6e4f7df7a72fd10776ff59e277f8b4f763f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf8af23bad99d6789bf7bde6c4c7db7a7bedb53dfeda9effef425fac0ee3f4bfc0e9ff67eec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ffcb23fa8faff83fe6677ef6bffbe7bff277fc8877f834ff2bd09f7ffc1e9ff67eec7e7d19bb5f5fc6eed797b1fbf565167cfc12dd11edf75b62c6eed797b1fbf565ec7e7d19bb5f5f66c13fffcf397e3d947ff8bf73403ffc1d3fe21d3ecd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905ffb78fe81f07f3ebdff4cb33e2eff811eff069fe57a43ffff83d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf8bff5ff58f85747f4eff077fc8877f834bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fcb78ee8675effa63ffffe1dfe8e1ff10e9fe67f85faf38fdfe3d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82ff3aa27f677e3ea49ff9ce69fefbe659e2ef9e371b53dfeda9eff6d4777beabb3fbff525fa073f0ee87778e73fff219f79d77f96f81d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e0bf75443fe433ff6d7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905ff754437bbf32cf177cf9b8da9eff6d4777beabb3df5dd9fbe441fd8fd6789dfe1d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ffe38b3fffe5efb1f0a3dfc1eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82ff3aa29f79fe45b337cf127ff7bcd998fa6e4f7db7a7bedb53dffdf9e711fdcceff0fc9bde219ff9bff69f257e874f7b3f76bfbe8cddaf2f63f7ebcbd8fdfa320bfebf1cd1bf73482ffce877b0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e0ffdb11fd0cb1f0a3dfc1ee7f05fdf38fdfe3d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82ff7533fffb11fdcc5fb1f0a3dfc1ee7fc5fcf38fdfe3d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82ff752f7f7f443ff31d0b3ffa1decfe57c83ffff83d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf85fb7729109bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f05f47f4f347b339cf127ff7bcd998fa6e4f7db7a7bedb53dffde94bf481dd7f96f81d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d99057ffe887e7edf8f79f8d5fff59fff8aedf7fe1b7ff1bbfe0afbeffd34bfbe8cddaf2f63f7ebcbd8fdfa320bfed7edb81ff9e743f967ffe7e77f85f1f7fe0bf0dbbec3fe7b3fcdaf2f63f7ebcbd8fdfa3276bfbecc82ff753f7e46e41fc7f2cffe8f6784f5f7fe930fe9fb834ff3ebcbd8fdfa3276bfbe8cddaf2fb3e07fdd909f11f9c7c1fce3f7fefaafff0aebeffd27c7effb15fbeffd34bfbe8cddaf2f63f7ebcbd8fdfa320bfed70df939917f3e9a7ffe9b30ffde171fd4f7e1d3fcfa3276bfbe8cddaf2f63f7ebcb2cf85f77e46745fe713cffeeefb6ffde9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fecbfb72566ec7e7d19bb5f5fc6eed797b1fbf56516fcd711fdfcf129f3f311fddd3f5f9b6789bf7bde6c4c7db7a7bedb53dfeda9effebc8ee87778fe4deff0dfe4ff389e7ffd9b30ffde171fd4f7e1d3fcfa3276bfbe8cddaf2f63f7ebcb2cf85f77e46744fe7134fff8bdbffeebbfc2fa7bffc9f1fb7ec5fe7b3fcdaf2f63f7ebcbd8fdfa3276bfbecc82ff7543ee47fef960fed9fff9f95f61fcbdff02fcb6efb0ffde4ff3ebcbd8fdfa3276bfbe8cddaf2fb3e07fdd8ffb917f3e947ff57ffe67df61fcbdffc207f4fd994ff3ebcbd8fdfa3276bfbe8cddaf2fb3e07fdd8fdb917f1cc93f7ee7affeaffffc576cbff7dff88bdff557d87fefa7f9f565ec7e7d19bb5f5fc6eed79759f0bf6ec7ff5ce4effe77ff6fffe7ff981f7ce7ffeafcccffe67f9feff8bff6bf7ed89f7ffc1ef6dffb697e7d19bb5f5fc6eed797b1fbf56516fcafdbf13f17f9bbe3f5eff8d1ef60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ffaf38a27ffeeff077fce877b0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e0ffd71cd13ffe7bfc1d3ffa1decfed78bfdf38fdfe3d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82ff75bbfee722ff7c40ff98bfe347bf83ddff7aa97ffef17b7cdafbb1fbf565ec7e7d19bb5f5fc6eed79759f0bfeed6ff5ce49f8fe79fe71dfe8e97f40eff6dfed70bfdf38fdfe3d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82ff5cad5ffff3df37cf7fb9e6ff7fbe5ee6b7cf9b8da9eff6d4777beabb3df55d9f7ffccfff032b871b57c016dcf80000000049454e44ae426082	f
37	test map upload	\N	\N	\N	PNG	2025-03-12 14:13:29.567532	-80	-40	0	160	160	160	0	0	\\x89504e470d0a1a0a0000000d49484452000002d10000025908060000006f2a69b2000000017352474200aece1ce90000000467414d410000b18f0bfc6105000000097048597300000ec400000ec401952b0e1b00003af149444154785eed9b018e248971edf6fe67d39dfc3b0b3bc268d4cb98c2b757e22b120ea0954bc9aa24020824ec3ffef18f7ffc4fb33bfff3c71fdf3e6f36a6bedb53dfeda9eff6d4777f5e47f43be433ff6dfeb3c4eff069efc7eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f05f4774b33bcf127ff7bcd998fa6e4f7db7a7bedb53dffde94bf481dd7f96f81d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320bfeeb886e76e759e2ef9e371b53dfeda9eff6d4777beabb3f7d893eb0fbcf12bfc3a7bd1fbb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c17f1dd1cdee3c4bfcddf36663eabb3df5dd9efa6e4f7df7a72fd10776ff59e277f8b4f763f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf8af23bad99d6789bf7bde6c4c7db7a7bedb53dfeda9effef425fac0ee3f4bfc0e9ff67eec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905ff754437bbf32cf177cf9b8da9eff6d4777beabb3df5dd9fbe441fd8fd6789dfe1d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e0bf8ee866779e25feee79b331f5dd9efa6e4f7db7a7befbd397e803bbff2cf13b7cdafbb1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fcd711ddecceb3c4df3d6f36a6bedb53dfeda9eff6d4777ffa127d60f79f257e874f7b3f76bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82ff3aa29bdd7996f8bbe7cdc6d4777beabb3df5dd9efaee4f5fa20fecfeb3c4eff069efc7eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f05f4774b33bcf127ff7bcd998fa6e4f7db7a7bedb53dffde94bf481dd7f96f81d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320bfe1fafc84dd3344dd3344dd3fcf6f425fac0eebf42bfc1a7bd1fbb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c17f1dd1cdee3c4bfcddf36663eabb3df5dd9efa6e4f7df7a72fd10776ff59e277f8b4f763f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf8af23bad99d6789bf7bde6c4c7db7a7bedb53dfeda9effef425fac0ee3f4bfc0e9ff67eec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905ff754437bbf32cf177cf9b8da9eff6d4777beabb3df5dd9fbe441fd8fd6789dfe1d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e0bf8ee866779e25feee79b331f5dd9efa6e4f7db7a7befbd397e803bbff2cf13b7cdafbb1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fcd711ddecceb3c4df3d6f36a6bedb53dfeda9eff6d4777ffa127d60f79f257e874f7b3f76bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82ff3aa29bdd7996f8bbe7cdc6d4777beabb3df5dd9efaee4f5fa20fecfeb3c4eff069efc7eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f05f4774b33bcf127ff7bcd998fa6e4f7db7a7bedb53dffde94bf481dd7f96f81d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320bfeeb886e76e759e2ef9e371b53dfeda9eff6d4777beabb3f7d893eb0fbcf12bfc3a7bd1fbb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c17f1dd1cdee3c4bfcddf36663eabb3df5dd9efa6e4f7df7a72fd10776ff59e277f8b4f763f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf87fbc22374dd3344dd3344df3dbd397e803bbff0afd069ff67eec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905ff754437bbf32cf177cf9b8da9eff6d4777beabb3df5dd9fbe441fd8fd6789dfe1d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e0bf8ee866779e25feee79b331f5dd9efa6e4f7db7a7befbd397e803bbff2cf13b7cdafbb1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fcd711ddecceb3c4df3d6f36a6bedb53dfeda9eff6d4777ffa127d60f79f257e874f7b3f76bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82ff3aa29bdd7996f8bbe7cdc6d4777beabb3df5dd9efaee4f5fa20fecfeb3c4eff069efc7eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f05f4774b33bcf127ff7bcd998fa6e4f7db7a7bedb53dffde94bf481dd7f96f81d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320bfeeb886e76e759e2ef9e371b53dfeda9eff6d4777beabb3f7d893eb0fbcf12bfc3a7bd1fbb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c17f1dd1cdee3c4bfcddf36663eabb3df5dd9efa6e4f7df7a72fd10776ff59e277f8b4f763f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf8af23bad99d6789bf7bde6c4c7db7a7bedb53dfeda9effef425fac0ee3f4bfc0e9ff67eec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905ff754437bbf32cf177cf9b8da9eff6d4777beabb3df5dd9fbe441fd8fd6789dfe1d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e0fff18adc344dd3344dd334cd6f4f5fa20fecfe2bf41b7cdafbb1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fcd711ddecceb3c4df3d6f36a6bedb53dfeda9eff6d4777ffa127d60f79f257e874f7b3f76bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82ff3aa29bdd7996f8bbe7cdc6d4777beabb3df5dd9efaee4f5fa20fecfeb3c4eff069efc7eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f05f4774b33bcf127ff7bcd998fa6e4f7db7a7bedb53dffde94bf481dd7f96f81d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320bfeeb886e76e759e2ef9e371b53dfeda9eff6d4777beabb3f7d893eb0fbcf12bfc3a7bd1fbb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c17f1dd1cdee3c4bfcddf36663eabb3df5dd9efa6e4f7df7a72fd10776ff59e277f8b4f763f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf8af23bad99d6789bf7bde6c4c7db7a7bedb53dfeda9effef425fac0ee3f4bfc0e9ff67eec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905ff754437bbf32cf177cf9b8da9eff6d4777beabb3df5dd9fbe441fd8fd6789dfe1d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e0bf8ee866779e25feee79b331f5dd9efa6e4f7db7a7befbd397e803bbff2cf13b7cdafbb1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fcd711ddecceb3c4df3d6f36a6bedb53dfeda9eff6d4777ffa127d60f79f257e874f7b3f76bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82ffc72b72d3344dd3344dd334bf3d7d893eb0fbafd06ff069efc7eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f05f4774b33bcf127ff7bcd998fa6e4f7db7a7bedb53dffde94bf481dd7f96f81d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320bfeeb886e76e759e2ef9e371b53dfeda9eff6d4777beabb3f7d893eb0fbcf12bfc3a7bd1fbb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c17f1dd1cdee3c4bfcddf36663eabb3df5dd9efa6e4f7df7a72fd10776ff59e277f8b4f763f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf8af23bad99d6789bf7bde6c4c7db7a7bedb53dfeda9effef425fac0ee3f4bfc0e9ff67eec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ffcb23fa8faff83fe6677ef6bffbe7bff277fc8877f834ff2bd09f7ffc1e9ff67eec7e7d19bb5f5fc6eed797b1fbf565167cfc12dd11edf75b62c6eed797b1fbf565ec7e7d19bb5f5f66c13fffcf397e3d947ff8bf73403ffc1d3fe21d3ecd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905ffb78fe81f07f3ebdff4cb33e2eff811eff069fe57a43ffff83d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf8bff5ff58f85747f4eff077fc8877f834bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fcb78ee8675effa63ffffe1dfe8e1ff10e9fe67f85faf38fdfe3d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82ff3aa27f677e3ea49ff9ce69fefbe659e2ef9e371b53dfeda9eff6d4777beabb3fbff525fa073f0ee87778e73fff219f79d77f96f81d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e0bf75443fe433ff6d7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905ff754437bbf32cf177cf9b8da9eff6d4777beabb3df5dd9fbe441fd8fd6789dfe1d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fec7e4bccd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ffe38b3fffe5efb1f0a3dfc1eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82ff3aa29f79fe45b337cf127ff7bcd998fa6e4f7db7a7bedb53dffdf9e711fdcceff0fc9bde219ff9bff69f257e874f7b3f76bfbe8cddaf2f63f7ebcbd8fdfa320bfebf1cd1bf73482ffce877b0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e0ffdb11fd0cb1f0a3dfc1ee7f05fdf38fdfe3d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82ff7533fffb11fdcc5fb1f0a3dfc1ee7fc5fcf38fdfe3d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82ff752f7f7f443ff31d0b3ffa1decfe57c83ffff83d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf85fb7729109bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d9905bf23fac0eeb7c48cddaf2f63f7ebcbd8fdfa3276bfbecc82df117d60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ef883eb0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e077441fd8fd9698b1fbf565ec7e7d19bb5f5fc6eed79759f05f47f4f347b339cf127ff7bcd998fa6e4f7db7a7bedb53dffde94bf481dd7f96f81d3eedfdd8fdfa3276bfbe8cddaf2f63f7ebcb2cf81dd10776bf2566ec7e7d19bb5f5fc6eed797b1fbf56516fc8ee803bbdf123376bfbe8cddaf2f63f7ebcbd8fdfa320b7e47f481dd6f8919bb5f5fc6eed797b1fbf565ec7e7d99057ffe887e7edf8f79f8d5fff59fff8aedf7fe1b7ff1bbfe0afbeffd34bfbe8cddaf2f63f7ebcbd8fdfa320bfed7edb81ff9e743f967ffe7e77f85f1f7fe0bf0dbbec3fe7b3fcdaf2f63f7ebcbd8fdfa3276bfbecc82ff753f7e46e41fc7f2cffe8f6784f5f7fe930fe9fb834ff3ebcbd8fdfa3276bfbe8cddaf2fb3e07fdd909f11f9c7c1fce3f7fefaafff0aebeffd27c7effb15fbeffd34bfbe8cddaf2f63f7ebcbd8fdfa320bfed70df939917f3e9a7ffe9b30ffde171fd4f7e1d3fcfa3276bfbe8cddaf2f63f7ebcb2cf85f77e46745fe713cffeeefb6ffde9698b1fbf565ec7e7d19bb5f5fc6eed79759f03ba20fecbfb72566ec7e7d19bb5f5fc6eed797b1fbf56516fcd711fdfcf129f3f311fddd3f5f9b6789bf7bde6c4c7db7a7bedb53dfeda9effebc8ee87778fe4deff0dfe4ff389e7ffd9b30ffde171fd4f7e1d3fcfa3276bfbe8cddaf2f63f7ebcb2cf85f77e46744fe7134fff8bdbffeebbfc2fa7bffc9f1fb7ec5fe7b3fcdaf2f63f7ebcbd8fdfa3276bfbecc82ff7543ee47fef960fed9fff9f95f61fcbdff02fcb6efb0ffde4ff3ebcbd8fdfa3276bfbe8cddaf2fb3e07fdd8ffb917f3e947ff57ffe67df61fcbdffc207f4fd994ff3ebcbd8fdfa3276bfbe8cddaf2fb3e07fdd8fdb917f1cc93f7ee7affeaffffc576cbff7dff88bdff557d87fefa7f9f565ec7e7d19bb5f5fc6eed79759f0bf6ec7ff5ce4effe77ff6fffe7ff981f7ce7ffeafcccffe67f9feff8bff6bf7ed89f7ffc1ef6dffb697e7d19bb5f5fc6eed797b1fbf56516fcafdbf13f17f9bbe3f5eff8d1ef60f75b62c6eed797b1fbf565ec7e7d19bb5f5f66c1ffaf38a27ffeeff077fce877b0fb2d3163f7ebcbd8fdfa3276bfbe8cddaf2fb3e0ffd71cd13ffe7bfc1d3ffa1decfed78bfdf38fdfe3d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82ff75bbfee722ff7c40ff98bfe347bf83ddff7aa97ffef17b7cdafbb1fbf565ec7e7d19bb5f5fc6eed79759f0bfeed6ff5ce49f8fe79fe71dfe8e97f40eff6dfed70bfdf38fdfe3d3de8fddaf2f63f7ebcbd8fdfa3276bfbecc82ff5cad5ffff3df37cf7fb9e6ff7fbe5ee6b7cf9b8da9eff6d4777beabb3df55d9f7ffccfff032b871b57c016dcf80000000049454e44ae426082	f
\.


--
-- Data for Name: regions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.regions (i_rgn, i_zn, x_nm_rgn, n_max_x, n_max_y, n_max_z, n_min_x, n_min_y, n_min_z, i_trg) FROM stdin;
404	409	2503132254CL1	159.79059	159.84741	0	-79.50883	-40.397495	0	\N
405	409	Region for Trigger 50	10	10	10	0	0	0	50
\.


--
-- Data for Name: tlkassmtreasons; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tlkassmtreasons (i_rsn, x_rsn) FROM stdin;
1	Routine Check
\.


--
-- Data for Name: tlkdevicetypes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tlkdevicetypes (i_typ_dev, x_dsc_dev) FROM stdin;
1	Tag
2	Tag with Batt Ind
4	Personel Badge
5	Updated Device Type
6	Receiver
7	Network Hub
8	UPS
9	Security Gateway
10	Local PC
11	Raspberry Pi
12	Barcode Tag
\.


--
-- Data for Name: tlkentitytypes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tlkentitytypes (x_dsc_ent, d_crt, d_udt, i_typ_ent) FROM stdin;
Updated Sample Type	2025-02-06 10:00:00	2025-02-06 16:03:38.727465	1
Auto-Fixed Type	2025-02-07 21:34:56.23069	2025-02-07 21:34:56.23069	3
\.


--
-- Data for Name: tlkresources; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tlkresources (i_res, i_typ_res, x_nm_res, x_ip, i_prt, i_rnk, f_fs, f_avg) FROM stdin;
1	2	Updated Resource Name	192.168.1.101	9090	10	f	f
\.


--
-- Data for Name: tlkresourcetypes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tlkresourcetypes (i_typ_res, x_dsc_res) FROM stdin;
1	R and T Raw FS
2	R and T Averaged FS
3	O Data Raw FS
4	O Data Averaged FS
5	P Data FS
6	P Data Sub
7	R and T Raw Sub
8	R and T Averaged Sub
9	O Data Raw Sub
10	O Data Averaged Sub
\.


--
-- Data for Name: tlktrigdirections; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tlktrigdirections (i_dir, x_dir) FROM stdin;
1	While In
2	While Out
3	On Cross
4	On Enter
5	On Exit
\.


--
-- Data for Name: tlkzonetypes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tlkzonetypes (i_typ_zn, x_dsc_zn) FROM stdin;
6	ODataProximity
7	PDataProximity
9	Demo Zone Type
1	Campus L1
10	Building Outside L2
2	Building L3
3	Floor L4
4	Wing L5
5	Room L6
\.


--
-- Data for Name: trigger_states; Type: TABLE DATA; Schema: public; Owner: parcoadmin
--

COPY public.trigger_states (i_trg, x_id_dev, last_state) FROM stdin;
14	Device001	0
14	DEV001	0
14	1	0
14	AllTraq_2503251632	0
14	AllTraq_2503251633	0
14	AllTraq_2503251634	0
14	AllTraq_2503251635	0
15	Device001	0
15	DEV001	0
15	1	0
15	AllTraq_2503251632	0
15	AllTraq_2503251633	0
15	AllTraq_2503251634	0
15	AllTraq_2503251635	0
16	Device001	0
16	DEV001	0
16	1	0
16	AllTraq_2503251632	0
16	AllTraq_2503251633	0
16	AllTraq_2503251634	0
16	AllTraq_2503251635	0
17	Device001	0
17	DEV001	0
17	1	0
17	AllTraq_2503251632	0
17	AllTraq_2503251633	0
17	AllTraq_2503251634	0
17	AllTraq_2503251635	0
18	Device001	0
18	DEV001	0
18	1	0
18	AllTraq_2503251632	0
18	AllTraq_2503251633	0
18	AllTraq_2503251634	0
18	AllTraq_2503251635	0
19	Device001	0
19	DEV001	0
19	1	0
19	AllTraq_2503251632	0
19	AllTraq_2503251633	0
19	AllTraq_2503251634	0
19	AllTraq_2503251635	0
20	Device001	0
20	DEV001	0
20	1	0
20	AllTraq_2503251632	0
20	AllTraq_2503251633	0
20	AllTraq_2503251634	0
20	AllTraq_2503251635	0
21	Device001	0
21	DEV001	0
21	1	0
21	AllTraq_2503251632	0
21	AllTraq_2503251633	0
21	AllTraq_2503251634	0
21	AllTraq_2503251635	0
22	Device001	0
22	DEV001	0
22	1	0
22	AllTraq_2503251632	0
22	AllTraq_2503251633	0
22	AllTraq_2503251634	0
22	AllTraq_2503251635	0
23	Device001	0
23	DEV001	0
23	1	0
23	AllTraq_2503251632	0
23	AllTraq_2503251633	0
23	AllTraq_2503251634	0
23	AllTraq_2503251635	0
24	Device001	0
24	DEV001	0
24	1	0
24	AllTraq_2503251632	0
24	AllTraq_2503251633	0
24	AllTraq_2503251634	0
24	AllTraq_2503251635	0
25	Device001	0
25	DEV001	0
25	1	0
25	AllTraq_2503251632	0
25	AllTraq_2503251633	0
25	AllTraq_2503251634	0
25	AllTraq_2503251635	0
26	Device001	0
26	DEV001	0
26	1	0
26	AllTraq_2503251632	0
26	AllTraq_2503251633	0
26	AllTraq_2503251634	0
26	AllTraq_2503251635	0
27	Device001	0
27	DEV001	0
27	1	0
27	AllTraq_2503251632	0
27	AllTraq_2503251633	0
27	AllTraq_2503251634	0
27	AllTraq_2503251635	0
28	Device001	0
28	DEV001	0
28	1	0
28	AllTraq_2503251632	0
28	AllTraq_2503251633	0
28	AllTraq_2503251634	0
28	AllTraq_2503251635	0
29	Device001	0
29	DEV001	0
29	1	0
29	AllTraq_2503251632	0
29	AllTraq_2503251633	0
29	AllTraq_2503251634	0
29	AllTraq_2503251635	0
30	Device001	0
30	DEV001	0
30	1	0
30	AllTraq_2503251632	0
30	AllTraq_2503251633	0
30	AllTraq_2503251634	0
30	AllTraq_2503251635	0
31	Device001	0
31	DEV001	0
31	1	0
31	AllTraq_2503251632	0
31	AllTraq_2503251633	0
31	AllTraq_2503251634	0
31	AllTraq_2503251635	0
32	Device001	0
32	DEV001	0
32	1	0
32	AllTraq_2503251632	0
32	AllTraq_2503251633	0
32	AllTraq_2503251634	0
32	AllTraq_2503251635	0
33	Device001	0
33	DEV001	0
33	1	0
33	AllTraq_2503251632	0
33	AllTraq_2503251633	0
33	AllTraq_2503251634	0
33	AllTraq_2503251635	0
34	Device001	0
34	DEV001	0
34	1	0
34	AllTraq_2503251632	0
34	AllTraq_2503251633	0
34	AllTraq_2503251634	0
34	AllTraq_2503251635	0
35	Device001	0
35	DEV001	0
35	1	0
35	AllTraq_2503251632	0
35	AllTraq_2503251633	0
35	AllTraq_2503251634	0
35	AllTraq_2503251635	0
36	Device001	0
36	DEV001	0
36	1	0
36	AllTraq_2503251632	0
36	AllTraq_2503251633	0
36	AllTraq_2503251634	0
36	AllTraq_2503251635	0
37	Device001	0
37	DEV001	0
37	1	0
37	AllTraq_2503251632	0
37	AllTraq_2503251633	0
37	AllTraq_2503251634	0
37	AllTraq_2503251635	0
38	Device001	0
38	DEV001	0
38	1	0
38	AllTraq_2503251632	0
38	AllTraq_2503251633	0
38	AllTraq_2503251634	0
38	AllTraq_2503251635	0
39	Device001	0
39	DEV001	0
39	1	0
39	AllTraq_2503251632	0
39	AllTraq_2503251633	0
39	AllTraq_2503251634	0
39	AllTraq_2503251635	0
40	Device001	0
40	DEV001	0
40	1	0
40	AllTraq_2503251632	0
40	AllTraq_2503251633	0
40	AllTraq_2503251634	0
40	AllTraq_2503251635	0
41	Device001	0
41	DEV001	0
41	1	0
41	AllTraq_2503251632	0
41	AllTraq_2503251633	0
41	AllTraq_2503251634	0
41	AllTraq_2503251635	0
42	Device001	0
42	DEV001	0
42	1	0
42	AllTraq_2503251632	0
42	AllTraq_2503251633	0
42	AllTraq_2503251634	0
42	AllTraq_2503251635	0
43	Device001	0
43	DEV001	0
43	1	0
43	AllTraq_2503251632	0
43	AllTraq_2503251633	0
43	AllTraq_2503251634	0
43	AllTraq_2503251635	0
44	Device001	0
44	DEV001	0
44	1	0
44	AllTraq_2503251632	0
44	AllTraq_2503251633	0
44	AllTraq_2503251634	0
44	AllTraq_2503251635	0
45	Device001	0
45	DEV001	0
45	1	0
45	AllTraq_2503251632	0
45	AllTraq_2503251633	0
45	AllTraq_2503251634	0
45	AllTraq_2503251635	0
46	Device001	0
46	DEV001	0
46	1	0
46	AllTraq_2503251632	0
46	AllTraq_2503251633	0
46	AllTraq_2503251634	0
46	AllTraq_2503251635	0
47	Device001	0
47	DEV001	0
47	1	0
47	AllTraq_2503251632	0
47	AllTraq_2503251633	0
47	AllTraq_2503251634	0
47	AllTraq_2503251635	0
48	Device001	0
48	DEV001	0
48	1	0
48	AllTraq_2503251632	0
48	AllTraq_2503251633	0
48	AllTraq_2503251634	0
48	AllTraq_2503251635	0
49	Device001	0
49	DEV001	0
49	1	0
49	AllTraq_2503251632	0
49	AllTraq_2503251633	0
49	AllTraq_2503251634	0
49	AllTraq_2503251635	0
50	Device001	0
50	DEV001	0
50	1	0
50	AllTraq_2503251632	0
50	AllTraq_2503251633	0
50	AllTraq_2503251634	0
50	AllTraq_2503251635	0
\.


--
-- Data for Name: triggers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.triggers (i_trg, x_nm_trg, i_dir, f_ign, ignore_unknowns) FROM stdin;
1	test_trigger	1	f	f
3	Manual_Trigger_Test	2	f	f
5	No_ID_Trigger	3	f	f
6	Debug_Trigger	2	f	f
7	Fixed_Trigger_Test	2	f	f
8	Another_Test_Trigger	3	f	f
14	CLI_Test_Trigger_3	2	f	f
15	CLI_Test_Trigger_4	2	f	f
16	CLI_Test_Trigger_5	2	f	f
17	CLI_Test_Trigger_6	2	f	f
18	CLI_Test_Trigger_7	2	f	f
19	CLI_Test_Trigger_8	2	f	f
20	CLI_Test_Trigger_9	2	f	f
21	CLI_Test_Trigger_10	2	f	f
22	CLI_Test_Trigger_20	2	f	f
23	Echo	1	t	f
24	Gulf	1	t	f
25	Hotel	1	t	f
26	India	1	t	f
27	Junior	1	t	f
28	kilo	1	t	f
29	Nancy	1	t	f
30	oscar	1	t	f
31	queen	1	t	f
32	Tango	1	t	f
33	echo	1	t	f
34	foxtrot	3	t	f
35	hotel	3	t	f
36	india	5	t	f
37	Delta	1	t	f
38	zulubravo	1	t	f
39	zulufoxtrot	1	t	f
40	zoezoe	1	t	f
41	Room0Trigger	1	t	f
42	bobfapi2cl1	1	t	f
43	testok	1	t	f
44	bobzoe	1	t	f
45	bobzeoleaf	1	t	f
46	yoyoyo1	1	t	f
47	0000ytyt	1	t	f
48	5454545	1	t	f
49	2503121	1	t	f
50	2503132255t1	1	t	f
\.


--
-- Data for Name: vertices; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.vertices (i_vtx, n_x, n_y, n_z, n_ord, i_rgn) FROM stdin;
2032	-79.068436	-40.397495	0	1	404
2033	-79.50883	159.84741	0	2	404
2034	159.79059	159.6762	0	3	404
2035	159.76617	-39.789055	0	4	404
2036	-79.068436	-40.397495	0	5	404
\.


--
-- Data for Name: zones; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.zones (i_zn, i_typ_zn, x_nm_zn, i_pnt_zn, i_map) FROM stdin;
409	1	2503132254CL1	\N	29
\.


--
-- Name: deviceassmts_i_asn_dev_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.deviceassmts_i_asn_dev_seq', 14, true);


--
-- Name: entity_type_mapping_new_i_typ_ent_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.entity_type_mapping_new_i_typ_ent_seq', 1, true);


--
-- Name: entityassmts_i_asn_ent_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.entityassmts_i_asn_ent_seq', 2, true);


--
-- Name: map_scale_id_seq; Type: SEQUENCE SET; Schema: public; Owner: parcoadmin
--

SELECT pg_catalog.setval('public.map_scale_id_seq', 1, false);


--
-- Name: maps_i_map_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.maps_i_map_seq', 37, true);


--
-- Name: regions_i_rgn_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.regions_i_rgn_seq', 406, true);


--
-- Name: tlkassmtreasons_i_rsn_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tlkassmtreasons_i_rsn_seq', 3, true);


--
-- Name: tlkdevicetypes_i_typ_dev_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tlkdevicetypes_i_typ_dev_seq', 6, true);


--
-- Name: tlkresources_i_res_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tlkresources_i_res_seq', 1, true);


--
-- Name: tlkresourcetypes_i_typ_res_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tlkresourcetypes_i_typ_res_seq', 1, false);


--
-- Name: tlktrigdirections_i_dir_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tlktrigdirections_i_dir_seq', 1, false);


--
-- Name: tlkzonetypes_i_typ_zn_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tlkzonetypes_i_typ_zn_seq', 9, true);


--
-- Name: triggers_i_trg_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.triggers_i_trg_seq', 50, true);


--
-- Name: vertices_i_vtx_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.vertices_i_vtx_seq', 2040, true);


--
-- Name: zones_i_zn_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.zones_i_zn_seq', 410, true);


--
-- Name: deviceassmts deviceassmts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deviceassmts
    ADD CONSTRAINT deviceassmts_pkey PRIMARY KEY (i_asn_dev);


--
-- Name: devices devices_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_pkey PRIMARY KEY (x_id_dev);


--
-- Name: entities entities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entities
    ADD CONSTRAINT entities_pkey PRIMARY KEY (x_id_ent);


--
-- Name: entity_type_mapping entity_type_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entity_type_mapping
    ADD CONSTRAINT entity_type_mapping_pkey PRIMARY KEY (old_i_typ_ent);


--
-- Name: entityassmts entityassmts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entityassmts
    ADD CONSTRAINT entityassmts_pkey PRIMARY KEY (i_asn_ent);


--
-- Name: map_scale map_scale_pkey; Type: CONSTRAINT; Schema: public; Owner: parcoadmin
--

ALTER TABLE ONLY public.map_scale
    ADD CONSTRAINT map_scale_pkey PRIMARY KEY (id);


--
-- Name: maps maps_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.maps
    ADD CONSTRAINT maps_pkey PRIMARY KEY (i_map);


--
-- Name: regions regions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.regions
    ADD CONSTRAINT regions_pkey PRIMARY KEY (i_rgn);


--
-- Name: tlkassmtreasons tlkassmtreasons_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tlkassmtreasons
    ADD CONSTRAINT tlkassmtreasons_pkey PRIMARY KEY (i_rsn);


--
-- Name: tlkdevicetypes tlkdevicetypes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tlkdevicetypes
    ADD CONSTRAINT tlkdevicetypes_pkey PRIMARY KEY (i_typ_dev);


--
-- Name: tlkresources tlkresources_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tlkresources
    ADD CONSTRAINT tlkresources_pkey PRIMARY KEY (i_res);


--
-- Name: tlkresourcetypes tlkresourcetypes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tlkresourcetypes
    ADD CONSTRAINT tlkresourcetypes_pkey PRIMARY KEY (i_typ_res);


--
-- Name: tlktrigdirections tlktrigdirections_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tlktrigdirections
    ADD CONSTRAINT tlktrigdirections_pkey PRIMARY KEY (i_dir);


--
-- Name: tlkzonetypes tlkzonetypes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tlkzonetypes
    ADD CONSTRAINT tlkzonetypes_pkey PRIMARY KEY (i_typ_zn);


--
-- Name: trigger_states trigger_states_pkey; Type: CONSTRAINT; Schema: public; Owner: parcoadmin
--

ALTER TABLE ONLY public.trigger_states
    ADD CONSTRAINT trigger_states_pkey PRIMARY KEY (i_trg, x_id_dev);


--
-- Name: triggers triggers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.triggers
    ADD CONSTRAINT triggers_pkey PRIMARY KEY (i_trg);


--
-- Name: tlkentitytypes unique_i_typ_ent; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tlkentitytypes
    ADD CONSTRAINT unique_i_typ_ent UNIQUE (i_typ_ent);


--
-- Name: triggers unique_trigger_name; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.triggers
    ADD CONSTRAINT unique_trigger_name UNIQUE (x_nm_trg);


--
-- Name: vertices vertices_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vertices
    ADD CONSTRAINT vertices_pkey PRIMARY KEY (i_vtx);


--
-- Name: zones zones_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.zones
    ADD CONSTRAINT zones_pkey PRIMARY KEY (i_zn);


--
-- Name: deviceassmts fk_deviceassmts_devices; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deviceassmts
    ADD CONSTRAINT fk_deviceassmts_devices FOREIGN KEY (x_id_dev) REFERENCES public.devices(x_id_dev);


--
-- Name: deviceassmts fk_deviceassmts_entities; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deviceassmts
    ADD CONSTRAINT fk_deviceassmts_entities FOREIGN KEY (x_id_ent) REFERENCES public.entities(x_id_ent);


--
-- Name: deviceassmts fk_deviceassmts_tlkassmtreasons; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deviceassmts
    ADD CONSTRAINT fk_deviceassmts_tlkassmtreasons FOREIGN KEY (i_rsn) REFERENCES public.tlkassmtreasons(i_rsn);


--
-- Name: entities fk_entities_tlkentitytypes; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entities
    ADD CONSTRAINT fk_entities_tlkentitytypes FOREIGN KEY (i_typ_ent) REFERENCES public.tlkentitytypes(i_typ_ent);


--
-- Name: entityassmts fk_entityassmts_entities; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entityassmts
    ADD CONSTRAINT fk_entityassmts_entities FOREIGN KEY (x_id_pnt) REFERENCES public.entities(x_id_ent);


--
-- Name: entityassmts fk_entityassmts_entities1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entityassmts
    ADD CONSTRAINT fk_entityassmts_entities1 FOREIGN KEY (x_id_chd) REFERENCES public.entities(x_id_ent);


--
-- Name: entityassmts fk_entityassmts_tlkassmtreasons; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entityassmts
    ADD CONSTRAINT fk_entityassmts_tlkassmtreasons FOREIGN KEY (i_rsn) REFERENCES public.tlkassmtreasons(i_rsn);


--
-- Name: tlkresources fk_tlkresources_tlkresourcetypes; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tlkresources
    ADD CONSTRAINT fk_tlkresources_tlkresourcetypes FOREIGN KEY (i_typ_res) REFERENCES public.tlkresourcetypes(i_typ_res);


--
-- Name: zones fk_zones_zones; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.zones
    ADD CONSTRAINT fk_zones_zones FOREIGN KEY (i_pnt_zn) REFERENCES public.zones(i_zn);


--
-- Name: regions regions_i_trg_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.regions
    ADD CONSTRAINT regions_i_trg_fkey FOREIGN KEY (i_trg) REFERENCES public.triggers(i_trg);


--
-- Name: regions regions_i_zn_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.regions
    ADD CONSTRAINT regions_i_zn_fkey FOREIGN KEY (i_zn) REFERENCES public.zones(i_zn);


--
-- Name: trigger_states trigger_states_i_trg_fkey; Type: FK CONSTRAINT; Schema: public; Owner: parcoadmin
--

ALTER TABLE ONLY public.trigger_states
    ADD CONSTRAINT trigger_states_i_trg_fkey FOREIGN KEY (i_trg) REFERENCES public.triggers(i_trg) ON DELETE CASCADE;


--
-- Name: triggers triggers_i_dir_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.triggers
    ADD CONSTRAINT triggers_i_dir_fkey FOREIGN KEY (i_dir) REFERENCES public.tlktrigdirections(i_dir);


--
-- Name: vertices vertices_i_rgn_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vertices
    ADD CONSTRAINT vertices_i_rgn_fkey FOREIGN KEY (i_rgn) REFERENCES public.regions(i_rgn);


--
-- Name: zones zones_i_map_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.zones
    ADD CONSTRAINT zones_i_map_fkey FOREIGN KEY (i_map) REFERENCES public.maps(i_map);


--
-- Name: zones zones_i_typ_zn_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.zones
    ADD CONSTRAINT zones_i_typ_zn_fkey FOREIGN KEY (i_typ_zn) REFERENCES public.tlkzonetypes(i_typ_zn);


--
-- Name: DATABASE "ParcoRTLSMaint"; Type: ACL; Schema: -; Owner: postgres
--

GRANT ALL ON DATABASE "ParcoRTLSMaint" TO adminparco;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT USAGE ON SCHEMA public TO parcoadmin;


--
-- Name: FUNCTION usp_region_add(p_i_rgn integer, p_i_zn integer, p_x_nm_rgn character varying, p_n_max_x real, p_n_max_y real, p_n_max_z real, p_n_min_x real, p_n_min_y real, p_n_min_z real, p_i_trg integer); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.usp_region_add(p_i_rgn integer, p_i_zn integer, p_x_nm_rgn character varying, p_n_max_x real, p_n_max_y real, p_n_max_z real, p_n_min_x real, p_n_min_y real, p_n_min_z real, p_i_trg integer) TO parcoadmin;


--
-- Name: FUNCTION usp_zone_add(i_typ_zn integer, x_nm_zn character varying, i_pnt_zn integer); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.usp_zone_add(i_typ_zn integer, x_nm_zn character varying, i_pnt_zn integer) TO parcoadmin;


--
-- Name: FUNCTION usp_zone_select_all(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.usp_zone_select_all() TO parcoadmin;


--
-- Name: TABLE maps; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.maps TO parcoadmin;


--
-- Name: TABLE regions; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.regions TO parcoadmin;


--
-- Name: TABLE tlkzonetypes; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.tlkzonetypes TO parcoadmin;


--
-- Name: TABLE vertices; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.vertices TO parcoadmin;


--
-- Name: TABLE zones; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.zones TO parcoadmin;


--
-- PostgreSQL database dump complete
--

--
-- Database "postgres" dump
--

\connect postgres

--
-- PostgreSQL database dump
--

-- Dumped from database version 16.8 (Ubuntu 16.8-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.8 (Ubuntu 16.8-0ubuntu0.24.04.1)

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
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database cluster dump complete
--

