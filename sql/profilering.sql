-- Fordeling per organisasjonsform
SELECT organisasjonsform_kode, count(*) AS antall
FROM enheter GROUP BY 1 ORDER BY 2 DESC LIMIT 15;

-- Registreringer per år: ser vi brudd i tidsserien som kan forklare kvalitetsforskjeller?
SELECT year(try_cast(registreringsdatoenhetsregisteret AS DATE)) AS aar, count(*) AS antall
FROM enheter GROUP BY 1 ORDER BY 1;

-- Hyppigste næringskoder
SELECT naeringskode1_kode, count(*) AS antall
FROM enheter GROUP BY 1 ORDER BY 2 DESC LIMIT 15;

-- Mangler næringskode fordelt på organisasjonsform: er problemet konsentrert?
SELECT organisasjonsform_kode,
       count(*) AS antall,
       round(100 * avg((naeringskode1_kode IS NULL)::INT), 1) AS prosent_uten_naeringskode
FROM enheter GROUP BY 1 HAVING count(*) > 1000 ORDER BY 3 DESC;

-- Historikk: hvordan har avvikene utviklet seg mellom kjøringer?
SELECT kontroll_id, kjoretidspunkt, avvik
FROM kvalitetsresultat ORDER BY kontroll_id, kjoretidspunkt;
