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
-- Name: aa_merge_oa_addresses_city_temp; Type: TABLE; Schema: public; Owner: pat
--

CREATE TABLE public.aa_merge_oa_addresses_city_temp (
    ogc_fid integer NOT NULL,
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


ALTER TABLE public.aa_merge_oa_addresses_city_temp OWNER TO pat;

--
-- Name: aa_merge_oa_addresses_city_temp_ogc_fid_seq; Type: SEQUENCE; Schema: public; Owner: pat
--

CREATE SEQUENCE public.aa_merge_oa_addresses_city_temp_ogc_fid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.aa_merge_oa_addresses_city_temp_ogc_fid_seq OWNER TO pat;

--
-- Name: aa_merge_oa_addresses_city_temp_ogc_fid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pat
--

ALTER SEQUENCE public.aa_merge_oa_addresses_city_temp_ogc_fid_seq OWNED BY public.aa_merge_oa_addresses_city_temp.ogc_fid;


--
-- Name: aa_merge_oa_addresses_city_temp ogc_fid; Type: DEFAULT; Schema: public; Owner: pat
--

ALTER TABLE ONLY public.aa_merge_oa_addresses_city_temp ALTER COLUMN ogc_fid SET DEFAULT nextval('public.aa_merge_oa_addresses_city_temp_ogc_fid_seq'::regclass);


--
-- Data for Name: aa_merge_oa_addresses_city_temp; Type: TABLE DATA; Schema: public; Owner: pat
--

COPY public.aa_merge_oa_addresses_city_temp (ogc_fid, hash, number, street, unit, city, district, region, postcode, id, wkb_geometry) FROM stdin;
1	e8605a496593386e	119	NW  41ST ST		SEATTLE	KING		98107	324731.0	0101000020E61000003BEFB556EA965EC03EFC4685FBD34740
2	87d28792bee6b164	115	NW  41ST ST		SEATTLE	KING		98107	316864.0	0101000020E6100000DD7C23BAE7965EC0FC3ACB87FBD34740
\.


--
-- Name: aa_merge_oa_addresses_city_temp_ogc_fid_seq; Type: SEQUENCE SET; Schema: public; Owner: pat
--

SELECT pg_catalog.setval('public.aa_merge_oa_addresses_city_temp_ogc_fid_seq', 2, true);


--
-- Name: aa_merge_oa_addresses_city_temp aa_merge_oa_addresses_city_temp_pkey; Type: CONSTRAINT; Schema: public; Owner: pat
--

ALTER TABLE ONLY public.aa_merge_oa_addresses_city_temp
    ADD CONSTRAINT aa_merge_oa_addresses_city_temp_pkey PRIMARY KEY (ogc_fid);


--
-- Name: aa_merge_oa_addresses_city_temp_wkb_geometry_geom_idx; Type: INDEX; Schema: public; Owner: pat
--

CREATE INDEX aa_merge_oa_addresses_city_temp_wkb_geometry_geom_idx ON public.aa_merge_oa_addresses_city_temp USING gist (wkb_geometry);


--
-- PostgreSQL database dump complete
--

