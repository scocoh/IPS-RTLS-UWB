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
-- Name: component_versions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.component_versions (
    name character varying(255) NOT NULL,
    version character varying(20) NOT NULL,
    created character varying(6) NOT NULL,
    modified character varying(6) NOT NULL,
    creator character varying(50) NOT NULL,
    modified_by character varying(50) NOT NULL,
    description text,
    location text NOT NULL,
    role character varying(50) NOT NULL,
    status character varying(50) DEFAULT 'Active'::character varying,
    dependent boolean DEFAULT true NOT NULL
);


--
-- Name: trigger_states; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.trigger_states (
    i_trg integer NOT NULL,
    x_id_dev character varying(50) NOT NULL,
    last_state integer DEFAULT 0
);


--
-- Name: component_versions component_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.component_versions
    ADD CONSTRAINT component_versions_pkey PRIMARY KEY (name, role, location);


--
-- Name: trigger_states trigger_states_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.trigger_states
    ADD CONSTRAINT trigger_states_pkey PRIMARY KEY (i_trg, x_id_dev);


--
-- Name: trigger_states trigger_states_i_trg_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.trigger_states
    ADD CONSTRAINT trigger_states_i_trg_fkey FOREIGN KEY (i_trg) REFERENCES public.triggers(i_trg) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

