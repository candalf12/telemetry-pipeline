CREATE TABLE IF NOT EXISTS system_metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ram_usage REAL NOT NULL
);

CREATE OR REPLACE VIEW hourly_ram_summary AS
SELECT 
    DATE_TRUNC('minute', timestamp) AS olcum_dakikasi,
    COUNT(*) AS veri_sayisi,
    ROUND(AVG(ram_usage)::numeric, 2) AS ortalama_ram
FROM system_metrics
GROUP BY olcum_dakikasi
ORDER BY olcum_dakikasi DESC;