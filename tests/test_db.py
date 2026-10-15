import sqlite3
import unittest

from recipes.db import init_db


class TestInitDb(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        init_db(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_init_db_is_idempotent(self):
        init_db(self.conn)
        table_names = {
            row[0]
            for row in self.conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        self.assertTrue(
            {
                "language",
                "recipe_category",
                "recipe_category_language",
                "recipe_author",
                "recipe",
                "recipe_language",
                "ingredient",
                "ingredient_language",
                "recipe_ingredient",
            }.issubset(table_names)
        )

    def insert_related_records(self):
        self.conn.executescript("""
            INSERT INTO language (id, name, code) VALUES (1, 'English', 'en');
            INSERT INTO recipe_category (id) VALUES (1);
            INSERT INTO recipe_category_language
                (recipe_category_id, language_id, name)
                VALUES (1, 1, 'Dinner');
            INSERT INTO recipe_author (id, name) VALUES (1, 'Alex');
            INSERT INTO recipe (id, category_id, author_id)
                VALUES (1, 1, 1);
            INSERT INTO recipe_language (recipe_id, language_id, name)
                VALUES (1, 1, 'Soup');
            INSERT INTO ingredient (id) VALUES (1);
            INSERT INTO ingredient_language (ingredient_id, language_id, name)
                VALUES (1, 1, 'Carrot');
            INSERT INTO recipe_ingredient (recipe_id, ingredient_id)
                VALUES (1, 1);
            """)

    def count_rows(self, table):
        return self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    def test_deleting_author_cascades_to_recipes_and_dependents(self):
        self.insert_related_records()

        self.conn.execute("DELETE FROM recipe_author WHERE id = 1")

        self.assertEqual(self.count_rows("recipe"), 0)
        self.assertEqual(self.count_rows("recipe_language"), 0)
        self.assertEqual(self.count_rows("recipe_ingredient"), 0)
        self.assertEqual(self.count_rows("ingredient"), 1)

    def test_deleting_category_cascades_to_recipes_and_dependents(self):
        self.insert_related_records()

        self.conn.execute("DELETE FROM recipe_category WHERE id = 1")

        self.assertEqual(self.count_rows("recipe_category_language"), 0)
        self.assertEqual(self.count_rows("recipe"), 0)
        self.assertEqual(self.count_rows("recipe_language"), 0)
        self.assertEqual(self.count_rows("recipe_ingredient"), 0)
        self.assertEqual(self.count_rows("recipe_author"), 1)
        self.assertEqual(self.count_rows("ingredient"), 1)

    def test_deleting_recipe_cascades_to_languages_and_ingredients(self):
        self.insert_related_records()

        self.conn.execute("DELETE FROM recipe WHERE id = 1")

        self.assertEqual(self.count_rows("recipe_language"), 0)
        self.assertEqual(self.count_rows("recipe_ingredient"), 0)
        self.assertEqual(self.count_rows("ingredient"), 1)

    def test_deleting_ingredient_cascades_to_languages_and_recipe_links(self):
        self.insert_related_records()

        self.conn.execute("DELETE FROM ingredient WHERE id = 1")

        self.assertEqual(self.count_rows("ingredient_language"), 0)
        self.assertEqual(self.count_rows("recipe_ingredient"), 0)
        self.assertEqual(self.count_rows("recipe"), 1)

    def test_deleting_language_cascades_to_all_translations(self):
        self.insert_related_records()

        self.conn.execute("DELETE FROM language WHERE id = 1")

        self.assertEqual(self.count_rows("recipe_category_language"), 0)
        self.assertEqual(self.count_rows("recipe_language"), 0)
        self.assertEqual(self.count_rows("ingredient_language"), 0)
        self.assertEqual(self.count_rows("recipe_category"), 1)
        self.assertEqual(self.count_rows("recipe"), 1)
        self.assertEqual(self.count_rows("ingredient"), 1)

    def test_inserting_records_with_missing_foreign_keys_raises_error(self):
        self.insert_related_records()
        self.conn.executescript("""
            INSERT INTO recipe_category (id) VALUES (2);
            INSERT INTO recipe_author (id, name) VALUES (2, 'Sam');
            INSERT INTO recipe (id, category_id, author_id) VALUES (2, 2, 2);
            INSERT INTO ingredient (id) VALUES (2);
            """)

        invalid_inserts = (
            (
                "category translation with missing category",
                "INSERT INTO recipe_category_language "
                "(recipe_category_id, language_id, name) VALUES (99, 1, 'Dinner')",
            ),
            (
                "category translation with missing language",
                "INSERT INTO recipe_category_language "
                "(recipe_category_id, language_id, name) VALUES (2, 99, 'Dinner')",
            ),
            (
                "recipe with missing category",
                "INSERT INTO recipe (category_id, author_id) VALUES (99, 1)",
            ),
            (
                "recipe with missing author",
                "INSERT INTO recipe (category_id, author_id) VALUES (1, 99)",
            ),
            (
                "recipe translation with missing recipe",
                "INSERT INTO recipe_language (recipe_id, language_id, name) "
                "VALUES (99, 1, 'Stew')",
            ),
            (
                "recipe translation with missing language",
                "INSERT INTO recipe_language (recipe_id, language_id, name) "
                "VALUES (2, 99, 'Stew')",
            ),
            (
                "ingredient translation with missing ingredient",
                "INSERT INTO ingredient_language (ingredient_id, language_id, name) "
                "VALUES (99, 1, 'Celery')",
            ),
            (
                "ingredient translation with missing language",
                "INSERT INTO ingredient_language (ingredient_id, language_id, name) "
                "VALUES (2, 99, 'Celery')",
            ),
            (
                "recipe ingredient with missing recipe",
                "INSERT INTO recipe_ingredient (recipe_id, ingredient_id) "
                "VALUES (99, 1)",
            ),
            (
                "recipe ingredient with missing ingredient",
                "INSERT INTO recipe_ingredient (recipe_id, ingredient_id) "
                "VALUES (2, 99)",
            ),
        )

        for relation, statement in invalid_inserts:
            with self.subTest(relation=relation):
                with self.assertRaises(sqlite3.IntegrityError):
                    self.conn.execute(statement)
