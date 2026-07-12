-- Create an index on the english column for faster text search
CREATE INDEX IF NOT EXISTS idx_dictionary_entries_english ON dictionary_entries USING gin (to_tsvector('english', english));

-- Create a function to automatically update the search vector
CREATE OR REPLACE FUNCTION update_search_vector() RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector = to_tsvector('english', NEW.english);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create a trigger to automatically update the search vector
DROP TRIGGER IF EXISTS update_dictionary_entries_search_vector ON dictionary_entries;
CREATE TRIGGER update_dictionary_entries_search_vector
    BEFORE INSERT OR UPDATE ON dictionary_entries
    FOR EACH ROW
    EXECUTE FUNCTION update_search_vector();

-- Add a search_vector column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'dictionary_entries' 
        AND column_name = 'search_vector'
    ) THEN
        ALTER TABLE dictionary_entries ADD COLUMN search_vector tsvector;
    END IF;
END $$;

-- Update existing rows with search vectors
UPDATE dictionary_entries 
SET search_vector = to_tsvector('english', english) 
WHERE search_vector IS NULL; 