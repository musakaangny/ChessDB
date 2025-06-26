ALTER TABLE Tables
ADD CONSTRAINT fk_tables_hall_id FOREIGN KEY (hall_id) REFERENCES Halls(hall_id);

ALTER TABLE Matches
ADD CONSTRAINT fk_matches_team1_id FOREIGN KEY (team1_id) REFERENCES Teams(team_id),
ADD CONSTRAINT fk_matches_team2_id FOREIGN KEY (team2_id) REFERENCES Teams(team_id),
ADD CONSTRAINT fk_matches_white_player FOREIGN KEY (white_player) REFERENCES Players(username),
ADD CONSTRAINT fk_matches_black_player FOREIGN KEY (black_player) REFERENCES Players(username),
ADD CONSTRAINT fk_matches_table_id FOREIGN KEY (table_id) REFERENCES Tables(table_id),
ADD CONSTRAINT fk_matches_hall_id FOREIGN KEY (hall_id) REFERENCES Halls(hall_id),
ADD CONSTRAINT fk_matches_arbiter_username FOREIGN KEY (arbiter_username) REFERENCES Arbiters(username),
ADD CONSTRAINT fk_matches_coach_username FOREIGN KEY (coach_username) REFERENCES Coaches(username),
ADD CONSTRAINT chk_matches_teams CHECK (team1_id != team2_id);

ALTER TABLE PlayerTeams
ADD CONSTRAINT fk_playerteams_username FOREIGN KEY (username) REFERENCES Players(username),
ADD CONSTRAINT fk_playerteams_team_id FOREIGN KEY (team_id) REFERENCES Teams(team_id);

ALTER TABLE CoachCertifications
ADD CONSTRAINT fk_coachcertifications_username FOREIGN KEY (username) REFERENCES Coaches(username);

ALTER TABLE ArbiterCertifications
ADD CONSTRAINT fk_arbitercertifications_username FOREIGN KEY (username) REFERENCES Arbiters(username);

ALTER TABLE CoachTeams
ADD CONSTRAINT fk_coachteams_username FOREIGN KEY (username) REFERENCES Coaches(username),
ADD CONSTRAINT fk_coachteams_team_id FOREIGN KEY (team_id) REFERENCES Teams(team_id);