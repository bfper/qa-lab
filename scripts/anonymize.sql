-- Run against the LAB database only. Never against production.
-- Restore the dump first, then psql -f this file.
--
-- Column names are a best guess from app/models.py — verify and adjust
-- before the first run. It is meant to be edited, not trusted blindly.
BEGIN;

-- Fail loudly if someone points this at the wrong database.
DO $$
BEGIN
  IF current_database() NOT IN ('mentoria', 'auth') THEN
    RAISE EXCEPTION 'Refusing to run: database is %', current_database();
  END IF;
  IF inet_server_addr() IS NOT NULL
     AND host(inet_server_addr()) NOT IN ('127.0.0.1', '::1') THEN
    RAISE EXCEPTION 'Refusing to run against a remote server';
  END IF;
END $$;

UPDATE mentorando SET
  nome     = 'Mentorando ' || id,
  email    = 'mentorando' || id || '@qalab.local',
  telefone = '+5531900000' || lpad(id::text, 3, '0');

-- Two known accounts so tests have predictable credentials.
UPDATE mentorando SET email = 'mentorando@qalab.local'
 WHERE id = (SELECT min(id) FROM mentorando);

-- Free-text columns can leak names even after the email is scrubbed.
-- Decide per column: keep for realistic testing, or blank it out.
-- UPDATE entrada_diario SET texto = 'redacted for lab use';
-- UPDATE sessao        SET observacoes = 'redacted for lab use';

COMMIT;
