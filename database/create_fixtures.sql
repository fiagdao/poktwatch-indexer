create role web_anon nologin;
grant select on public.state to web_anon;
grant select on public.transactions to web_anon;
grant select on public.pulse to web_anon;
grant select on public.blocks to web_anon;
