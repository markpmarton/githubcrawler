import os
import json
import aiohttp
import asyncio
import random
from datetime import datetime
from selectolax.parser import HTMLParser


class GhCrawler:
    """The class handling all the crawler jobs."""

    _MAX_DOWNLOAD_TRIES = 10  # How many times should the crawler try to download a page (with random proxies)
    _TIMEOUT = 10  # In seconds.
    _DOWNLOAD_JOB_LIMIT = 0  # Sets, how many downloaders can run at the same time. 0 means it's unlimited.

    def log_to_console(self, level, url, msg, act_try_count, proxy):
        """Simple console printer to get info about the downloads"""
        print(
            "[{}][{}][{}][{}][{}/{}][{}]".format(
                datetime.now().strftime("%H:%M:%S.%f"),
                level,
                url,
                proxy,
                act_try_count,
                self._MAX_DOWNLOAD_TRIES,
                msg,
            )
        )

    def __init__(self, inp_config, out_path):
        if inp_config:
            if "proxies" in inp_config and len(inp_config["proxies"]) > 0:
                self.proxies = inp_config["proxies"]
            else:
                self.log_to_console(
                    "ERROR", "-", "no proxies found in the input config", "-", "-"
                )
                raise Exception("No proxy found in the input config")

            if "type" in inp_config and inp_config["type"].lower() in [
                "repositories",
                "wikis",
                "issues",
            ]:
                self.type = inp_config["type"].lower()
            else:
                self.log_to_console(
                    "ERROR", "-", "no type found in the input config", "-", "-"
                )
                raise Exception("No valid type found in the input config")

            if "keywords" in inp_config and len(inp_config["keywords"]) > 0:
                self.urls = [
                    "https://github.com/search?q={}&type={}".format(
                        act_keyword, self.type
                    )
                    for act_keyword in inp_config["keywords"]
                ]
            else:
                self.log_to_console(
                    "ERROR", "-", "no keywords found in the input config", "-", "-"
                )
                raise Exception("No keywords found in the input config")

            self.out_path = out_path if out_path else "result.json"
        else:
            raise Exception("Invalid input received")

    def collect_url(self, tree, selector):
        """Collect url-s from list elements defined in selector"""
        for li_elem in tree.css(selector):
            yield json.loads(
                li_elem.css_first("a[data-hydro-click]").attributes["data-hydro-click"]
            )["payload"]["result"]["url"]

    async def _concurrent_download(self, urls=None):
        """Highly concurrent downloader based on aiohttp and asyncio. Each download runs in its own coroutine."""
        """The proxies are randomly selected for each coroutine and if the download fails, retries with a different proxy."""
        """If the connection times out, the used proxy will be blocklisted temporarily. If all proxies became blocked, the list resets."""
        """Max. 100 connection can be established to the same endpoint in the same time."""
        """DNS resolutions are cached for 2 minutes. Most crawling jobs can finish during this time."""
        conn = aiohttp.TCPConnector(
            limit_per_host=10, limit=self._DOWNLOAD_JOB_LIMIT, ttl_dns_cache=120
        )
        async with aiohttp.ClientSession(connector=conn) as session:

            async def get(url):
                """The main task of the coroutines."""
                """Each one handles the download independently and returns its data to the loop gatherer."""
                tries = 0
                selected_proxy = ""
                blocking_proxies = []
                while tries < self._MAX_DOWNLOAD_TRIES:
                    non_blocking_proxies = list(
                        filter(
                            lambda proxy: proxy not in blocking_proxies, self.proxies
                        )
                    )
                    if len(non_blocking_proxies) > 0:
                        selected_proxy = random.choice(non_blocking_proxies)
                    else:
                        blocking_proxies = []
                        selected_proxy = random.choice(self.proxies)

                    try:
                        self.log_to_console(
                            "INFO", url, "Crawling started", tries, selected_proxy
                        )
                        async with session.get(
                            url,
                            ssl=True,
                            proxy="http://{}".format(selected_proxy),
                            timeout=aiohttp.ClientTimeout(total=self._TIMEOUT),
                        ) as response:
                            obj = await response.read()
                            if response.status == 200:
                                self.log_to_console(
                                    "INFO",
                                    url,
                                    "Finished successfully!",
                                    tries,
                                    selected_proxy,
                                )
                                return obj
                            else:
                                self.log_to_console(
                                    "WARNING",
                                    url,
                                    "Download failed! Status: {}".format(
                                        response.status
                                    ),
                                    tries,
                                    selected_proxy,
                                )
                                tries += 1
                    except asyncio.exceptions.TimeoutError:
                        self.log_to_console(
                            "ERROR", url, "Timeout.", tries, selected_proxy
                        )
                        blocking_proxies.append(selected_proxy)
                        tries += 1
                    except Exception as e:
                        self.log_to_console("ERROR", url, str(e), tries, selected_proxy)
                        tries += 1
                self.log_to_console(
                    "CRITICAL",
                    url,
                    "Download tries exceeded. Try to replace proxies. Closing.",
                    tries,
                    selected_proxy,
                )
                raise Exception(
                    "Download tries exceeded. Try to replace proxies. Closing."
                )

            async def get_url_with_repo(url):
                """A helper function for the coroutines to be able to bind url-s to pages."""
                """Used while crawling the repository pages"""
                page = await get(url)
                return [url, page.decode("utf-8")]

            merged_urls = []
            for act_page in await asyncio.gather(*(get(url) for url in self.urls)):
                for act_elem in self.parser_selector(act_page.decode("utf-8")):
                    merged_urls.append(act_elem)

            if "repositories" in self.type:
                self.log_to_console(
                    "INFO",
                    "-",
                    "Repo list download finished! Starting crawling extra data...",
                    "-",
                    "-",
                )
                urls = [act_url["url"] for act_url in merged_urls]
                urls_w_repo_pages = await asyncio.gather(
                    *(get_url_with_repo(url) for url in urls)
                )
                merged_urls = self.parser_selector(urls_w_repo_pages)

        return merged_urls

    def parse_content_repo_page(self, params):
        """Collects owner and language info from the repository pages"""
        results = []
        for act_page in params:
            tree = HTMLParser(act_page[1])
            url = act_page[0]
            author = tree.css_first("a[rel=author]")
            langs = {}
            for act_lang in tree.css(
                "a[data-ga-click='Repository, language stats search click, location:repo overview']"
            ):
                lang_name = act_lang.css_first("span:first-of-type").text()
                lang_perc = act_lang.css_first("span:nth-of-type(2)").text()
                langs[lang_name] = float(lang_perc.replace("%", ""))
            results.append(
                {"url": url, "extra": {"owner": author.text(), "language_stats": langs}}
            )
        return results

    def parse_content_repositories(self, page_string):
        """Collects the repo links from the search list"""
        tree = HTMLParser(page_string)
        results = [
            {"url": act_url} for act_url in self.collect_url(tree, "li.repo-list-item")
        ]
        return results

    def parse_content_issues(self, page_string):
        """Collects the issue links from the search list"""
        tree = HTMLParser(page_string)
        results = [
            {"url": act_url}
            for act_url in self.collect_url(tree, "div.issue-list-item")
        ]
        return results

    def parse_content_wikis(self, page_string):
        """Collects the wiki links from the search list"""
        tree = HTMLParser(page_string)
        results = [
            {"url": act_url} for act_url in self.collect_url(tree, "div.hx_hit-wiki")
        ]
        return results

    def parser_selector(self, params):
        """Handles the selection of parsers based on input parameters."""
        if "repositories" in self.type:
            if isinstance(params[0], list):
                return self.parse_content_repo_page(params)
            else:
                return self.parse_content_repositories(params)
        elif "issues" in self.type:
            return self.parse_content_issues(params)
        elif "wikis" in self.type:
            return self.parse_content_wikis(params)
        return []

    def output_result(self, result):
        """Saves the parsed json data in a file (based on the out_path parameter)."""
        out_full_path = os.path.join(os.getcwd(), self.out_path)
        print("INFO: Extracting results into {}.".format(out_full_path))
        with open(out_full_path, "w") as writer:
            json.dump(result, writer)

    def run(self):
        """Defines the coroutine loop and executes the crawling."""
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(self._concurrent_download())

        self.output_result(results)
