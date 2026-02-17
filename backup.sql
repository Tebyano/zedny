--
-- PostgreSQL database dump
--

\restrict cP7EgLW2pS4NDu9LShzlBJ5DGEChKOH4C6g9aZMiGvAxCR0g87GUpH4hYIwgXwq

-- Dumped from database version 15.15 (Debian 15.15-1.pgdg13+1)
-- Dumped by pg_dump version 15.15 (Debian 15.15-1.pgdg13+1)

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
-- Name: items; Type: TABLE; Schema: public; Owner: tebyan
--

CREATE TABLE public.items (
    item_id integer NOT NULL,
    item_name name NOT NULL
);


ALTER TABLE public.items OWNER TO tebyan;

--
-- Name: items_item_id_seq; Type: SEQUENCE; Schema: public; Owner: tebyan
--

ALTER TABLE public.items ALTER COLUMN item_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.items_item_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: user_item; Type: TABLE; Schema: public; Owner: tebyan
--

CREATE TABLE public.user_item (
    user_id integer NOT NULL,
    item_id integer NOT NULL,
    id integer NOT NULL
);


ALTER TABLE public.user_item OWNER TO tebyan;

--
-- Name: user_item_id_seq; Type: SEQUENCE; Schema: public; Owner: tebyan
--

ALTER TABLE public.user_item ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.user_item_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: tebyan
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username name NOT NULL,
    email text,
    hashed_password character varying(255) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE public.users OWNER TO tebyan;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: tebyan
--

ALTER TABLE public.users ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Data for Name: items; Type: TABLE DATA; Schema: public; Owner: tebyan
--

COPY public.items (item_id, item_name) FROM stdin;
1	laptop
2	laptop
3	bag
4	bag
\.


--
-- Data for Name: user_item; Type: TABLE DATA; Schema: public; Owner: tebyan
--

COPY public.user_item (user_id, item_id, id) FROM stdin;
1	1	3
3	1	4
2	2	5
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: tebyan
--

COPY public.users (id, username, email, hashed_password) FROM stdin;
1	tebyan	tebyan.samy2003@gmail.com	
2	tebyan	tebyan.samy2003@gmail.com	
3	tebyan	tebyan.samy2003@gmail.com	
4	tebyan	tebyan.samy2003@gmail.com	
5	tebyan	tebyan.samy2003@gmail.com	
6	tebyan	tebyan.samy2003@gmail.com	
8	tebyan	tebyan.samy2003@gmail.com	
9	khadega	khad@email	
10	string	user@example.com	$2b$12$knmVT.TglkTKNnNGSvNKTef9GYfb5Hy0MqywpR60IO6Aj/LK7Eqsu
11	shams	shams@example.com	$2b$12$nah1h8/AerDxSFOAM1ODq.D2rMCAlaSsx8mkaNaFqWbAXQLwZDMgC
12	string	user@example.com	$2b$12$3CGXIthNk3nlPVri9ukn6euoO6uNmEG375VFb.K6bpa2tVFc9xuom
13	bbbbbbb	user@example.com	$2b$12$Z39vcuAJj.4TiUuj34ZIdeRCbssZwMiOe3jEzw0vJ388oZR9eWfIK
\.


--
-- Name: items_item_id_seq; Type: SEQUENCE SET; Schema: public; Owner: tebyan
--

SELECT pg_catalog.setval('public.items_item_id_seq', 4, true);


--
-- Name: user_item_id_seq; Type: SEQUENCE SET; Schema: public; Owner: tebyan
--

SELECT pg_catalog.setval('public.user_item_id_seq', 5, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: tebyan
--

SELECT pg_catalog.setval('public.users_id_seq', 13, true);


--
-- Name: user_item id; Type: CONSTRAINT; Schema: public; Owner: tebyan
--

ALTER TABLE ONLY public.user_item
    ADD CONSTRAINT id PRIMARY KEY (id);


--
-- Name: items items_pkey; Type: CONSTRAINT; Schema: public; Owner: tebyan
--

ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_pkey PRIMARY KEY (item_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: tebyan
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: user_item item_id; Type: FK CONSTRAINT; Schema: public; Owner: tebyan
--

ALTER TABLE ONLY public.user_item
    ADD CONSTRAINT item_id FOREIGN KEY (item_id) REFERENCES public.items(item_id) NOT VALID;


--
-- Name: user_item user_id; Type: FK CONSTRAINT; Schema: public; Owner: tebyan
--

ALTER TABLE ONLY public.user_item
    ADD CONSTRAINT user_id FOREIGN KEY (user_id) REFERENCES public.users(id) NOT VALID;


--
-- PostgreSQL database dump complete
--

\unrestrict cP7EgLW2pS4NDu9LShzlBJ5DGEChKOH4C6g9aZMiGvAxCR0g87GUpH4hYIwgXwq

