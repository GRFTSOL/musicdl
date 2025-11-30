'''
Function:
    Implementation of YinyuedaoMusicClient: https://1mp3.top/
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
import os
import json_repair
from bs4 import BeautifulSoup
from .base import BaseMusicClient
from rich.progress import Progress
from ..utils import legalizestring, isvalidresp, usesearchheaderscookies, AudioLinkTester, WhisperLRC


'''YinyuedaoMusicClient'''
class YinyuedaoMusicClient(BaseMusicClient):
    source = 'YinyuedaoMusicClient'
    def __init__(self, **kwargs):
        super(YinyuedaoMusicClient, self).__init__(**kwargs)
        self.default_search_headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "priority": "u=0, i",
            "referer": "https://1mp3.top/",
            "sec-ch-ua": "\"Chromium\";v=\"142\", \"Google Chrome\";v=\"142\", \"Not_A Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
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
        search_urls = [f'https://1mp3.top/?key={keyword}&search=1']
        self.search_size_per_page = self.search_size_per_source
        # return
        return search_urls
    '''_parsesearchresultsfromhtml'''
    def _parsesearchresultsfromhtml(self, html_text: str):
        soup = BeautifulSoup(html_text, "lxml")
        search_results = []
        for li in soup.select("#musicList > li"):
            music_id_attr = li.get("data-music-id")
            music_title_attr = li.get("data-music-title")
            music_singer_attr = li.get("data-music-singer")
            music_cover_attr = li.get("data-music-cover")
            a_download = li.select_one("a.download-btn")
            music_json_str = a_download.get("data-music")
            music_data = json_repair.loads(music_json_str)
            search_results.append({
                "id_attr": music_id_attr, "title_attr": music_title_attr, "singer_attr": music_singer_attr, "cover_attr": music_cover_attr,
                "id": music_data.get("id"), "title": music_data.get("title"), "singer": music_data.get("singer"), "picurl": music_data.get("picurl"),
                "create_time": music_data.get("create_time"), "mtype": music_data.get("mtype"), "downlist": music_data.get("downlist", []),
                "ktmdownlist": music_data.get("ktmdownlist", []),
            })
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
                if 'id' not in search_result:
                    continue
                resp = self.get(f'https://1mp3.top/include/geturl.php?id={search_result["id"]}', **request_overrides)
                if not isvalidresp(resp=resp): continue
                download_url = resp.text.strip()
                if not download_url: continue
                download_url_status = AudioLinkTester(headers=self.default_download_headers, cookies=self.default_download_cookies).test(download_url, request_overrides)
                if not download_url_status['ok']: continue
                download_result = AudioLinkTester(headers=self.default_download_headers, cookies=self.default_download_cookies).probe(download_url, request_overrides)
                if download_result['ext'] == 'NULL': download_result['ext'] = 'mp3'
                # --lyric results
                try:
                    if os.environ.get('ENABLE_WHISPERLRC', 'False').lower() == 'true':
                        lyric_result = WhisperLRC(model_size_or_path='small').fromurl(
                            download_url, headers=self.default_download_headers, cookies=self.default_download_cookies, request_overrides=request_overrides
                        )
                        lyric = lyric_result['lyric']
                    else:
                        lyric_result, lyric = dict(), 'NULL'
                except:
                    lyric_result, lyric = dict(), 'NULL'
                # --construct song_info
                song_info = dict(
                    source=self.source, raw_data=dict(search_result=search_result, download_result=download_result, lyric_result=lyric_result), 
                    download_url_status=download_url_status, download_url=download_url, ext=download_result['ext'], file_size=download_result['file_size'], 
                    lyric=lyric, duration='-:-:-', song_name=legalizestring(search_result.get('title', 'NULL'), replace_null_string='NULL'), 
                    singers=legalizestring(search_result.get('singer', 'NULL'), replace_null_string='NULL'), album='NULL',
                    identifier=search_result['id'],
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