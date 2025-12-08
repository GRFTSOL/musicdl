'''
Function:
    Implementation of QianqianMusicClient: http://music.taihe.com/
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
import re
import time
import copy
import hashlib
from .base import BaseMusicClient
from urllib.parse import urlencode
from rich.progress import Progress
from ..utils import byte2mb, resp2json, seconds2hms, legalizestring, safeextractfromdict, usesearchheaderscookies, SongInfo


'''QianqianMusicClient'''
class QianqianMusicClient(BaseMusicClient):
    source = 'QianqianMusicClient'
    def __init__(self, **kwargs):
        super(QianqianMusicClient, self).__init__(**kwargs)
        self.appid = '16073360'
        self.default_search_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'Referer': 'https://music.91q.com/',
            'From': 'Web',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        self.default_download_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        }
        self.default_headers = self.default_search_headers
        self._initsession()
    '''_addsignandtstoparams'''
    def _addsignandtstoparams(self, params: dict):
        secret = '0b50b02fd0d73a9c4c8c3a781c30845f'
        params['timestamp'] = str(int(time.time()))
        keys = sorted(params.keys())
        string = "&".join(f"{k}={params[k]}" for k in keys)
        params['sign'] = hashlib.md5((string + secret).encode('utf-8')).hexdigest()
        return params
    '''_constructsearchurls'''
    def _constructsearchurls(self, keyword: str, rule: dict = None, request_overrides: dict = None):
        # init
        rule, request_overrides = rule or {}, request_overrides or {}
        # search rules
        default_rule = {'word': keyword, 'type': '1', 'pageNo': '1', 'pageSize': '10', 'appid': self.appid}
        default_rule.update(rule)
        # construct search urls based on search rules
        base_url = 'https://music.91q.com/v1/search?'
        search_urls, page_size, count = [], self.search_size_per_page, 0
        while self.search_size_per_source > count:
            page_rule = copy.deepcopy(default_rule)
            page_rule['pageSize'] = page_size
            page_rule['pageNo'] = str(int(count // page_size) + 1)
            page_rule = self._addsignandtstoparams(params=page_rule)
            search_urls.append(base_url + urlencode(page_rule))
            count += page_size
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
            search_results = resp2json(resp)['data']['typeTrack']
            for search_result in search_results:
                # --download results
                if not isinstance(search_result, dict) or ('TSID' not in search_result):
                    continue
                song_info = SongInfo(source=self.source)
                for rate in ['64', '128', '320', '3000'][::-1]:
                    params = {'TSID': search_result['TSID'], 'appid': self.appid, 'rate': rate}
                    params = self._addsignandtstoparams(params=params)
                    try:
                        resp = self.get("https://music.91q.com/v1/song/tracklink", params=params, **request_overrides)
                        resp.raise_for_status()
                        download_result: dict = resp2json(resp)
                        download_url = safeextractfromdict(download_result, ['data', 'path'], '')
                        if not download_url: continue
                        song_info = SongInfo(
                            source=self.source, download_url=download_url, download_url_status=self.audio_link_tester.test(download_url, request_overrides),
                            raw_data={'search': search_result, 'download': download_result}, file_size_bytes=download_result['data'].get('size', 0), 
                            file_size=byte2mb(download_result['data'].get('size', 0)), duration_s=download_result['data'].get('duration', 0),
                            duration = seconds2hms(download_result['data'].get('duration', 0)), ext=download_result['data'].get('format', 'mp3')
                        )
                        if song_info.with_valid_download_url: break
                    except:
                        continue
                if not song_info.with_valid_download_url: continue
                song_info.download_url_status['prob_status'] = self.audio_link_tester.probe(song_info.download_url, request_overrides)
                ext, file_size = song_info.download_url_status['prob_status']['ext'], song_info.download_url_status['prob_status']['file_size']
                if file_size and file_size != 'NULL': song_info.file_size = file_size
                if ext and ext != 'NULL': song_info.ext = ext
                song_info.update(dict(
                    song_name=legalizestring(search_result.get('title', 'NULL'), replace_null_string='NULL'), 
                    singers=legalizestring(', '.join([singer.get('name', 'NULL') for singer in search_result.get('artist', [])]), replace_null_string='NULL'), 
                    album=legalizestring(search_result.get('albumTitle', 'NULL'), replace_null_string='NULL'),
                    identifier=search_result['TSID'],
                ))
                # --lyric results
                try:
                    resp = self.get(search_result['lyric'], **request_overrides)
                    resp.raise_for_status()
                    resp.encoding = 'utf-8'
                    lyric = resp.text or 'NULL'
                    lyric_result = dict(lyric=lyric)
                    if song_info.singers == 'NULL':
                        try:
                            song_info.singers = re.findall(r'\[ar:(.*?)\]', lyric)[0]
                        except:
                            song_info.singers = 'NULL'
                except:
                    lyric_result, lyric = dict(), 'NULL'
                song_info.raw_data['lyric'] = lyric_result
                song_info.lyric = lyric
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