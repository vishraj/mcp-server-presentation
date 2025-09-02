CREATE TABLE etl_load_status (
    job_id SERIAL PRIMARY KEY,
    job_name VARCHAR(200) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('RUNNING', 'SUCCESS', 'FAILED')),
    rows_loaded BIGINT,
    dataset_size_mb NUMERIC(12,2),
    start_time TIMESTAMP NOT NULL DEFAULT NOW(),
    end_time TIMESTAMP,
    error_message TEXT
);

-- Example index for quick filtering on recent loads
CREATE INDEX idx_etl_status_jobname_starttime ON etl_load_status(job_name, start_time DESC);
