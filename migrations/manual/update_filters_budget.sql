--- Script manuel permettant de modifier les filtres des préférences utilisateurs pour l'application budget

-- remplace <HOST> par le host de l'application budget

ALTER TABLE settings.preference_users  ADD filters_copy JSON;
UPDATE settings.preference_users SET filters_copy = filters;



UPDATE settings.preference_users
SET filters =  json_build_object('year', filters -> 'year', 'theme',

(SELECT json_agg(elem->>'Label') FROM json_array_elements(filters->'theme') AS elem ),

'bops', (SELECT json_build_object(
    'tmp',
    (
        SELECT json_agg(jsonb_build_object('code', elem->>'Code', 'label', elem->>'Label'))
        FROM json_array_elements(filters->'bops') AS elem
    )
))->'tmp',
'location', filters -> 'location',
'beneficiaire', (SELECT json_build_object('siret', filters->'beneficiaire'->'Code', 'denomination', filters->'beneficiaire'->'Denomination' ))

 ) WHERE application_host = '<HOST>';




UPDATE settings.preference_users
SET filters = filters::jsonb - 'beneficiaire'
WHERE  (filters -> 'beneficiaire')::jsonb = '{}'::jsonb AND  application_host = '<HOST>';


ALTER TABLE  settings.preference_users DROP COLUMN  filters_copy;