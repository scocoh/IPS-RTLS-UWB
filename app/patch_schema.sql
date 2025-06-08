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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: event_log; Type: TABLE; Schema: public; Owner: -
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


--
-- Name: event_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.event_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: event_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.event_log_id_seq OWNED BY public.event_log.id;


--
-- Name: tlk_event_reason; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tlk_event_reason (
    id integer NOT NULL,
    description text NOT NULL
);


--
-- Name: tlk_event_reason_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tlk_event_reason_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tlk_event_reason_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tlk_event_reason_id_seq OWNED BY public.tlk_event_reason.id;


--
-- Name: tlk_event_type; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tlk_event_type (
    id integer NOT NULL,
    name text NOT NULL
);


--
-- Name: tlk_event_type_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tlk_event_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tlk_event_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tlk_event_type_id_seq OWNED BY public.tlk_event_type.id;


--
-- Name: tlk_rules; Type: TABLE; Schema: public; Owner: -
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


--
-- Name: TABLE tlk_rules; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.tlk_rules IS 'Stores rules for TETSE to evaluate events and trigger actions';


--
-- Name: COLUMN tlk_rules.conditions; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.tlk_rules.conditions IS 'JSONB object specifying conditions (e.g., trigger, zone, entity_status)';


--
-- Name: COLUMN tlk_rules.actions; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.tlk_rules.actions IS 'JSONB array of actions (e.g., mqtt_publish with topic and payload)';


--
-- Name: tlk_rules_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tlk_rules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tlk_rules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tlk_rules_id_seq OWNED BY public.tlk_rules.id;


--
-- Name: event_log id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.event_log ALTER COLUMN id SET DEFAULT nextval('public.event_log_id_seq'::regclass);


--
-- Name: tlk_event_reason id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tlk_event_reason ALTER COLUMN id SET DEFAULT nextval('public.tlk_event_reason_id_seq'::regclass);


--
-- Name: tlk_event_type id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tlk_event_type ALTER COLUMN id SET DEFAULT nextval('public.tlk_event_type_id_seq'::regclass);


--
-- Name: tlk_rules id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tlk_rules ALTER COLUMN id SET DEFAULT nextval('public.tlk_rules_id_seq'::regclass);


--
-- Name: event_log event_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.event_log
    ADD CONSTRAINT event_log_pkey PRIMARY KEY (id);


--
-- Name: tlk_event_reason tlk_event_reason_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tlk_event_reason
    ADD CONSTRAINT tlk_event_reason_pkey PRIMARY KEY (id);


--
-- Name: tlk_event_type tlk_event_type_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tlk_event_type
    ADD CONSTRAINT tlk_event_type_name_key UNIQUE (name);


--
-- Name: tlk_event_type tlk_event_type_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tlk_event_type
    ADD CONSTRAINT tlk_event_type_pkey PRIMARY KEY (id);


--
-- Name: tlk_rules tlk_rules_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tlk_rules
    ADD CONSTRAINT tlk_rules_name_key UNIQUE (name);


--
-- Name: tlk_rules tlk_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tlk_rules
    ADD CONSTRAINT tlk_rules_pkey PRIMARY KEY (id);


--
-- Name: idx_eventlog_entity_ts; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_eventlog_entity_ts ON public.event_log USING btree (entity_id, ts DESC);


--
-- Name: idx_eventlog_type_ts; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_eventlog_type_ts ON public.event_log USING btree (event_type_id, ts DESC);


--
-- Name: idx_tlk_rules_is_enabled_priority; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tlk_rules_is_enabled_priority ON public.tlk_rules USING btree (is_enabled, priority DESC);


--
-- Name: event_log fk_event_reason; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.event_log
    ADD CONSTRAINT fk_event_reason FOREIGN KEY (reason_id) REFERENCES public.tlk_event_reason(id);


--
-- Name: event_log fk_event_type; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.event_log
    ADD CONSTRAINT fk_event_type FOREIGN KEY (event_type_id) REFERENCES public.tlk_event_type(id);


--
-- PostgreSQL database dump complete
--

