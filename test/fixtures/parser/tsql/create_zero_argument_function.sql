CREATE OR ALTER FUNCTION a() RETURNS integer
AS
'
    SELECT 1;
'
LANGUAGE SQL;

CREATE FUNCTION a() RETURNS integer
AS
'
    SELECT 1;
'
LANGUAGE SQL;
