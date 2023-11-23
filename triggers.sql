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

