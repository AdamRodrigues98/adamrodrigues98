CREATE USER "adam.rodrigues" WITH PASSWORD '11111111111111';
GRANT CONNECT ON DATABASE admissao TO "adam.rodrigues";
GRANT USAGE ON SCHEMA admissao TO "adam.rodrigues";
GRANT SELECT ON ALL TABLES IN SCHEMA admissao TO "adam.rodrigues";
ALTER DEFAULT PRIVILEGES IN SCHEMA admissao GRANT SELECT ON TABLES TO "adam.rodrigues";


