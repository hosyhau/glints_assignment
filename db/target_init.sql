CREATE TABLE sale (
    id SERIAL PRIMARY KEY,
    creation_date DATE NOT NULL,
    sale_value INT NOT NULL,
    created_at TIMESTAMP with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE job (
    id SERIAL PRIMARY KEY,
    job_type VARCHAR(255) NOT NULL,
    job_name VARCHAR(255) NOT NULL,
    job_description TEXT NOT NULL,
    batch_size INT NOT NULL,
    last_id VARCHAR(255) NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL,
    error_log TEXT
);
