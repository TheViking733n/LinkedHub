-- TRIGGERS

-- comments delete trigger
CREATE OR REPLACE FUNCTION comments_procedure()
    RETURNS TRIGGER AS $$
BEGIN

    DELETE 
    FROM post_like  
    WHERE post_like.item_id = OLD.comment_id AND post_like.item_type = 'comment';

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER commentsDeleteTrigger
AFTER DELETE ON post_comment
FOR EACH ROW 
EXECUTE PROCEDURE comments_procedure();


-- post delete trigger
CREATE OR REPLACE FUNCTION posts_procedure()
    RETURNS TRIGGER AS $$
BEGIN

    DELETE 
    FROM post_like 
    WHERE post_like.item_id = OLD.post_id AND post_like.item_type = 'post'; 

    DELETE 
    FROM post_comment  
    WHERE post_comment.post_id = OLD.post_id;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER postsDeleteTrigger
AFTER DELETE ON post_post
FOR EACH ROW 
EXECUTE PROCEDURE posts_procedure();


-- uppercase name trigger 
CREATE OR REPLACE FUNCTION uppercase_procedure()
    RETURNS TRIGGER AS $$
BEGIN

    UPDATE home_userprofile 
    SET name = CONCAT(UPPER(SUBSTRING(name, 1, 1)), SUBSTRING(name FROM 2));

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER uppercaseTrigger
AFTER INSERT ON home_userprofile
FOR EACH ROW 
EXECUTE PROCEDURE uppercase_procedure();












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












-- PROCEDURES

-- delete pending request procedure 
CREATE OR REPLACE PROCEDURE deleterequests(inputreceiver VARCHAR, inputsender VARCHAR)
LANGUAGE plpgsql
as $$
BEGIN
    DELETE FROM home_pendingrequest WHERE sender = inputsender AND receiver = inputreceiver;
END;$$ ;


-- update organization procedure 
CREATE OR REPLACE PROCEDURE organizationUpdateProc(IN username VARCHAR, IN oldOrg VARCHAR, IN newOrg VARCHAR)
LANGUAGE plpgsql
AS $$
BEGIN
    IF oldOrg IS NULL THEN 
        INSERT INTO home_connection VALUES(username, newOrg);
        INSERT INTO home_connection VALUES(newOrg, username);
    ELSEIF EXISTS (SELECT * FROM home_connection WHERE user1 = username AND user2 = oldOrg) THEN
        DELETE FROM home_connection WHERE user1 = username AND user2 = oldOrg;
        DELETE FROM home_connection WHERE user1 = oldOrg AND user2 = username;
        INSERT INTO home_connection VALUES(username, newOrg);
        INSERT INTO home_connection VALUES(newOrg, username);
    END IF;
END;
$$; 


