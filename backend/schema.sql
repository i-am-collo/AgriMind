-- AgriMind Database Schema (PostgreSQL / Supabase Compatible)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Batches Table
CREATE TABLE IF NOT EXISTS batches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    batch_type VARCHAR(50) NOT NULL CHECK (batch_type IN ('Poultry', 'Crops', 'Livestock')),
    initial_quantity INT NOT NULL,
    current_quantity INT NOT NULL,
    status VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active', 'Harvested', 'Quarantined')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Daily Logs Table
CREATE TABLE IF NOT EXISTS daily_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    batch_id UUID REFERENCES batches(id) ON DELETE CASCADE,
    log_date DATE NOT NULL DEFAULT CURRENT_DATE,
    mortality_count INT DEFAULT 0,
    feed_consumed_kg NUMERIC(8, 2) DEFAULT 0.0,
    water_consumed_l NUMERIC(8, 2) DEFAULT 0.0,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Diagnostics Table
CREATE TABLE IF NOT EXISTS diagnostics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    batch_id UUID REFERENCES batches(id) ON DELETE CASCADE,
    image_url TEXT,
    detected_issue VARCHAR(255) NOT NULL,
    severity VARCHAR(20) CHECK (severity IN ('Low', 'Medium', 'High', 'Critical')),
    confidence_score NUMERIC(5, 2),
    treatment_plan JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Initial Seed Data
INSERT INTO batches (id, name, batch_type, initial_quantity, current_quantity, status) VALUES
('b1111111-1111-1111-1111-111111111111', 'Cobb 500 Broiler Flock A', 'Poultry', 500, 488, 'Active'),
('b2222222-2222-2222-2222-222222222222', 'Maize Plot #3 (North Field)', 'Crops', 1200, 1180, 'Active'),
('b3333333-3333-3333-3333-333333333333', 'Dairy Holstein Herd B', 'Livestock', 45, 45, 'Active');

INSERT INTO daily_logs (batch_id, log_date, mortality_count, feed_consumed_kg, water_consumed_l, notes) VALUES
('b1111111-1111-1111-1111-111111111111', CURRENT_DATE - INTERVAL '2 days', 2, 85.50, 190.00, 'Normal behavior, appetite consistent.'),
('b1111111-1111-1111-1111-111111111111', CURRENT_DATE - INTERVAL '1 day', 4, 82.00, 185.00, 'Slightly reduced feed intake in northern coop section.'),
('b1111111-1111-1111-1111-111111111111', CURRENT_DATE, 6, 76.00, 175.00, 'Observed lethargy in 8 birds. Submitted image for AI inspection.'),

('b2222222-2222-2222-2222-222222222222', CURRENT_DATE - INTERVAL '1 day', 10, 0.00, 450.00, 'Irrigation cycle complete. Spotted yellowing on lower leaves.'),
('b2222222-2222-2222-2222-222222222222', CURRENT_DATE, 10, 0.00, 450.00, 'Nitrogen foliar spray applied.');

INSERT INTO diagnostics (batch_id, image_url, detected_issue, severity, confidence_score, treatment_plan) VALUES
('b1111111-1111-1111-1111-111111111111', '/uploads/poultry_sample.jpg', 'Coccidiosis (Eimeria infection)', 'High', 94.50, '{
    "symptom_analysis": ["Ruffled feathers", "Lethargy", "Pale wattles", "Diarrhea"],
    "immediate_actions": ["Isolate affected birds immediately to containment pen 2.", "Sanitize all drinking troughs with chlorine dioxide (2 ppm).", "Increase coop ventilation by 15%."],
    "medication_or_inputs": ["Administer Amprolium 9.6% solution via drinking water for 5 consecutive days (10 ml per gallon).", "Provide vitamin K3 supplement to reduce intestinal hemorrhaging."],
    "preventative_measures": ["Replace damp litter with dry pine shavings.", "Keep litter moisture below 25%."],
    "isolation_required": true,
    "resource_adjustments": {
        "feed_recommendation": "Switch to pre-starter crumb with probiotic additives; reduce high-fat protein intake by 10%.",
        "water_recommendation": "Increase clean electrolyte water availability by 20% to prevent dehydration."
    }
}');
