"""
Language file verification tests.

These are spot-check sanity checks only.  Ideally the tests would
verify that the language definition files are in fact **complete**,
i.e. contain all the necessary fields, but for now this will suffice.
Lute will double-check that the files are valid anyway.
"""

import unittest
import re
from glob import glob
import os
import string
import yaml


class TestVerifyFiles(unittest.TestCase):
    "Verify files."

    def test_definition_files_are_valid_yaml(self):
        "Files must be valid yaml."
        thisdir = os.path.dirname(__file__)
        langglob = os.path.join(thisdir, "**", "definition.yaml")
        for filename in glob(langglob):
            print(filename)
            with open(filename, "r", encoding="utf-8") as f:
                try:
                    d = yaml.safe_load(f)
                except Exception as e:  # pylint: disable=broad-exception-caught
                    self.fail(f"ERROR: {filename} invalid: {e}")
                self.assertTrue(d["name"] is not None, f"{filename} missing name")

    def test_story_files_contain_title(self):
        "Must have # title: at the top."
        thisdir = os.path.dirname(__file__)
        storyglob = os.path.join(thisdir, "**", "*.txt")
        for filename in glob(storyglob):
            print(filename)
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
            retitle = r"title:\s*(.*)\n"
            t = re.search(retitle, content)
            msg = f"{filename} missing '# title:' comment, {retitle}"
            self.assertTrue(t is not None, msg)
            title = t.group(1).strip()
            self.assertTrue(title != "", f"{filename} missing title")


class TestTibetanDefaults(unittest.TestCase):
    """Tibetan word rules must not turn English glosses into vocabulary."""

    @classmethod
    def setUpClass(cls):
        path = os.path.join(os.path.dirname(__file__), "tibetan", "definition.yaml")
        with open(path, encoding="utf-8") as source:
            cls.definition = yaml.safe_load(source)

    def test_word_characters_include_tibetan_but_exclude_ascii(self):
        pattern = re.compile(f"[{self.definition['word_chars']}]", re.IGNORECASE)
        for char in "བོདསྐདༀ":
            with self.subTest(tibetan=char):
                self.assertIsNotNone(pattern.fullmatch(char))
        for codepoint in range(128):
            with self.subTest(ascii=codepoint):
                self.assertIsNone(pattern.fullmatch(chr(codepoint)))

    def test_sentence_exceptions_do_not_match_english_endings(self):
        # Lute treats matched exceptions as words, with case-insensitive matching.
        exceptions = self.definition.get("split_sentence_exceptions", "")
        if not exceptions:
            return
        pattern = re.compile(exceptions.replace(".", r"\."), re.IGNORECASE)
        examples = ["reason.", "etc.", "cognitions.", "above."]
        examples += [char + "." for char in string.ascii_letters]
        for text in examples:
            with self.subTest(text=text):
                self.assertIsNone(pattern.search(text))


if __name__ == "__main__":
    unittest.main()
