'''
Function:
    Implementation of XimalayaMusicClient: https://www.ximalaya.com/
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
import re
import time
import copy
import base64
import binascii
import json_repair
from Crypto.Cipher import AES
from .base import BaseMusicClient
from urllib.parse import urlencode
from rich.progress import Progress
from ..utils import byte2mb, resp2json, seconds2hms, legalizestring, safeextractfromdict, usesearchheaderscookies, SongInfo


'''XimalayaMusicClient'''
class XimalayaMusicClient(BaseMusicClient):
    source = 'XimalayaMusicClient'
    def __init__(self, **kwargs):
        super(XimalayaMusicClient, self).__init__(**kwargs)
        self.default_search_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://api-v1.cenguigui.cn/",
            "Connection": "keep-alive",
        }
        self.default_download_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        }
        self.default_headers = self.default_search_headers
        self._initsession()
    '''_decrypturl'''
    def _decrypturl(self, ciphertext: str):
        if not ciphertext: return ciphertext
        key = binascii.unhexlify("aaad3e4fd540b0f79dca95606e72bf93")
        ciphertext = base64.urlsafe_b64decode(ciphertext + "=" * (4 - len(ciphertext) % 4))
        cipher = AES.new(key, AES.MODE_ECB)
        plaintext = cipher.decrypt(ciphertext)
        plaintext = re.sub(r"[^\x20-\x7E]", "", plaintext.decode("utf-8"))
        return plaintext
    '''_constructsearchurls'''
    def _constructsearchurls(self, keyword: str, rule: dict = None, request_overrides: dict = None):
        # init
        rule, request_overrides = rule or {}, request_overrides or {}
        # search rules
        default_rule = {'msg': keyword, 'n': '', 'num': self.search_size_per_source, 'type': 'json'}
        default_rule.update(rule)
        # construct search urls based on search rules
        base_url = 'https://api-v1.cenguigui.cn/api/music/dg_ximalayamusic.php?'
        page_rule = copy.deepcopy(default_rule)
        page_rule['num'] = self.search_size_per_source
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
            search_results = resp2json(resp)['data']
            for search_result in search_results:
                # --download results
                if (not isinstance(search_result, dict)) or 'trackId' not in search_result:
                    continue
                song_info = SongInfo(source=self.source)
                # ----try http://mobile.ximalaya.com/v1/track/ca/playpage/{trackId} first
                try:
                    resp = self.get(f'http://mobile.ximalaya.com/v1/track/ca/playpage/{search_result["trackId"]}', **request_overrides)
                    resp.raise_for_status()
                    download_result: dict = json_repair.loads(resp.text)
                    track_info = safeextractfromdict(download_result, ['trackInfo'], {})
                    qualities = [
                        ('playHqSize', 'playPathHq'), ('playPathAacv164Size', 'playPathAacv164'), ('downloadAacSize', 'downloadAacUrl'), ('playUrl64Size', 'playUrl64'), 
                        ('playUrl32Size', 'playUrl32'), ('downloadSize', 'downloadUrl'), ('playPathAacv224Size', 'playPathAacv224'),
                    ]
                    for quality in qualities:
                        song_info = SongInfo(source=self.source)
                        file_size, download_url = track_info.get(quality[0], 0), track_info.get(quality[1], '')
                        if not download_url: continue
                        ext = download_url.split('.')[-1].split('?')[0]
                        download_url_status = self.audio_link_tester.test(download_url, request_overrides)
                        song_info.update(dict(
                            download_url=download_url, download_url_status=download_url_status, ext=ext, file_size_bytes=file_size, file_size=byte2mb(file_size),
                            raw_data={'search': search_result, 'download': download_result}, duration_s=track_info.get('duration', 0), duration=seconds2hms(track_info.get('duration', 0)),
                        ))
                        if song_info.with_valid_download_url: break
                except:
                    pass
                # ----try https://www.ximalaya.com/mobile-playpage/track/v3/baseInfo/ second
                if not song_info.with_valid_download_url:
                    params = {"device": "web", "trackId": search_result["trackId"], "trackQualityLevel": 2}
                    try:
                        resp = self.get(f"https://www.ximalaya.com/mobile-playpage/track/v3/baseInfo/{int(time.time() * 1000)}", params=params, **request_overrides)
                        resp.raise_for_status()
                        download_result = resp2json(resp)
                        track_info = safeextractfromdict(download_result, ['trackInfo'], {})
                        for encrypted_url in sorted(safeextractfromdict(track_info, ['playUrlList'], []), key=lambda x: int(x['fileSize']), reverse=True):
                            song_info = SongInfo(source=self.source)
                            download_url = self._decrypturl(encrypted_url.get('url', ''))
                            if not download_url: continue
                            ext = download_url.split('.')[-1].split('?')[0]
                            download_url_status = self.audio_link_tester.test(download_url, request_overrides)
                            song_info.update(dict(
                                download_url=download_url, download_url_status=download_url_status, ext=ext, duration=seconds2hms(track_info.get('duration', 0)),
                                raw_data={'search': search_result, 'download': download_result}, duration_s=track_info.get('duration', 0), 
                            ))
                            if song_info.with_valid_download_url: break
                    except:
                        pass
                # ----try https://api-v1.cenguigui.cn/api/music/dg_ximalayamusic.php finally
                if (not song_info.with_valid_download_url) and ('n' in search_result):
                    song_info = SongInfo(source=self.source)
                    params = {'msg': keyword, 'n': search_result['n'], 'num': self.search_size_per_source, 'type': 'json'}
                    try:
                        resp = self.get('https://api-v1.cenguigui.cn/api/music/dg_ximalayamusic.php', params=params, **request_overrides)
                        download_result = resp2json(resp)
                        download_url = download_result.get('url', '')
                        if not download_url: continue
                        ext = download_url.split('.')[-1].split('?')[0]
                        download_url_status = self.audio_link_tester.test(download_url, request_overrides)
                        song_info.update(dict(
                            download_url=download_url, download_url_status=download_url_status, raw_data={'search': search_result, 'download': download_result},
                            duration='-:-:-', ext=ext,
                        ))
                    except:
                        continue
                # ----parse more infos
                if not song_info.with_valid_download_url: continue
                song_info.download_url_status['probe_status'] = self.audio_link_tester.probe(song_info.download_url, request_overrides)
                ext, file_size = song_info.download_url_status['probe_status']['ext'], song_info.download_url_status['probe_status']['file_size']
                if file_size and file_size != 'NULL': song_info.file_size = file_size
                if not song_info.file_size: song_info.file_size = 'NULL'
                if ext and ext != 'NULL': song_info.ext = ext
                lyric_result, lyric = dict(), 'NULL'
                song_info.raw_data['lyric'] = lyric_result
                song_info.update(dict(
                    lyric=lyric, song_name=legalizestring(search_result.get('title', 'NULL'), replace_null_string='NULL'), 
                    singers=legalizestring(search_result.get('Nickname', 'NULL'), replace_null_string='NULL'), 
                    album=legalizestring(search_result.get('album_title', 'NULL'), replace_null_string='NULL'),
                    identifier=search_result['trackId'],
                ))
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