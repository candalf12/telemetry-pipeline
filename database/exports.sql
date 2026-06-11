COPY (
    SELECT * FROM system_metrics
    WHERE ram_usage > 35.0
    ORDER BY timestamp DESC
) TO '/exports/ram_report.csv' WITH CSV HEADER;
DELETE FROM system_metrics WHERE ram_usage < 32.0;