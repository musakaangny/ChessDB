-- Trigger to prevent overlapping matches for arbiters
DELIMITER //
CREATE TRIGGER prevent_arbiter_overlap
BEFORE INSERT ON Matches
FOR EACH ROW
BEGIN
    DECLARE conflict_count INT;
    
    -- Calculate the time slot before and after the new match
    DECLARE prev_slot INT;
    DECLARE next_slot INT;
    
    SET prev_slot = IF(NEW.time_slot = '1', NULL, IF(NEW.time_slot = '2', 1, 2));
    SET next_slot = IF(NEW.time_slot = '3', NULL, IF(NEW.time_slot = '2', 3, 2));
    
    -- Check if arbiter has a match in adjacent time slots
    SELECT COUNT(*) INTO conflict_count
    FROM Matches
    WHERE arbiter_username = NEW.arbiter_username
    AND date = NEW.date
    AND (time_slot = NEW.time_slot 
         OR (prev_slot IS NOT NULL AND time_slot = prev_slot)
         OR (next_slot IS NOT NULL AND time_slot = next_slot));
    
    IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Arbiter is already assigned to a match in overlapping time slots';
    END IF;
END //
DELIMITER ;

-- Trigger to prevent overlapping matches for players
DELIMITER //
CREATE TRIGGER prevent_player_overlap
BEFORE INSERT ON Matches
FOR EACH ROW
BEGIN
    DECLARE conflict_count INT;
    
    -- Calculate the time slot before and after the new match
    DECLARE prev_slot INT;
    DECLARE next_slot INT;
    
    SET prev_slot = IF(NEW.time_slot = '1', NULL, IF(NEW.time_slot = '2', 1, 2));
    SET next_slot = IF(NEW.time_slot = '3', NULL, IF(NEW.time_slot = '2', 3, 2));
    
    -- Check if white player has a match in adjacent time slots
    SELECT COUNT(*) INTO conflict_count
    FROM Matches
    WHERE (white_player = NEW.white_player OR black_player = NEW.white_player)
    AND date = NEW.date
    AND (time_slot = NEW.time_slot 
         OR (prev_slot IS NOT NULL AND time_slot = prev_slot)
         OR (next_slot IS NOT NULL AND time_slot = next_slot));
    
    IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'White player is already assigned to a match in overlapping time slots';
    END IF;
    
    -- Check if black player has a match in adjacent time slots
    SELECT COUNT(*) INTO conflict_count
    FROM Matches
    WHERE (white_player = NEW.black_player OR black_player = NEW.black_player)
    AND date = NEW.date
    AND (time_slot = NEW.time_slot 
         OR (prev_slot IS NOT NULL AND time_slot = prev_slot)
         OR (next_slot IS NOT NULL AND time_slot = next_slot));
    
    IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Black player is already assigned to a match in overlapping time slots';
    END IF;
END //
DELIMITER ;

-- Trigger to ensure coach works with only one team at a time (no overlapping dates)
DELIMITER //
CREATE TRIGGER prevent_coach_overlap
BEFORE INSERT ON CoachTeams
FOR EACH ROW
BEGIN
    DECLARE conflict_count INT;
    
    -- Check if coach has an overlapping contract with another team
    SELECT COUNT(*) INTO conflict_count
    FROM CoachTeams
    WHERE username = NEW.username
    AND team_id <> NEW.team_id
    AND (
        -- New contract starts during existing contract
        (NEW.contract_start BETWEEN contract_start AND contract_finish) OR
        -- New contract ends during existing contract
        (NEW.contract_finish BETWEEN contract_start AND contract_finish) OR
        -- New contract encompasses existing contract
        (NEW.contract_start <= contract_start AND NEW.contract_finish >= contract_finish)
    );
    
    IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Coach already has a contract with another team during this period';
    END IF;
END //
DELIMITER ;

-- Also add triggers for UPDATE operations

-- Trigger to prevent overlapping matches for arbiters on UPDATE
DELIMITER //
CREATE TRIGGER prevent_arbiter_overlap_update
BEFORE UPDATE ON Matches
FOR EACH ROW
BEGIN
    DECLARE conflict_count INT;
    
    -- Calculate the time slot before and after the updated match
    DECLARE prev_slot INT;
    DECLARE next_slot INT;
    
    SET prev_slot = IF(NEW.time_slot = '1', NULL, IF(NEW.time_slot = '2', 1, 2));
    SET next_slot = IF(NEW.time_slot = '3', NULL, IF(NEW.time_slot = '2', 3, 2));
    
    -- Check if arbiter has a match in adjacent time slots (excluding the match being updated)
    SELECT COUNT(*) INTO conflict_count
    FROM Matches
    WHERE arbiter_username = NEW.arbiter_username
    AND date = NEW.date
    AND match_id <> NEW.match_id
    AND (time_slot = NEW.time_slot 
         OR (prev_slot IS NOT NULL AND time_slot = prev_slot)
         OR (next_slot IS NOT NULL AND time_slot = next_slot));
    
    IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Arbiter is already assigned to a match in overlapping time slots';
    END IF;
END //
DELIMITER ;

-- Trigger to prevent overlapping matches for players on UPDATE
DELIMITER //
CREATE TRIGGER prevent_player_overlap_update
BEFORE UPDATE ON Matches
FOR EACH ROW
BEGIN
    DECLARE conflict_count INT;
    
    -- Calculate the time slot before and after the updated match
    DECLARE prev_slot INT;
    DECLARE next_slot INT;
    
    SET prev_slot = IF(NEW.time_slot = '1', NULL, IF(NEW.time_slot = '2', 1, 2));
    SET next_slot = IF(NEW.time_slot = '3', NULL, IF(NEW.time_slot = '2', 3, 2));
    
    -- Check if white player has a match in adjacent time slots (excluding the match being updated)
    SELECT COUNT(*) INTO conflict_count
    FROM Matches
    WHERE (white_player = NEW.white_player OR black_player = NEW.white_player)
    AND date = NEW.date
    AND match_id <> NEW.match_id
    AND (time_slot = NEW.time_slot 
         OR (prev_slot IS NOT NULL AND time_slot = prev_slot)
         OR (next_slot IS NOT NULL AND time_slot = next_slot));
    
    IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'White player is already assigned to a match in overlapping time slots';
    END IF;
    
    -- Check if black player has a match in adjacent time slots (excluding the match being updated)
    SELECT COUNT(*) INTO conflict_count
    FROM Matches
    WHERE (white_player = NEW.black_player OR black_player = NEW.black_player)
    AND date = NEW.date
    AND match_id <> NEW.match_id
    AND (time_slot = NEW.time_slot 
         OR (prev_slot IS NOT NULL AND time_slot = prev_slot)
         OR (next_slot IS NOT NULL AND time_slot = next_slot));
    
    IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Black player is already assigned to a match in overlapping time slots';
    END IF;
END //
DELIMITER ;

-- Trigger to ensure coach works with only one team at a time on UPDATE (no overlapping dates)
DELIMITER //
CREATE TRIGGER prevent_coach_overlap_update
BEFORE UPDATE ON CoachTeams
FOR EACH ROW
BEGIN
    DECLARE conflict_count INT;
    
    -- Check if coach has an overlapping contract with another team (excluding the contract being updated)
    SELECT COUNT(*) INTO conflict_count
    FROM CoachTeams
    WHERE username = NEW.username
    AND team_id <> NEW.team_id
    AND NOT (username = OLD.username AND team_id = OLD.team_id AND contract_start = OLD.contract_start)
    AND (
        -- Updated contract starts during existing contract
        (NEW.contract_start BETWEEN contract_start AND contract_finish) OR
        -- Updated contract ends during existing contract
        (NEW.contract_finish BETWEEN contract_start AND contract_finish) OR
        -- Updated contract encompasses existing contract
        (NEW.contract_start <= contract_start AND NEW.contract_finish >= contract_finish)
    );
    
    IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Coach already has a contract with another team during this period';
    END IF;
END //
DELIMITER ;

-- Triggers to prevent duplicate usernames across user tables

-- Trigger to prevent duplicate usernames in DBManagers
DELIMITER //
CREATE TRIGGER prevent_duplicate_username_dbmanager
BEFORE INSERT ON DBManagers
FOR EACH ROW
BEGIN
    DECLARE conflict_count INT DEFAULT 0;
    
    -- Check if username exists in Coaches
    SELECT COUNT(*) INTO conflict_count
    FROM Coaches
    WHERE username = NEW.username;
    
    IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Username already exists in Coaches table';
    END IF;
    
    -- Check if username exists in Arbiters
    SELECT COUNT(*) INTO conflict_count
    FROM Arbiters
    WHERE username = NEW.username;
    
    IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Username already exists in Arbiters table';
    END IF;
    
    -- Check if username exists in Players
    SELECT COUNT(*) INTO conflict_count
    FROM Players
    WHERE username = NEW.username;
    
    IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Username already exists in Players table';
    END IF;
END //
DELIMITER ;

-- Trigger to prevent duplicate usernames in Coaches
DELIMITER //
CREATE TRIGGER prevent_duplicate_username_coach
BEFORE INSERT ON Coaches
FOR EACH ROW
BEGIN
    DECLARE conflict_count INT DEFAULT 0;
    
    -- Check if username exists in DBManagers
    SELECT COUNT(*) INTO conflict_count
    FROM DBManagers
    WHERE username = NEW.username;
    
    IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Username already exists in DBManagers table';
    END IF;
    
    -- Check if username exists in Arbiters
    SELECT COUNT(*) INTO conflict_count
    FROM Arbiters
    WHERE username = NEW.username;
    
    IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Username already exists in Arbiters table';
    END IF;
    
    -- Check if username exists in Players
    SELECT COUNT(*) INTO conflict_count
    FROM Players
    WHERE username = NEW.username;
    
    IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Username already exists in Players table';
    END IF;
END //
DELIMITER ;

-- Trigger to prevent duplicate usernames in Arbiters
DELIMITER //
CREATE TRIGGER prevent_duplicate_username_arbiter
BEFORE INSERT ON Arbiters
FOR EACH ROW
BEGIN
    DECLARE conflict_count INT DEFAULT 0;
    
    -- Check if username exists in DBManagers
    SELECT COUNT(*) INTO conflict_count
    FROM DBManagers
    WHERE username = NEW.username;
    
    IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Username already exists in DBManagers table';
    END IF;
    
    -- Check if username exists in Coaches
    SELECT COUNT(*) INTO conflict_count
    FROM Coaches
    WHERE username = NEW.username;
    
    IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Username already exists in Coaches table';
    END IF;
    
    -- Check if username exists in Players
    SELECT COUNT(*) INTO conflict_count
    FROM Players
    WHERE username = NEW.username;
    
    IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Username already exists in Players table';
    END IF;
END //
DELIMITER ;

-- Trigger to prevent duplicate usernames in Players
DELIMITER //
CREATE TRIGGER prevent_duplicate_username_player
BEFORE INSERT ON Players
FOR EACH ROW
BEGIN
    DECLARE conflict_count INT DEFAULT 0;
    
    -- Check if username exists in DBManagers
    SELECT COUNT(*) INTO conflict_count
    FROM DBManagers
    WHERE username = NEW.username;
    
    IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Username already exists in DBManagers table';
    END IF;
    
    -- Check if username exists in Coaches
    SELECT COUNT(*) INTO conflict_count
    FROM Coaches
    WHERE username = NEW.username;
    
    IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Username already exists in Coaches table';
    END IF;
    
    -- Check if username exists in Arbiters
    SELECT COUNT(*) INTO conflict_count
    FROM Arbiters
    WHERE username = NEW.username;
    
    IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Username already exists in Arbiters table';
    END IF;
END //
DELIMITER ;

-- Triggers for UPDATE operations to prevent duplicate usernames

-- Trigger to prevent duplicate usernames in DBManagers on UPDATE
DELIMITER //
CREATE TRIGGER prevent_duplicate_username_dbmanager_update
BEFORE UPDATE ON DBManagers
FOR EACH ROW
BEGIN
    DECLARE conflict_count INT DEFAULT 0;
    
    -- Only check if username is being changed
    IF NEW.username <> OLD.username THEN
        -- Check if username exists in Coaches
        SELECT COUNT(*) INTO conflict_count
        FROM Coaches
        WHERE username = NEW.username;
        
        IF conflict_count > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Username already exists in Coaches table';
        END IF;
        
        -- Check if username exists in Arbiters
        SELECT COUNT(*) INTO conflict_count
        FROM Arbiters
        WHERE username = NEW.username;
        
        IF conflict_count > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Username already exists in Arbiters table';
        END IF;
        
        -- Check if username exists in Players
        SELECT COUNT(*) INTO conflict_count
        FROM Players
        WHERE username = NEW.username;
        
        IF conflict_count > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Username already exists in Players table';
        END IF;
    END IF;
END //
DELIMITER ;

-- Trigger to prevent duplicate usernames in Coaches on UPDATE
DELIMITER //
CREATE TRIGGER prevent_duplicate_username_coach_update
BEFORE UPDATE ON Coaches
FOR EACH ROW
BEGIN
    DECLARE conflict_count INT DEFAULT 0;
    
    -- Only check if username is being changed
    IF NEW.username <> OLD.username THEN
        -- Check if username exists in DBManagers
        SELECT COUNT(*) INTO conflict_count
        FROM DBManagers
        WHERE username = NEW.username;
        
        IF conflict_count > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Username already exists in DBManagers table';
        END IF;
        
        -- Check if username exists in Arbiters
        SELECT COUNT(*) INTO conflict_count
        FROM Arbiters
        WHERE username = NEW.username;
        
        IF conflict_count > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Username already exists in Arbiters table';
        END IF;
        
        -- Check if username exists in Players
        SELECT COUNT(*) INTO conflict_count
        FROM Players
        WHERE username = NEW.username;
        
        IF conflict_count > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Username already exists in Players table';
        END IF;
    END IF;
END //
DELIMITER ;

-- Trigger to prevent duplicate usernames in Arbiters on UPDATE
DELIMITER //
CREATE TRIGGER prevent_duplicate_username_arbiter_update
BEFORE UPDATE ON Arbiters
FOR EACH ROW
BEGIN
    DECLARE conflict_count INT DEFAULT 0;
    
    -- Only check if username is being changed
    IF NEW.username <> OLD.username THEN
        -- Check if username exists in DBManagers
        SELECT COUNT(*) INTO conflict_count
        FROM DBManagers
        WHERE username = NEW.username;
        
        IF conflict_count > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Username already exists in DBManagers table';
        END IF;
        
        -- Check if username exists in Coaches
        SELECT COUNT(*) INTO conflict_count
        FROM Coaches
        WHERE username = NEW.username;
        
        IF conflict_count > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Username already exists in Coaches table';
        END IF;
        
        -- Check if username exists in Players
        SELECT COUNT(*) INTO conflict_count
        FROM Players
        WHERE username = NEW.username;
        
        IF conflict_count > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Username already exists in Players table';
        END IF;
    END IF;
END //
DELIMITER ;

-- Trigger to prevent duplicate usernames in Players on UPDATE
DELIMITER //
CREATE TRIGGER prevent_duplicate_username_player_update
BEFORE UPDATE ON Players
FOR EACH ROW
BEGIN
    DECLARE conflict_count INT DEFAULT 0;
    
    -- Only check if username is being changed
    IF NEW.username <> OLD.username THEN
        -- Check if username exists in DBManagers
        SELECT COUNT(*) INTO conflict_count
        FROM DBManagers
        WHERE username = NEW.username;
        
        IF conflict_count > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Username already exists in DBManagers table';
        END IF;
        
        -- Check if username exists in Coaches
        SELECT COUNT(*) INTO conflict_count
        FROM Coaches
        WHERE username = NEW.username;
        
        IF conflict_count > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Username already exists in Coaches table';
        END IF;
        
        -- Check if username exists in Arbiters
        SELECT COUNT(*) INTO conflict_count
        FROM Arbiters
        WHERE username = NEW.username;
        
        IF conflict_count > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Username already exists in Arbiters table';
        END IF;
    END IF;
END //
DELIMITER ;

-- Trigger to prevent overlapping matches for tables
DELIMITER //
CREATE TRIGGER prevent_table_overlap
BEFORE INSERT ON Matches
FOR EACH ROW
BEGIN
    DECLARE conflict_count INT;
    
    -- Calculate the time slot before and after the new match
    DECLARE prev_slot INT;
    DECLARE next_slot INT;
    
    SET prev_slot = IF(NEW.time_slot = '1', NULL, IF(NEW.time_slot = '2', 1, 2));
    SET next_slot = IF(NEW.time_slot = '3', NULL, IF(NEW.time_slot = '2', 3, 2));
    
    -- Check if table has a match in adjacent time slots
    SELECT COUNT(*) INTO conflict_count
    FROM Matches
    WHERE table_id = NEW.table_id
    AND date = NEW.date
    AND (time_slot = NEW.time_slot 
         OR (prev_slot IS NOT NULL AND time_slot = prev_slot)
         OR (next_slot IS NOT NULL AND time_slot = next_slot));
    
    IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Table is already assigned to a match in overlapping time slots';
    END IF;
END //
DELIMITER ;

-- Trigger to prevent overlapping matches for tables on UPDATE
DELIMITER //
CREATE TRIGGER prevent_table_overlap_update
BEFORE UPDATE ON Matches
FOR EACH ROW
BEGIN
    DECLARE conflict_count INT;
    
    -- Calculate the time slot before and after the updated match
    DECLARE prev_slot INT;
    DECLARE next_slot INT;
    
    SET prev_slot = IF(NEW.time_slot = '1', NULL, IF(NEW.time_slot = '2', 1, 2));
    SET next_slot = IF(NEW.time_slot = '3', NULL, IF(NEW.time_slot = '2', 3, 2));
    
    -- Check if table has a match in adjacent time slots (excluding the match being updated)
    SELECT COUNT(*) INTO conflict_count
    FROM Matches
    WHERE table_id = NEW.table_id
    AND date = NEW.date
    AND match_id <> NEW.match_id
    AND (time_slot = NEW.time_slot 
         OR (prev_slot IS NOT NULL AND time_slot = prev_slot)
         OR (next_slot IS NOT NULL AND time_slot = next_slot));
    
    IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Table is already assigned to a match in overlapping time slots';
    END IF;
END //
DELIMITER ;