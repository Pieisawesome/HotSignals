HTML
    Input
        Takes in drone imagery input (video or screenshots)
        Takes in name (location maybe)
        Make sure format is valid
        Make sure length and size if valid
    Galley Profile
        Pull from folder/database
        First screenshot is image
        Name of Tower
        Maintenance Rating (0/10)
    Profile
        Up to 5 Screenshots (perhaps screenshots in which found criteria)
        List of Details
            Type, Height, Maintenance Rating
        Problems/Maintenance in bullet points
    
Object Detection Models / Criteria
    Start with 0

    Criteria:
    One
        Detect types of antenna
            If two types, interference 1
            Statement: "Two types of Antenna. This may cause interference."
            Null: "Was unable to confidently detect."
    Two
        Detect rust or damage to tower
            None 0, Light 1, Med 2, Heavy Rust 3, Null 
            Statement: "(No/Light/Med/Heavy) rust on structure."
            Null: "Was unable to confidently detect."
    Three
        Detect town/scenery in background
            City 0, Town 0, Small Town 0, No towns/trees 3
            Statement: "
            Null: "Was unable to confidently detect."
    Four
        Detect unknown objects
            None 0, One 1, Two 2, Three 3

    End with range of 0 to 10
    Rating is sent back with data found

Photo And Details Storage
    


```
CREATE TABLE IF NOT EXISTS profile (
    PRIMARY KEY SERIAL INT id,
    VARCHAR(255) name
    .... other data about the profile
);

CREATE TABLE IF NOT EXISTS detection_criteria (
    PRIMARY KEY INT id,
    INT antenna,
    INT rust_level,
    INT background,
    INT unknown_objects,
    ....
    FOREIGN KEY (id) REFERENCES profile(id)
);

CREATE TABLE IF NOT EXISTS photos (
    INT id,
    INT profile_id,
    VARCHAR(255) filename,
    VARCHAR(255) original_name,
    
    ....
    UNIQUE filename,
    FOREIGN KEY (id) REFERENCES profile(id),
    PRIMARY KEY (id,profile_id)
);
