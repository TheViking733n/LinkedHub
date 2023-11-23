-- FUNCTIONS

-- fist mutual connections function 
CREATE OR REPLACE FUNCTION mutualConnections(u VARCHAR, v VARCHAR)
RETURNS TABLE (name VARCHAR) AS $$
    BEGIN
      RETURN QUERY SELECT user2 FROM home_connection WHERE user1 = u INTERSECT SELECT user1 FROM home_connection WHERE user2 = v;
    END;
    $$ LANGUAGE plpgsql;


-- get user profile function 
CREATE OR REPLACE FUNCTION getUserProfile(inputuser VARCHAR)
RETURNS TABLE (username VARCHAR, name VARCHAR, profile_pic VARCHAR, bio VARCHAR, organization VARCHAR) AS $$
BEGIN
RETURN QUERY SELECT * FROM home_userprofile
WHERE home_userprofile.username = inputuser;
END;
$$ LANGUAGE plpgsql;


-- second mutual connection function 
CREATE OR REPLACE FUNCTION secondMutualConnectionsFunc(u VARCHAR, v VARCHAR)
RETURNS TABLE(name VARCHAR) AS $$
BEGIN
  RETURN QUERY WITH firstLevel(names) AS (
      SELECT DISTINCT user2 
      FROM home_connection 
      WHERE home_connection.user1 = u ),
    secondLevel(names) AS (
      SELECT DISTINCT user2
      FROM home_connection, firstLevel
      WHERE home_connection.user1 IN (SELECT * FROM firstLevel) AND home_connection.user2 <> u AND home_connection.user2 NOT IN (SELECT * FROM firstLevel))
    SELECT DISTINCT user1 
    FROM home_connection, secondLevel
    WHERE home_connection.user1 IN (SELECT * FROM secondLevel) AND home_connection.user2 = v;          
END;
$$ LANGUAGE plpgsql;

