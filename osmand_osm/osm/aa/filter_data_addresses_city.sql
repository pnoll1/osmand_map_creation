--
-- PostgreSQL database dump
--

-- Dumped from database version 14.4 (Debian 14.4-1+b1)
-- Dumped by pg_dump version 14.4 (Debian 14.4-1+b1)

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
-- Name: aa_filter_data_addresses_city; Type: TABLE; Schema: public; Owner: pat
--

CREATE TABLE public.aa_filter_data_addresses_city (
    ogc_fid integer NOT NULL,
    id character varying,
    unit character varying,
    number character varying,
    street character varying,
    city character varying,
    district character varying,
    region character varying,
    postcode character varying,
    hash character varying,
    wkb_geometry public.geometry(Point,4326)
);


ALTER TABLE public.aa_filter_data_addresses_city OWNER TO pat;

--
-- Name: aa_filter_data_addresses_city_ogc_fid_seq; Type: SEQUENCE; Schema: public; Owner: pat
--

CREATE SEQUENCE public.aa_filter_data_addresses_city_ogc_fid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.aa_filter_data_addresses_city_ogc_fid_seq OWNER TO pat;

--
-- Name: aa_filter_data_addresses_city_ogc_fid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pat
--

ALTER SEQUENCE public.aa_filter_data_addresses_city_ogc_fid_seq OWNED BY public.aa_filter_data_addresses_city.ogc_fid;


--
-- Name: aa_filter_data_addresses_city ogc_fid; Type: DEFAULT; Schema: public; Owner: pat
--

ALTER TABLE ONLY public.aa_filter_data_addresses_city ALTER COLUMN ogc_fid SET DEFAULT nextval('public.aa_filter_data_addresses_city_ogc_fid_seq'::regclass);


--
-- Data for Name: aa_filter_data_addresses_city; Type: TABLE DATA; Schema: public; Owner: pat
--

COPY public.aa_filter_data_addresses_city (ogc_fid, id, unit, number, street, city, district, region, postcode, hash, wkb_geometry) FROM stdin;
1			1	Di Mario Dr				02904	908f551defc1295a	0101000020E610000037F0B446CEDA51C04D593CABBBED4440
2	0100101061763020-5		SN	CALLE EMILIO GARCÍA	ARELLANO	Aguascalientes	Aguascalientes		59a2672f7f81bc31	0101000020E6100000F1DB6B9CA89159C01C19F55A1ACD3540
3			--	Linwood Ave				02907	e1262d57e0077c2e	0101000020E6100000430F6BE0FDDB51C0224212AC60E74440
\.


--
-- Name: aa_filter_data_addresses_city_ogc_fid_seq; Type: SEQUENCE SET; Schema: public; Owner: pat
--

SELECT pg_catalog.setval('public.aa_filter_data_addresses_city_ogc_fid_seq', 3, true);


--
-- Name: aa_filter_data_addresses_city aa_filter_data_addresses_city_pkey; Type: CONSTRAINT; Schema: public; Owner: pat
--

ALTER TABLE ONLY public.aa_filter_data_addresses_city
    ADD CONSTRAINT aa_filter_data_addresses_city_pkey PRIMARY KEY (ogc_fid);


--
-- Name: aa_filter_data_addresses_city_wkb_geometry_geom_idx; Type: INDEX; Schema: public; Owner: pat
--

CREATE INDEX aa_filter_data_addresses_city_wkb_geometry_geom_idx ON public.aa_filter_data_addresses_city USING gist (wkb_geometry);


--
-- PostgreSQL database dump complete
--

