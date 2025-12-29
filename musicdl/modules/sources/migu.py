'''
Function:
    Implementation of MiguMusicClient: https://music.migu.cn/v5/#/musicLibrary
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
import copy
from .base import BaseMusicClient
from rich.progress import Progress
from urllib.parse import urlencode
from ..utils import byte2mb, resp2json, seconds2hms, legalizestring, safeextractfromdict, usesearchheaderscookies, SongInfo


'''MiguMusicClient'''
class MiguMusicClient(BaseMusicClient):
    source = 'MiguMusicClient'
    def __init__(self, **kwargs):
        super(MiguMusicClient, self).__init__(**kwargs)
        self.default_search_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        }
        self.default_download_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        }
        self.default_headers = self.default_search_headers
        self._initsession()
    '''_parsewithcggapi'''
    def _parsewithcggapi(self, search_result: dict, request_overrides: dict = None):
        # init
        request_overrides, song_id = request_overrides or {}, search_result['contentId']
        # _safefetchfilesize
        def _safefetchfilesize(meta: dict):
            if not isinstance(meta, dict): return 0
            file_size = str(meta.get('size', '0.00 MB'))
            file_size = file_size.removesuffix('MB').strip()
            try: return float(file_size)
            except: return 0
        # parse
        try:
            for prefix in ['api-v1', 'api']:
                try:
                    resp = self.get(url=f'https://{prefix}.cenguigui.cn/api/mg_music/api.php?id={song_id}', timeout=10, **request_overrides)
                    resp.raise_for_status()
                    break
                except:
                    continue
            download_result = resp2json(resp=resp)
        except:
            return SongInfo(source=self.source)
        for rate in sorted(safeextractfromdict(download_result, ['data', 'level', 'quality'], []), key=lambda x: _safefetchfilesize(x), reverse=True):
            download_url = rate.get('url', '')
            if not download_url: continue
            song_info = SongInfo(
                source=self.source, download_url=download_url, download_url_status=self.audio_link_tester.test(download_url, request_overrides),
                ext=str(rate.get('format', 'flac')).lower(), raw_data={'search': search_result, 'download': download_result},
            )
            song_info.download_url_status['probe_status'] = self.audio_link_tester.probe(song_info.download_url, request_overrides)
            ext, file_size = song_info.download_url_status['probe_status']['ext'], song_info.download_url_status['probe_status']['file_size']
            if file_size and file_size != 'NULL': song_info.file_size = file_size
            if not song_info.file_size: song_info.file_size = 'NULL'
            if ext and ext != 'NULL': song_info.ext = ext
            if song_info.with_valid_download_url: break
        # return
        return song_info
    '''_constructsearchurls'''
    def _constructsearchurls(self, keyword: str, rule: dict = None, request_overrides: dict = None):
        # init
        rule, request_overrides = rule or {}, request_overrides or {}
        # search rules
        default_rule = {"text": keyword, 'pageNo': 1, 'pageSize': 10}
        default_rule.update(rule)
        # construct search urls based on search rules
        base_url = 'https://app.u.nf.migu.cn/pc/resource/song/item/search/v1.0?'
        search_urls, page_size, count = [], self.search_size_per_page, 0
        while self.search_size_per_source > count:
            page_rule = copy.deepcopy(default_rule)
            page_rule['pageSize'] = page_size
            page_rule['pageNo'] = int(count // page_size) + 1
            search_urls.append(base_url + urlencode(page_rule))
            count += page_size
        # return
        return search_urls
    '''_search'''
    @usesearchheaderscookies
    def _search(self, keyword: str = '', search_url: str = '', request_overrides: dict = None, song_infos: list = [], progress: Progress = None, progress_id: int = 0):
        # init
        request_overrides = request_overrides or {}
        # _safefetchfilesize
        def _safefetchfilesize(meta: dict):
            file_size = meta.get('asize') or meta.get('isize') or meta.get('size') or '0'
            if byte2mb(file_size) == 'NULL': file_size = '0'
            return file_size
        # user info
        uid = '15548614588710179085069'
        # successful
        try:
            # --search results
            resp = self.get(search_url, **request_overrides)
            resp.raise_for_status()
            search_results = resp2json(resp)
            for search_result in search_results:
                # --download results
                if not isinstance(search_result, dict) or ('copyrightId' not in search_result) or ('contentId' not in search_result):
                    continue
                song_info = SongInfo(source=self.source)
                # ----try _parsewithcggapi first
                try:
                    song_info_cgg = self._parsewithcggapi(search_result, request_overrides)
                except:
                    song_info_cgg = SongInfo(source=self.source)
                # ----general parse with official API
                for rate in sorted(search_result.get('audioFormats', []), key=lambda x: int(_safefetchfilesize(x)), reverse=True):
                    if not isinstance(rate, dict): continue
                    if byte2mb(_safefetchfilesize(rate)) == 'NULL' or (not rate.get('formatType', '')) or (not rate.get('resourceType', '')): continue
                    song_info.file_size = byte2mb(_safefetchfilesize(rate))
                    if song_info_cgg.with_valid_download_url and song_info_cgg.file_size != 'NULL':
                        file_size_cgg = float(song_info_cgg.file_size.removesuffix('MB').strip())
                        file_size_official = float(song_info.file_size.removesuffix('MB').strip()) if song_info.file_size != 'NULL' else 0
                        if file_size_cgg + 1 >= file_size_official: song_info = song_info_cgg; break
                    ext = {'PQ': 'mp3', 'HQ': 'mp3', 'SQ': 'flac', 'ZQ24': 'flac'}.get(rate['formatType'], 'NULL')
                    url = (
                        f"https://c.musicapp.migu.cn/MIGUM3.0/strategy/listen-url/v2.4?resourceType={rate['resourceType']}&netType=01&scene="
                        f"&toneFlag={rate['formatType']}&contentId={search_result['contentId']}&copyrightId={search_result['copyrightId']}"
                        f"&lowerQualityContentId={search_result['contentId']}"
                    )
                    headers = copy.deepcopy(self.default_headers)
                    headers['channel'] = '014000D'
                    try:
                        resp = self.get(url, headers=headers, **request_overrides)
                        resp.raise_for_status()
                        download_result = resp2json(resp=resp)
                    except:
                        continue
                    download_url = safeextractfromdict(download_result, ['data', 'url'], "") or \
                                   f"https://app.pd.nf.migu.cn/MIGUM3.0/v1.0/content/sub/listenSong.do?channel=mx&copyrightId={search_result['copyrightId']}&contentId={search_result['contentId']}&toneFlag={rate['formatType']}&resourceType={rate['resourceType']}&userId={uid}&netType=00"
                    song_info = SongInfo(
                        source=self.source, download_url=download_url, download_url_status=self.audio_link_tester.test(download_url, request_overrides),
                        ext=ext, raw_data={'search': search_result, 'download': download_result},
                    )
                    if not song_info.with_valid_download_url: continue
                    song_info.download_url_status['probe_status'] = self.audio_link_tester.probe(song_info.download_url, request_overrides)
                    ext, file_size = song_info.download_url_status['probe_status']['ext'], song_info.download_url_status['probe_status']['file_size']
                    if file_size and file_size != 'NULL': song_info.file_size = file_size
                    if not song_info.file_size: song_info.file_size = 'NULL'
                    if ext and ext != 'NULL': song_info.ext = ext
                    if song_info.with_valid_download_url: break
                if not song_info.with_valid_download_url: song_info = song_info_cgg
                if not song_info.with_valid_download_url: continue
                # ----parse more information
                song_info.update(dict(
                    duration_s=search_result.get('duration', 0), duration=seconds2hms(search_result.get('duration', 0)),
                    song_name=legalizestring(search_result.get('songName', 'NULL'), replace_null_string='NULL'), 
                    singers=legalizestring(', '.join([singer.get('name', 'NULL') for singer in search_result.get('singerList', [])]), replace_null_string='NULL'), 
                    album=legalizestring(search_result.get('album', 'NULL'), replace_null_string='NULL'),
                    identifier=f"{search_result['copyrightId']}_{search_result['contentId']}"
                ))
                # --lyric results
                lyric_url = safeextractfromdict(search_result, ['ext', 'lrcUrl'], '') or safeextractfromdict(search_result, ['ext', 'mrcUrl'], '') or \
                            safeextractfromdict(search_result, ['ext', 'trcUrl'], '')
                if lyric_url:
                    try:
                        resp = self.get(lyric_url, **request_overrides)
                        resp.encoding = 'utf-8'
                        lyric_result, lyric = {'lyric': resp.text}, resp.text
                    except:
                        lyric_result, lyric = {}, 'NULL'
                else:
                    lyric_result, lyric = {}, 'NULL'
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