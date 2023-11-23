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


