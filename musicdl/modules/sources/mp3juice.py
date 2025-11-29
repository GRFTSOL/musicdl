'''
Function:
    Implementation of MP3JuiceMusicClient: https://mp3juice.co/
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
import os
import copy
import time
import base64
from urllib.parse import quote
from .base import BaseMusicClient
from urllib.parse import urlencode
from rich.progress import Progress
from ..utils import legalizestring, resp2json, isvalidresp, usesearchheaderscookies, AudioLinkTester, WhisperLRC


'''MP3JuiceMusicClient'''
class MP3JuiceMusicClient(BaseMusicClient):
    source = 'MP3JuiceMusicClient'
    def __init__(self, **kwargs):
        super(MP3JuiceMusicClient, self).__init__(**kwargs)
        self.default_search_headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "priority": "u=1, i",
            "referer": "https://mp3juice.co/",
            "sec-ch-ua": "\"Chromium\";v=\"142\", \"Google Chrome\";v=\"142\", \"Not_A Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
        }
        self.default_download_headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "priority": "u=1, i",
            "referer": "https://mp3juice.co/",
            "sec-ch-ua": "\"Chromium\";v=\"142\", \"Google Chrome\";v=\"142\", \"Not_A Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
        }
        self.default_headers = self.default_search_headers
        self._initsession()
    '''_constructsearchurls'''
    def _constructsearchurls(self, keyword: str, rule: dict = None, request_overrides: dict = None):
        # init
        rule, request_overrides = rule or {}, request_overrides or {}
        # search rules
        default_rule = {'a': 'VjhRUEdNT1BVRDlQSDhIUlkyUjNQNjNLQlZERkM4WURDTkhNTkpBSUxUUlhFNVozXzJ0blU1V1gwaEFUdjJPdDFv', 'y': 's', 'q': keyword, 't': str(int(time.time()))}
        default_rule.update(rule)
        default_rule['q'] = base64.b64encode(quote(keyword, safe="").encode("utf-8")).decode("utf-8")
        # construct search urls based on search rules
        base_url = 'https://mp3juice.co/api/v1/search?'
        page_rule = copy.deepcopy(default_rule)
        search_urls = [base_url + urlencode(page_rule)]
        self.search_size_per_page = self.search_size_per_source
        # return
        return search_urls
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
            search_results = resp2json(resp)
            search_results = list({item.get("id"): item for item in (search_results["yt"] + search_results["sc"])}.values())
            for search_result in search_results:
                # --download results
                if 'id' not in search_result:
                    continue
                download_result = dict()
                # ----init
                params = {'i': 'VjhRUEdNT1BVRDlQSDhIUlkyUjNQNjNLQlZERkM4WURDTkhNTkpBSUxUUlhFNVozXzJ0blU1V1gwaEFUdjJPdDFv', 't': str(int(time.time()))}
                resp = self.get('https://www1.eooc.cc/api/v1/init?', params=params, **request_overrides)
                if not isvalidresp(resp=resp): continue
                download_result['init'] = resp2json(resp=resp)
                conver_url = download_result['init'].get('convertURL', '')
                if not conver_url: continue
                # ----conver
                conver_url = f'{conver_url}&v={search_result["id"]}&f=mp3&t={str(int(time.time()))}'
                resp = self.get(conver_url, **request_overrides)
                if not isvalidresp(resp=resp): continue
                download_result['conver'] = resp2json(resp=resp)
                redirect_url = download_result['conver'].get('redirectURL', '')
                if not redirect_url: continue
                # ----redirect
                resp = self.get(redirect_url, **request_overrides)
                if not isvalidresp(resp=resp): continue
                download_result['redirect'] = resp2json(resp=resp)
                download_url = download_result['redirect'].get('downloadURL', '')
                if not download_url: continue
                # ----check whether download_url is available
                download_url_status = AudioLinkTester(headers=self.default_download_headers, cookies=self.default_download_cookies).test(download_url, request_overrides)
                if not download_url_status['ok']: continue
                # ----prob
                download_result_suppl = AudioLinkTester(headers=self.default_download_headers, cookies=self.default_download_cookies).probe(download_url, request_overrides)
                if download_result_suppl['ext'] == 'NULL': download_result_suppl['ext'] = 'mp3'
                download_result['download_result_suppl'] = download_result_suppl
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
                singers_song_name = search_result.get('title', 'NULL-NULL').split('-')
                if len(singers_song_name) == 1:
                    singers, song_name = 'NULL', singers_song_name[0].strip()
                elif len(singers_song_name) > 1:
                    singers, song_name = singers_song_name[0].strip(), singers_song_name[1].strip()
                song_info = dict(
                    source=self.source, raw_data=dict(search_result=search_result, download_result=download_result, lyric_result=lyric_result), 
                    download_url_status=download_url_status, download_url=download_url, ext=download_result_suppl['ext'], file_size=download_result_suppl['file_size'], 
                    lyric=lyric, duration='-:-:-', song_name=legalizestring(song_name, replace_null_string='NULL'), singers=legalizestring(singers, replace_null_string='NULL'), 
                    album='NULL', identifier=search_result['id'],
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