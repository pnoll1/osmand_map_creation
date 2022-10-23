--
-- PostgreSQL database dump
--

-- Dumped from database version 14.5 (Debian 14.5-2)
-- Dumped by pg_dump version 14.5 (Debian 14.5-2)

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
-- Name: aa_merge_oa_addresses_city; Type: TABLE; Schema: public; Owner: pat
--

CREATE TABLE public.aa_merge_oa_addresses_city (
    ogc_fid integer,
    hash character varying,
    number character varying,
    street character varying,
    unit character varying,
    city character varying,
    district character varying,
    region character varying,
    postcode character varying,
    id character varying,
    wkb_geometry public.geometry(Point,4326)
);


ALTER TABLE public.aa_merge_oa_addresses_city OWNER TO pat;

--
-- Data for Name: aa_merge_oa_addresses_city; Type: TABLE DATA; Schema: public; Owner: pat
--

COPY public.aa_merge_oa_addresses_city (ogc_fid, hash, number, street, unit, city, district, region, postcode, id, wkb_geometry) FROM stdin;
1	e8605a496593386e	119	NW  41ST ST		SEATTLE	KING		98107	324731.0	0101000020E61000003BEFB556EA965EC03EFC4685FBD34740
\.


--
-- PostgreSQL database dump complete
--

