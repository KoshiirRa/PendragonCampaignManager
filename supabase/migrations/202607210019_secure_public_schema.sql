BEGIN;

-- Supabase exposes the public schema through PostgREST. The application is the
-- only supported data boundary, so direct Data API roles receive no table or
-- sequence privileges and every existing public table has RLS enabled with no
-- permissive policies. The direct PostgreSQL application owner continues to
-- use the schema through FastAPI.
DO $secure_public_schema$
DECLARE
    relation_name text;
    data_api_role text;
BEGIN
    FOR relation_name IN
        SELECT quote_ident(tablename)
        FROM pg_catalog.pg_tables
        WHERE schemaname = 'public'
        ORDER BY tablename
    LOOP
        EXECUTE format('ALTER TABLE public.%s ENABLE ROW LEVEL SECURITY', relation_name);
    END LOOP;

    FOREACH data_api_role IN ARRAY ARRAY['anon', 'authenticated']
    LOOP
        IF pg_catalog.to_regrole(data_api_role) IS NOT NULL THEN
            EXECUTE format(
                'REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM %I',
                data_api_role
            );
            EXECUTE format(
                'REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM %I',
                data_api_role
            );
            EXECUTE format(
                'ALTER DEFAULT PRIVILEGES IN SCHEMA public '
                'REVOKE ALL PRIVILEGES ON TABLES FROM %I',
                data_api_role
            );
            EXECUTE format(
                'ALTER DEFAULT PRIVILEGES IN SCHEMA public '
                'REVOKE ALL PRIVILEGES ON SEQUENCES FROM %I',
                data_api_role
            );
        END IF;
    END LOOP;
END
$secure_public_schema$;

COMMIT;
