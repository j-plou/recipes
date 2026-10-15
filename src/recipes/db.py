import sqlite3


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys = ON")

    statements = (
        """
        CREATE TABLE IF NOT EXISTS language (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS recipe_category (
            id INTEGER PRIMARY KEY
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS recipe_category_language (
            id INTEGER PRIMARY KEY,
            recipe_category_id INTEGER NOT NULL
                REFERENCES recipe_category(id) ON DELETE CASCADE,
            language_id INTEGER NOT NULL
                REFERENCES language(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            UNIQUE (recipe_category_id, language_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS recipe_author (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS recipe (
            id INTEGER PRIMARY KEY,
            cook_time INTEGER,
            prep_time INTEGER,
            ratings REAL,
            category_id INTEGER NOT NULL
                REFERENCES recipe_category(id) ON DELETE CASCADE,
            author_id INTEGER NOT NULL
                REFERENCES recipe_author(id) ON DELETE CASCADE,
            image TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS recipe_language (
            id INTEGER PRIMARY KEY,
            recipe_id INTEGER NOT NULL
                REFERENCES recipe(id) ON DELETE CASCADE,
            language_id INTEGER NOT NULL
                REFERENCES language(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            UNIQUE (recipe_id, language_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS ingredient (
            id INTEGER PRIMARY KEY
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS ingredient_language (
            id INTEGER PRIMARY KEY,
            ingredient_id INTEGER NOT NULL
                REFERENCES ingredient(id) ON DELETE CASCADE,
            language_id INTEGER NOT NULL
                REFERENCES language(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            UNIQUE (ingredient_id, language_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS recipe_ingredient (
            recipe_id INTEGER NOT NULL
                REFERENCES recipe(id) ON DELETE CASCADE,
            ingredient_id INTEGER NOT NULL
                REFERENCES ingredient(id) ON DELETE CASCADE,
            amount TEXT,
            unit TEXT,
            PRIMARY KEY (recipe_id, ingredient_id)
        )
        """,
        "CREATE INDEX IF NOT EXISTS idx_recipe_category_id ON recipe(category_id)",
        "CREATE INDEX IF NOT EXISTS idx_recipe_author_id ON recipe(author_id)",
        "CREATE INDEX IF NOT EXISTS idx_recipe_category_language_language_id "
        "ON recipe_category_language(language_id)",
        "CREATE INDEX IF NOT EXISTS idx_recipe_language_language_id "
        "ON recipe_language(language_id)",
        "CREATE INDEX IF NOT EXISTS idx_ingredient_language_language_id "
        "ON ingredient_language(language_id)",
        "CREATE INDEX IF NOT EXISTS idx_recipe_ingredient_ingredient_id "
        "ON recipe_ingredient(ingredient_id)",
    )
    for statement in statements:
        conn.execute(statement)
