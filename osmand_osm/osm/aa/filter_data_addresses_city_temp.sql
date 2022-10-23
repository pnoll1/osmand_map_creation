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
-- Name: aa_filter_data_addresses_city_temp; Type: TABLE; Schema: public; Owner: pat
--

CREATE TABLE public.aa_filter_data_addresses_city_temp (
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


ALTER TABLE public.aa_filter_data_addresses_city_temp OWNER TO pat;

--
-- Name: aa_filter_data_addresses_city_temp_ogc_fid_seq; Type: SEQUENCE; Schema: public; Owner: pat
--

CREATE SEQUENCE public.aa_filter_data_addresses_city_temp_ogc_fid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.aa_filter_data_addresses_city_temp_ogc_fid_seq OWNER TO pat;

--
-- Name: aa_filter_data_addresses_city_temp_ogc_fid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pat
--

ALTER SEQUENCE public.aa_filter_data_addresses_city_temp_ogc_fid_seq OWNED BY public.aa_filter_data_addresses_city_temp.ogc_fid;


--
-- Name: aa_filter_data_addresses_city_temp ogc_fid; Type: DEFAULT; Schema: public; Owner: pat
--

ALTER TABLE ONLY public.aa_filter_data_addresses_city_temp ALTER COLUMN ogc_fid SET DEFAULT nextval('public.aa_filter_data_addresses_city_temp_ogc_fid_seq'::regclass);


--
-- Data for Name: aa_filter_data_addresses_city_temp; Type: TABLE DATA; Schema: public; Owner: pat
--

COPY public.aa_filter_data_addresses_city_temp (ogc_fid, id, unit, number, street, city, district, region, postcode, hash, wkb_geometry) FROM stdin;
1			1	Di Mario Dr				02904	908f551defc1295a	0101000020E610000037F0B446CEDA51C04D593CABBBED4440
2	0100101061763020-5		SN	CALLE EMILIO GARCÍA	ARELLANO	Aguascalientes	Aguascalientes		59a2672f7f81bc31	0101000020E6100000F1DB6B9CA89159C01C19F55A1ACD3540
3			--	Linwood Ave				02907	e1262d57e0077c2e	0101000020E6100000430F6BE0FDDB51C0224212AC60E74440
4	212888		1127\b	TANGELOS ST	BAKERSFIELD		CA	93306	11e4eb3ece546426	0101000020E6100000C3802557B1B95DC01E4BC4002EAF4140
5			2857	RAYMOND J REED  SE	 				45e2b88e896ed2e6	0101000020E6100000C65EDED2A0EE5AC00348C89B57204040
6			119	MAIN ST					5f1f1bb28879f693	\N
\.


--
-- Name: aa_filter_data_addresses_city_temp_ogc_fid_seq; Type: SEQUENCE SET; Schema: public; Owner: pat
--

SELECT pg_catalog.setval('public.aa_filter_data_addresses_city_temp_ogc_fid_seq', 6, true);


--
-- Name: aa_filter_data_addresses_city_temp aa_filter_data_addresses_city_temp_pkey; Type: CONSTRAINT; Schema: public; Owner: pat
--

ALTER TABLE ONLY public.aa_filter_data_addresses_city_temp
    ADD CONSTRAINT aa_filter_data_addresses_city_temp_pkey PRIMARY KEY (ogc_fid);


--
-- Name: aa_filter_data_addresses_city_temp_wkb_geometry_geom_idx; Type: INDEX; Schema: public; Owner: pat
--

CREATE INDEX aa_filter_data_addresses_city_temp_wkb_geometry_geom_idx ON public.aa_filter_data_addresses_city_temp USING gist (wkb_geometry);


--
-- PostgreSQL database dump complete
--

