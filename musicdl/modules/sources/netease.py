'''
Function:
    Implementation of NeteaseMusicClient: https://music.163.com/
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
import json
import copy
import random
from .base import BaseMusicClient
from rich.progress import Progress
from ..utils.neteaseutils import EapiCryptoUtils
from ..utils import resp2json, seconds2hms, legalizestring, safeextractfromdict, usesearchheaderscookies, SongInfo


'''NeteaseMusicClient'''
class NeteaseMusicClient(BaseMusicClient):
    source = 'NeteaseMusicClient'
    def __init__(self, **kwargs):
        super(NeteaseMusicClient, self).__init__(**kwargs)
        self.default_search_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'Referer': 'https://music.163.com/',
        }
        self.default_download_headers = {}
        self.default_headers = self.default_search_headers
        default_cookies = {'MUSIC_U': '1eb9ce22024bb666e99b6743b2222f29ef64a9e88fda0fd5754714b900a5d70d993166e004087dd3b95085f6a85b059f5e9aba41e3f2646e3cebdbec0317df58c119e5'}
        if not self.default_search_cookies: self.default_search_cookies = default_cookies
        if not self.default_download_cookies: self.default_download_cookies = default_cookies
        self._initsession()
    '''_parsewithcggapi'''
    def _parsewithcggapi(self, search_result: dict, request_overrides: dict = None):
        # init
        request_overrides, song_id = request_overrides or {}, search_result['id']
        # _safefetchfilesize
        def _safefetchfilesize(meta: dict):
            if not isinstance(meta, dict): return 0
            file_size = str(meta.get('size', '0.00MB'))
            file_size = file_size.removesuffix('MB').strip()
            try: return float(file_size)
            except: return 0
        # parse
        for quality in ['jymaster', 'sky', 'jyeffect', 'hires', 'lossless', 'exhigh', 'standard']:
            try:
                resp = self.get(url=f'https://api-v1.cenguigui.cn/api/netease/music_v1.php?id={song_id}&type=json&level={quality}', **request_overrides)
                resp.raise_for_status()
                download_result = resp2json(resp=resp)
                if 'data' not in download_result or (_safefetchfilesize(download_result['data']) < 0.01): continue
            except:
                continue
            download_url: str = download_result['data'].get('url', '')
            if not download_url: continue
            song_info = SongInfo(
                source=self.source, download_url=download_url, download_url_status=self.audio_link_tester.test(download_url, request_overrides),
                ext=download_url.split('.')[-1].split('?')[0], raw_data={'search': search_result, 'download': download_result},
            )
            song_info.download_url_status['probe_status'] = self.audio_link_tester.probe(song_info.download_url, request_overrides)
            ext, file_size = song_info.download_url_status['probe_status']['ext'], song_info.download_url_status['probe_status']['file_size']
            if file_size and file_size != 'NULL': song_info.file_size = file_size
            if not song_info.file_size: song_info.file_size = 'NULL'
            if ext and ext != 'NULL': song_info.ext = ext
            if song_info.with_valid_download_url: break
        # return
        return song_info, quality
    '''_constructsearchurls'''
    def _constructsearchurls(self, keyword: str, rule: dict = None, request_overrides: dict = None):
        # init
        rule, request_overrides = rule or {}, request_overrides or {}
        # search rules
        default_rule = {'s': keyword, 'type': 1, 'limit': 10, 'offset': 0}
        default_rule.update(rule)
        # construct search urls based on search rules
        base_url = 'https://music.163.com/api/cloudsearch/pc'
        search_urls, page_size, count = [], self.search_size_per_page, 0
        while self.search_size_per_source > count:
            page_rule = copy.deepcopy(default_rule)
            page_rule['limit'] = page_size
            page_rule['offset'] = int(count // page_size) * page_size
            search_urls.append({'url': base_url, 'data': page_rule})
            count += page_size
        # return
        return search_urls
    '''_search'''
    @usesearchheaderscookies
    def _search(self, keyword: str = '', search_url: dict = {}, request_overrides: dict = None, song_infos: list = [], progress: Progress = None, progress_id: int = 0):
        # init
        request_overrides = request_overrides or {}
        search_meta = copy.deepcopy(search_url)
        search_url = search_meta.pop('url')
        # successful
        try:
            # --search results
            resp = self.post(search_url, **search_meta, **request_overrides)
            resp.raise_for_status()
            search_results = resp2json(resp)['result']['songs']
            for search_result in search_results:
                # --download results
                if not isinstance(search_result, dict) or ('id' not in search_result):
                    continue
                song_info = SongInfo(source=self.source)
                # ----try _parsewithcggapi first
                try:
                    song_info_cgg, quality_cgg = self._parsewithcggapi(search_result, request_overrides)
                except:
                    song_info_cgg, quality_cgg = SongInfo(source=self.source), "standard"
                # ----general parse with official API
                qualties = ["jymaster", "jyeffect", "sky", "hires", "lossless", "exhigh", "standard"]
                for quality_idx, quality in enumerate(qualties):
                    if quality_idx >= qualties.index(quality_cgg) and song_info_cgg.with_valid_download_url: song_info = song_info_cgg; break
                    header = {"os": "pc", "appver": "", "osver": "", "deviceId": "pyncm!"}
                    header["requestId"] = str(random.randrange(20000000, 30000000))
                    params = {'ids': [search_result['id']], 'level': quality, 'encodeType': 'flac', 'header': json.dumps(header)}
                    if quality == 'sky': params['immerseType'] = 'c51'
                    params = EapiCryptoUtils.encryptparams(url='https://interface3.music.163.com/eapi/song/enhance/player/url/v1', payload=params)
                    try:
                        resp = self.post('https://interface3.music.163.com/eapi/song/enhance/player/url/v1', data={"params": params}, **request_overrides)
                        resp.raise_for_status()
                        download_result: dict = resp2json(resp)
                    except:
                        continue
                    if (download_result.get('code') not in [200, '200']) or ('data' not in download_result) or (not download_result['data']) or \
                       (not isinstance(download_result['data'], list)) or (not isinstance(download_result['data'][0], dict)):
                        continue
                    download_url: str = download_result['data'][0].get('url', '')
                    if not download_url: continue
                    song_info = SongInfo(
                        source=self.source, download_url=download_url, download_url_status=self.audio_link_tester.test(download_url, request_overrides),
                        ext=download_url.split('.')[-1].split('?')[0], raw_data={'search': search_result, 'download': download_result},
                    )
                    song_info.download_url_status['probe_status'] = self.audio_link_tester.probe(song_info.download_url, request_overrides)
                    ext, file_size = song_info.download_url_status['probe_status']['ext'], song_info.download_url_status['probe_status']['file_size']
                    if file_size and file_size != 'NULL': song_info.file_size = file_size
                    if not song_info.file_size: song_info.file_size = 'NULL'
                    if ext and ext != 'NULL': song_info.ext = ext
                    if song_info.with_valid_download_url: break
                if not song_info.with_valid_download_url: continue
                # ----parse more information
                song_info.update(dict(
                    duration=seconds2hms(search_result.get('dt', 0) / 1000 if isinstance(search_result.get('dt', 0), (int, float)) else 0),
                    song_name=legalizestring(search_result.get('name', 'NULL'), replace_null_string='NULL'), 
                    singers=legalizestring(', '.join([singer.get('name', 'NULL') for singer in search_result.get('ar', [])]), replace_null_string='NULL'), 
                    album=legalizestring(safeextractfromdict(search_result, ['al', 'name'], 'NULL'), replace_null_string='NULL'),
                    identifier=search_result['id'],
                ))
                # --lyric results
                data = {'id': search_result['id'], 'cp': 'false', 'tv': '0', 'lv': '0', 'rv': '0', 'kv': '0', 'yv': '0', 'ytv': '0', 'yrv': '0'}
                try:
                    resp = self.post('https://interface3.music.163.com/api/song/lyric', data=data, **request_overrides)
                    resp.raise_for_status()
                    lyric_result: dict = resp2json(resp)
                    lyric = lyric_result.get('lrc', {}).get('lyric', 'NULL') or lyric_result.get('tlyric', {}).get('lyric', 'NULL')
                except:
                    lyric_result, lyric = dict(), 'NULL'
                song_info.raw_data['lyric'] = lyric_result
                song_info.lyric = lyric
                # --append to song_infos
                song_infos.append(song_info)
                # --judgement for search_size
                if self.strict_limit_search_size_per_page and len(song_infos) >= self.search_size_per_page: break
            # --update progress
            progress.update(progress_id, description=f"{self.source}.search >>> {search_url} (Success)")
        # failure
        except Exception as err:
            progress.update(progress_id, description=f"{self.source}.search >>> {search_url} (Error: {err})")
        # return
        return song_infos