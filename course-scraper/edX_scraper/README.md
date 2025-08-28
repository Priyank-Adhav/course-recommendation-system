## Usage
```bash
python get.py
```

## Schema
```

CREATE TABLE IF NOT EXISTS courses (
    id TEXT PRIMARY KEY,
    title TEXT,
    description TEXT,
    subject TEXT,
    level TEXT,
    language TEXT,
    weeks_to_complete INTEGER,
    availability TEXT,
    marketing_url TEXT,
    card_image_url TEXT
);

CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id TEXT,
    skill TEXT,
    category TEXT,
    subcategory TEXT,
    UNIQUE(course_id, skill, category, subcategory) ON CONFLICT IGNORE,
    FOREIGN KEY(course_id) REFERENCES courses(id)
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id TEXT,
    tag TEXT,
    UNIQUE(course_id, tag) ON CONFLICT IGNORE,
    FOREIGN KEY(course_id) REFERENCES courses(id)
);

CREATE TABLE IF NOT EXISTS staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id TEXT,
    staff_key TEXT,
    UNIQUE(course_id, staff_key) ON CONFLICT IGNORE,
    FOREIGN KEY(course_id) REFERENCES courses(id)
);

CREATE TABLE IF NOT EXISTS owners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id TEXT,
    name TEXT,
    UNIQUE(course_id, name) ON CONFLICT IGNORE,
    FOREIGN KEY(course_id) REFERENCES courses(id)
);
```

## Note
+ Description is embedded within HTML tags (<p>, <span>).
+ Courses with languages other than English exist. May need filtering.
+ 4825 total courses
