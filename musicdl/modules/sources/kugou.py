'''
Function:
    Implementation of KugouMusicClient: http://www.kugou.com/
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
import copy
import base64
from .base import BaseMusicClient
from urllib.parse import urlencode
from rich.progress import Progress
from ..utils import legalizestring, byte2mb, resp2json, seconds2hms, usesearchheaderscookies, safeextractfromdict, SongInfo


'''KugouMusicClient'''
class KugouMusicClient(BaseMusicClient):
    source = 'KugouMusicClient'
    def __init__(self, **kwargs):
        super(KugouMusicClient, self).__init__(**kwargs)
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
        # search rules
        default_rule = {'keyword': keyword, 'page': 1, 'pagesize': 10}
        default_rule.update(rule)
        # construct search urls based on search rules
        base_url = 'http://songsearch.kugou.com/song_search_v2?'
        search_urls, page_size, count = [], self.search_size_per_page, 0
        while self.search_size_per_source > count:
            page_rule = copy.deepcopy(default_rule)
            page_rule['pagesize'] = page_size
            page_rule['page'] = int(count // page_size) + 1
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
            search_results = resp2json(resp)['data']['lists']
            for search_result in search_results:
                # --download results
                if not isinstance(search_result, dict) or ('FileHash' not in search_result):
                    continue
                song_info = SongInfo(source=self.source)
                try:
                    resp = self.get(f"http://m.kugou.com/app/i/getSongInfo.php?cmd=playInfo&hash={search_result['FileHash']}", **request_overrides)
                    resp.raise_for_status()
                    download_result_default: dict = resp2json(resp)
                except:
                    continue
                better_hashes = [
                    safeextractfromdict(download_result_default, ['extra', 'highhash'], ""), safeextractfromdict(download_result_default, ['extra', 'sqhash'], ""),
                    safeextractfromdict(download_result_default, ['extra', '320hash'], ""), safeextractfromdict(download_result_default, ['extra', '128hash'], ""),
                ]
                for better_hash in better_hashes:
                    if not better_hash: continue
                    if better_hash == search_result['FileHash']:
                        download_result = download_result_default
                        download_url = download_result.get('url') or download_result.get('backup_url')
                        if not download_url: continue
                        if isinstance(download_url, list): download_url = download_url[0]
                        song_info = SongInfo(
                            source=self.source, download_url=download_url, download_url_status=self.audio_link_tester.test(download_url, request_overrides),
                        )
                        if song_info.with_valid_download_url: break
                    else:
                        try:
                            resp = self.get(f"http://m.kugou.com/app/i/getSongInfo.php?cmd=playInfo&hash={better_hash}", **request_overrides)
                            resp.raise_for_status()
                            download_result: dict = resp2json(resp)
                            download_url = download_result.get('url') or download_result.get('backup_url')
                            if not download_url: continue
                            if isinstance(download_url, list): download_url = download_url[0]
                            song_info = SongInfo(
                                source=self.source, download_url=download_url, download_url_status=self.audio_link_tester.test(download_url, request_overrides),
                            )
                            if song_info.with_valid_download_url: break
                        except:
                            continue
                if not song_info.with_valid_download_url: continue
                song_info.update(dict(
                    file_size_bytes=download_result.get('fileSize', 0), file_size=byte2mb(download_result.get('fileSize', 0)),
                    duration_s=download_result.get('timeLength', 0), duration=seconds2hms(download_result.get('timeLength', 0)),
                    raw_data={'search': search_result, 'download': download_result}, ext=download_result.get('extName', 'mp3'),
                    song_name=legalizestring(search_result.get('SongName', 'NULL'), replace_null_string='NULL'), 
                    singers=legalizestring(search_result.get('SingerName', 'NULL'), replace_null_string='NULL'), 
                    album=legalizestring(search_result.get('AlbumName', 'NULL'), replace_null_string='NULL'),
                    identifier=better_hash,
                ))
                if song_info.song_name == 'NULL': song_info.song_name = legalizestring(search_result.get('FileName', 'NULL'), replace_null_string='NULL')
                if song_info.song_name == 'NULL': song_info.song_name = legalizestring(search_result.get('OriSongName', 'NULL'), replace_null_string='NULL')
                # --lyric results
                params = {'keyword': search_result.get('FileName', ''), 'duration': search_result.get('Duration', '99999'), 'hash': better_hash}
                try:
                    resp = self.get('http://lyrics.kugou.com/search', params=params, **request_overrides)
                    resp.raise_for_status()
                    lyric_result = resp2json(resp=resp)
                    id = lyric_result['candidates'][0]['id']
                    accesskey = lyric_result['candidates'][0]['accesskey']
                    resp = self.get(f'http://lyrics.kugou.com/download?ver=1&client=pc&id={id}&accesskey={accesskey}&fmt=lrc&charset=utf8', **request_overrides)
                    resp.raise_for_status()
                    lyric_result['lyrics.kugou.com/download'] = resp2json(resp=resp)
                    lyric = lyric_result['lyrics.kugou.com/download']['content']
                    lyric = base64.b64decode(lyric).decode('utf-8')
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