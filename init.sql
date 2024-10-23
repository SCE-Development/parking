-- Create the table
CREATE TABLE IF NOT EXISTS parking_data (
    id SERIAL PRIMARY KEY,
    garage_name VARCHAR(50) NOT NULL,
    garage_fullness VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL
);

-- Insert sample data
INSERT INTO parking_data (garage_name, garage_fullness, timestamp) VALUES
('North_Garage', '75% Full', '2023-05-01 08:00:00'),
('South_Garage', '50% Full', '2023-05-01 08:00:00'),
('West_Garage', '90% Full', '2023-05-01 08:00:00'),
('South_Campus_Garage', '30% Full', '2023-05-01 08:00:00'),
('North_Garage', '80% Full', '2023-05-01 09:00:00'),
('South_Garage', '60% Full', '2023-05-01 09:00:00'),
('West_Garage', '95% Full', '2023-05-01 09:00:00'),
('South_Campus_Garage', '40% Full', '2023-05-01 09:00:00');

-- Verify the data
SELECT * FROM parking_data;