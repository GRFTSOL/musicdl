'''
Function:
    Implementation of GDStudioMusicClient: https://music.gdstudio.xyz/
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
import copy
import time
import random
import hashlib
import json_repair
from urllib.parse import quote
from rich.progress import Progress
from ..sources import BaseMusicClient
from ..utils import legalizestring, resp2json, usesearchheaderscookies, byte2mb, estimatedurationwithfilesizebr, SongInfo


'''SUPPORTED_SITES'''
SUPPORTED_SITES = [
    'spotify', 'tencent', 'netease', 'kuwo', 'tidal', 'qobuz', 'joox', 'bilibili', 'apple', 'ytmusic'
]


'''GDStudioMusicClient'''
class GDStudioMusicClient(BaseMusicClient):
    source = 'GDStudioMusicClient'
    def __init__(self, **kwargs):
        super(GDStudioMusicClient, self).__init__(**kwargs)
        self.default_search_headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        }
        self.default_download_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        }
        self.default_headers = self.default_search_headers
        self._initsession()
    '''_yieldcallback'''
    def _yieldcallback(self):
        random_num = ''.join([str(random.randint(0, 9)) for _ in range(21)])
        timestamp = int(time.time() * 1000)
        return f"jQuery{random_num}_{timestamp}"
    '''_yieldcrc32'''
    def _yieldcrc32(self, id, timestamp=None):
        if timestamp is None: timestamp = int(time.time() * 1000)
        combined = f"music.gdstudio.xyz|20251104|{str(timestamp)[:9]}|{quote(id)}"
        return hashlib.md5(combined.encode()).hexdigest()[-8:].upper()
    '''_constructsearchurls'''
    def _constructsearchurls(self, keyword: str, rule: dict = None, request_overrides: dict = None):
        # init
        rule, request_overrides = rule or {}, request_overrides or {}
        # search rules
        default_rule = {'types': 'search', 'count': self.search_size_per_page, 'pages': '1', 'name': keyword}
        default_rule.update(rule)
        # construct search urls based on search rules
        base_url = 'https://music.gdstudio.xyz/api.php'
        search_urls, page_size = [], self.search_size_per_page
        for source in SUPPORTED_SITES:
            source_default_rule = copy.deepcopy(default_rule)
            source_default_rule['source'], count = source, 0
            while self.search_size_per_source > count:
                page_rule = copy.deepcopy(source_default_rule)
                page_rule['pages'] = str(int(count // page_size) + 1)
                page_rule['count'] = str(page_size)
                page_rule['s'] = self._yieldcrc32(keyword)
                search_urls.append({'url': base_url, 'data': page_rule, 'params': {'callback': self._yieldcallback()}})
                count += page_size
        # return
        return search_urls
    '''_search'''
    @usesearchheaderscookies
    def _search(self, keyword: str = '', search_url: dict = None, request_overrides: dict = None, song_infos: list = [], progress: Progress = None, progress_id: int = 0):
        # init
        request_overrides = request_overrides or {}
        search_meta = copy.deepcopy(search_url)
        search_url, base_url = search_meta.pop('url'), 'https://music.gdstudio.xyz/'
        # successful
        try:
            # --search results
            resp = self.post(search_url, **search_meta, **request_overrides)
            resp.raise_for_status()
            json_str = resp.text[resp.text.index('(')+1: resp.text.rindex(')')]
            search_results = json_repair.loads(json_str)
            for search_result in search_results:
                # --download results
                if (not isinstance(search_result, dict)) or ('id' not in search_result) or ('url_id' not in search_result) or ('source' not in search_result):
                    continue
                song_info = SongInfo(source=self.source, root_source=search_result['source'])
                for br in [320, 192, 128, 96, 64]: # it seems only up to br=320 for all sources and music files
                    params = {'callback': self._yieldcallback()}
                    data_json = {'types': 'url', 'id': search_result['id'], 'source': search_result['source'], 'br': br, 's': self._yieldcrc32(search_result['id'])}
                    try:
                        resp = self.post('https://music.gdstudio.xyz/api.php?', params=params, data=data_json, **request_overrides)
                        resp.raise_for_status()
                        download_result = resp2json(resp=resp)
                    except:
                        continue
                    if not download_result.get('url'): continue
                    download_url = download_result['url']
                    if not download_url.startswith('http'): download_url = base_url + download_url
                    song_info = SongInfo(
                        source=self.source, download_url=download_url, download_url_status=self.audio_link_tester.test(download_url, request_overrides),
                        ext=download_url.split('.')[-1].split('?')[0], file_size_bytes=download_result.get('size', 0), file_size=byte2mb(download_result.get('size', 0)),
                        duration=estimatedurationwithfilesizebr(download_result.get('size', 0), download_result.get('br', br)), raw_data={'search': search_result, 'download': download_result},
                        song_name=legalizestring(search_result.get('name', 'NULL'), replace_null_string='NULL'), identifier=f"{search_result['source']}_{search_result['id']}",
                        singers=legalizestring(', '.join(search_result.get('artist', 'NULL')), replace_null_string='NULL'),
                        album=legalizestring(search_result.get('album', 'NULL'), replace_null_string='NULL'), root_source=search_result['source'],
                    )
                    if song_info.with_valid_download_url: break
                    return
                if not song_info.with_valid_download_url: continue
                song_info.download_url_status['probe_status'] = self.audio_link_tester.probe(song_info.download_url, request_overrides)
                ext, file_size = song_info.download_url_status['probe_status']['ext'], song_info.download_url_status['probe_status']['file_size']
                if file_size and file_size != 'NULL': song_info.file_size = file_size
                if ext and ext != 'NULL': song_info.ext = ext
                # --lyric results
                try:
                    params = {'callback': self._yieldcallback()}
                    data_json = {'types': 'lyric', 'id': search_result['lyric_id'], 'source': search_result['source'], 's': self._yieldcrc32(search_result['lyric_id'])}
                    resp = self.post('https://music-api-hk.gdstudio.xyz/api.php', data=data_json, params=params, **request_overrides)
                    resp.raise_for_status()
                    lyric_result = resp2json(resp=resp)
                    lyric = lyric_result.get('lyric') or lyric_result.get('tlyric') or 'NULL'
                except:
                    lyric_result, lyric = dict(), 'NULL'
                song_info.lyric = lyric
                song_info.raw_data['lyric'] = lyric_result
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