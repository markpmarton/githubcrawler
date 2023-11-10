import os
import unittest
import json
from ghcrawler import GhCrawler

class TestGhCrawler(unittest.TestCase):

    _WORKING_PROXY = "195.225.232.3:8085"

    def test_no_input(self):
        test_inp = None 
        with self.assertRaises(Exception):
            GhCrawler(test_inp, out_path=None).run()


    def test_bad_input(self):
        test_inp = {
                "k":"test",
                "proxies":[],
                "type": "Issues"
                }

        with self.assertRaises(Exception):
            GhCrawler(test_inp, out_path=None).run()

    def test_no_proxy(self):
        test_inp = {
                "keywords":[
                    "rust"
                    ],
                "proxies":[],
                "type": "Issues"
                }

        with self.assertRaises(Exception):
            GhCrawler(test_inp, out_path=None).run()

    def test_bad_proxy(self):
        test_inp = {
                "keywords":[
                    "rust"
                    ],
                "proxies":[
                    "1.1.1.1"
                    ],
                "type": "Issues"
                }

        with self.assertRaises(Exception):
            GhCrawler(test_inp, out_path=None).run()

    def test_no_keywords(self):
        test_inp = {
                "keywords":[],
                "proxies":[
                    self._WORKING_PROXY
                    ],
                "type": "Issues"
                }

        with self.assertRaises(Exception):
            GhCrawler(test_inp, out_path=None).run()

    def test_bad_type(self):
        test_inp = {
                "keywords":[
                    "rust"
                    ],
                "proxies":[
                    self._WORKING_PROXY
                    ],
                "type": "Topics"
                }

        with self.assertRaises(Exception):
            GhCrawler(test_inp, out_path=None).run()

    def test_issues_good_input_out_given_single_kw(self):
        test_inp = {
                "keywords":[
                    "rust"
                    ],
                "proxies":[
                    self._WORKING_PROXY
                    ],
                "type": "Issues"
                }

        GhCrawler(test_inp, out_path="test_out.json").run()


        res_json = {}
        with open("test_out.json") as reader:
            res_json = json.load(reader)

        self.assertEqual(len(res_json),10)
        first_url = res_json[0]
        self.assertIn("url", first_url)
        os.remove("test_out.json")

    def test_issues_good_input_no_out_single_kw(self):
        test_inp = {
                "keywords":[
                    "rust"
                    ],
                "proxies":[
                    self._WORKING_PROXY
                    ],
                "type": "Issues"
                }

        GhCrawler(test_inp, out_path=None).run()


        res_json = {}
        with open("result.json") as reader:
            res_json = json.load(reader)

        self.assertEqual(len(res_json),10)
        first_url = res_json[0]
        self.assertIn("url", first_url)
        os.remove("result.json")

    def test_issues_good_input_no_out_multiple_kw(self):
        test_inp = {
                "keywords":[
                    "rust",
                    "go"
                    ],
                "proxies":[
                    self._WORKING_PROXY
                    ],
                "type": "Issues"
                }

        GhCrawler(test_inp, out_path=None).run()


        res_json = {}
        with open("result.json") as reader:
            res_json = json.load(reader)

        self.assertEqual(len(res_json),20)
        first_url = res_json[0]
        self.assertIn("url", first_url)
        os.remove("result.json")


    def test_wikis_good_input_out_given_single_kw(self):
        test_inp = {
                "keywords":[
                    "rust"
                    ],
                "proxies":[
                    self._WORKING_PROXY
                    ],
                "type": "Wikis"
                }

        GhCrawler(test_inp, out_path="test_out.json").run()


        res_json = {}
        with open("test_out.json") as reader:
            res_json = json.load(reader)

        self.assertEqual(len(res_json), 9)
        first_url = res_json[0]
        self.assertIn("url", first_url)
        os.remove("test_out.json")

    def test_wikis_good_input_no_out_single_kw(self):
        test_inp = {
                "keywords":[
                    "rust"
                    ],
                "proxies":[
                    self._WORKING_PROXY
                    ],
                "type": "Wikis"
                }

        GhCrawler(test_inp, out_path=None).run()


        res_json = {}
        with open("result.json") as reader:
            res_json = json.load(reader)

        self.assertEqual(len(res_json),9)
        first_url = res_json[0]
        self.assertIn("url", first_url)
        os.remove("result.json")

    def test_wikis_good_input_no_out_multiple_kw(self):
        test_inp = {
                "keywords":[
                    "rust",
                    "go"
                    ],
                "proxies":[
                    self._WORKING_PROXY
                    ],
                "type": "Wikis"
                }

        GhCrawler(test_inp, out_path=None).run()


        res_json = {}
        with open("result.json") as reader:
            res_json = json.load(reader)

        self.assertEqual(len(res_json),19)
        first_url = res_json[0]
        self.assertIn("url", first_url)
        os.remove("result.json")

    def test_repos_good_input_out_given_single_kw(self):
        test_inp = {
                "keywords":[
                    "rust"
                    ],
                "proxies":[
                    self._WORKING_PROXY
                    ],
                "type": "Repositories"
                }

        GhCrawler(test_inp, out_path="test_out.json").run()


        res_json = {}
        with open("test_out.json") as reader:
            res_json = json.load(reader)

        self.assertEqual(len(res_json),10)
        first_url = res_json[0]
        self.assertIn("url", first_url)
        self.assertIn("extra", first_url)
        self.assertIn("owner", first_url["extra"])
        self.assertIn("language_stats", first_url["extra"])
        os.remove("test_out.json")

    def test_repos_good_input_no_out_single_kw(self):
        test_inp = {
                "keywords":[
                    "rust"
                    ],
                "proxies":[
                    self._WORKING_PROXY
                    ],
                "type": "Repositories"
                }

        GhCrawler(test_inp, out_path=None).run()


        res_json = {}
        with open("result.json") as reader:
            res_json = json.load(reader)

        self.assertEqual(len(res_json),10)
        first_url = res_json[0]
        self.assertIn("url", first_url)
        self.assertIn("extra", first_url)
        self.assertIn("owner", first_url["extra"])
        self.assertIn("language_stats", first_url["extra"])
        os.remove("result.json")

    def test_repos_good_input_no_out_multiple_kw(self):
        test_inp = {
                "keywords":[
                    "rust",
                    "go"
                    ],
                "proxies":[
                    self._WORKING_PROXY
                    ],
                "type": "Repositories"
                }

        GhCrawler(test_inp, out_path=None).run()


        res_json = {}
        with open("result.json") as reader:
            res_json = json.load(reader)

        self.assertEqual(len(res_json),20)
        first_url = res_json[0]
        self.assertIn("url", first_url)
        self.assertIn("extra", first_url)
        self.assertIn("owner", first_url["extra"])
        self.assertIn("language_stats", first_url["extra"])
        os.remove("result.json")
        
