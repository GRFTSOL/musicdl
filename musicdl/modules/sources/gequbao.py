'''
Function:
    Implementation of GequbaoMusicClient: https://www.gequbao.com/
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
import re
import json_repair
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .base import BaseMusicClient
from rich.progress import Progress
from ..utils import legalizestring, resp2json, isvalidresp, usesearchheaderscookies, safeextractfromdict, AudioLinkTester


'''GequbaoMusicClient'''
class GequbaoMusicClient(BaseMusicClient):
    source = 'GequbaoMusicClient'
    def __init__(self, **kwargs):
        super(GequbaoMusicClient, self).__init__(**kwargs)
        self.default_search_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        }
        self.default_download_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        }
        self.default_headers = self.default_search_headers
        self._initsession()
    '''_constructsearchurls'''
    def _constructsearchurls(self, keyword: str, rule: dict = None, request_overrides: dict = None):
        # init
        rule, request_overrides = rule or {}, request_overrides or {}
        # construct search urls
        search_urls = [f'https://www.gequbao.com/s/{keyword}']
        self.search_size_per_page = self.search_size_per_source
        # return
        return search_urls
    '''_parsesearchresultsfromhtml'''
    def _parsesearchresultsfromhtml(self, html_text: str):
        soup = BeautifulSoup(html_text, "lxml")
        base_url, search_results = "https://www.gequbao.com", []
        for a in soup.select("a.music-link"):
            href = urljoin(base_url, a.get("href", "").strip())
            title_tag = a.select_one(".music-title span")
            title = title_tag.get_text(strip=True) if title_tag else ""
            artist_tag = a.select_one("small")
            artist = artist_tag.get_text(strip=True) if artist_tag else ""
            search_results.append({'href': href, 'title': title, 'artist': artist})
        return search_results
    '''_search'''
    @usesearchheaderscookies
    def _search(self, keyword: str = '', search_url: str = '', request_overrides: dict = None, song_infos: list = [], progress: Progress = None, progress_id: int = 0):
        # init
        request_overrides = request_overrides or {}
        # successful
        try:
            # --search results
            resp = self.get(search_url, **request_overrides)
            resp.raise_for_status()
            search_results = self._parsesearchresultsfromhtml(resp.text)
            for search_result in search_results:
                # --download results
                if 'href' not in search_result:
                    continue
                resp = self.get(search_result['href'], **request_overrides)
                if not isvalidresp(resp=resp): continue
                soup = BeautifulSoup(resp.text, "lxml")
                script_tag = soup.find("script", string=re.compile(r"window\.appData"))
                if script_tag is None: continue
                js_text = script_tag.string
                m = re.search(r"window\.appData\s*=\s*(\{.*?\})\s*;", js_text, re.S)
                if not m: continue
                download_result = json_repair.loads(m.group(1))
                if 'play_id' not in download_result or not download_result['play_id']: continue
                resp = self.post('https://www.gequbao.com/api/play-url', json={'id': download_result['play_id']}, **request_overrides)
                if not isvalidresp(resp=resp): continue
                download_result['api/play-url'] = resp2json(resp=resp)
                download_url = safeextractfromdict(download_result['api/play-url'], ['data', 'url'], '')
                if not download_url: continue
                download_url_status = AudioLinkTester(headers=self.default_download_headers, cookies=self.default_download_cookies).test(download_url, request_overrides)
                if not download_url_status['ok']: continue
                download_result_suppl = AudioLinkTester(headers=self.default_download_headers, cookies=self.default_download_cookies).probe(download_url, request_overrides)
                if download_result_suppl['ext'] == 'NULL': download_result_suppl['ext'] = 'mp3'
                download_result['download_result_suppl'] = download_result_suppl
                # --lyric results
                try:
                    lrc_div = soup.find("div", id="content-lrc")
                    lyric = lrc_div.get_text("\n", strip=True)
                    lyric_result = {'lrc_div': str(lrc_div)}
                except:
                    lyric, lyric_result = 'NULL', {}
                # --construct song_info
                format_duration = lambda d: "{:02}:{:02}:{:02}".format(*([0] * (3 - len(d.split(":"))) + list(map(int, d.split(":")))))
                duration = format_duration(download_result.get('mp3_duration', '00:00:00') or '00:00:00')
                if duration == '00:00:00': duration = '-:-:-'
                song_info = dict(
                    source=self.source, raw_data=dict(search_result=search_result, download_result=download_result, lyric_result=lyric_result), 
                    download_url_status=download_url_status, download_url=download_url, ext=download_result_suppl['ext'], file_size=download_result_suppl['file_size'], 
                    lyric=lyric, duration=duration, song_name=legalizestring(download_result.get('mp3_title', 'NULL'), replace_null_string='NULL'), 
                    singers=legalizestring(download_result.get('mp3_author', 'NULL'), replace_null_string='NULL'), album='NULL',
                    identifier=download_result['play_id'],
                )
                # --append to song_infos
                song_infos.append(song_info)
                # --judgement for search_size
                if self.strict_limit_search_size_per_page and len(song_infos) >= self.search_size_per_page: break
            # --update progress
            progress.advance(progress_id, 1)
            progress.update(progress_id, description=f"{self.source}.search >>> {search_url} (Success)")
        # failure
        except Exception as err:
            progress.update(progress_id, description=f"{self.source}.search >>> {search_url} (Error: {err})")
        # return
        return song_infos