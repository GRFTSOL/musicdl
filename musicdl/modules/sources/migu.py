'''
Function:
    Implementation of MiguMusicClient: https://music.migu.cn/v5/#/musicLibrary
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
import copy
import requests
from .base import BaseMusicClient
from rich.progress import Progress
from urllib.parse import urlencode, urlparse, parse_qs, quote
from ..utils import byte2mb, resp2json, seconds2hms, legalizestring, safeextractfromdict, usesearchheaderscookies, SongInfo


'''MiguMusicClient'''
class MiguMusicClient(BaseMusicClient):
    source = 'MiguMusicClient'
    def __init__(self, **kwargs):
        super(MiguMusicClient, self).__init__(**kwargs)
        self.default_search_headers = {
            "accept": "application/json, text/plain, */*", "accept-encoding": "gzip, deflate, br, zstd", "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "activityid": "v4_zt_2022_music", "appid": "ce", "channel": "014X031", "connection": "keep-alive", "deviceid": "E60C6B2F-7F11-4362-9FCE-6F1CC86E0F18",
            "host": "c.musicapp.migu.cn", "hwid": "", "imei": "", "h5page": "", "imsi": "", "location-info": "", "mgm-user-agent": "", "oaid": "", "uid": "",
            "location-data": "", "logid": "h5page[1808]", "mgm-network-operators": "02", "mgm-network-standard": "03", "mgm-network-type": "03", "origin": "https://y.migu.cn",
            "recommendstatus": "1", "referer": "https://y.migu.cn/app/v4/zt/2022/music/index.html", "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": "\"Windows\"", "sec-fetch-dest": "empty", "sec-fetch-mode": "cors", "sec-fetch-site": "same-site",
            "subchannel": "014X031", "test": "00", "ua": "Android_migu", "version": "6.8.8",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        }
        self.default_download_headers = {
            "accept": "*/*", "accept-encoding": "identity;q=1, *;q=0", "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7", "connection": "keep-alive",
            "host": "freetyst.nf.migu.cn", "range": "bytes=0-", "referer": "https://y.migu.cn/app/v4/zt/2022/music/index.html",
            "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"", "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"", "sec-fetch-dest": "audio", "sec-fetch-mode": "no-cors", "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        }
        self.default_headers = self.default_search_headers
        self._initsession()
    '''_limitedparsetries'''
    def _limitedparsetries(self, keyword: str, search_result: dict, request_overrides: dict = None, n: int = 1):
        # init
        request_overrides, song_id = request_overrides or {}, str(search_result['copyrightId'])
        # parse
        limited_apis = [
            f'https://api.jkyai.top/API/mgyyjs.php?gm={quote(keyword)}&n={n}&num=20&type=json',
            f'https://api.xcvts.cn/api/music/migu?gm={quote(keyword)}&n={n}&num=20&type=json',
        ]
        for url in limited_apis:
            try:
                resp = requests.get(url, timeout=10, **request_overrides)
                resp.raise_for_status()
                download_result = resp2json(resp=resp)
                copyright_id = str(urlparse(download_result['link']).path.strip('/').split('/')[-1])
                song_info = SongInfo(
                    source=self.source, download_url=download_result['music_url'], download_url_status=self.audio_link_tester.test(download_result['music_url'], request_overrides),
                    ext=download_result['music_url'].split('?')[0].split('.')[-1], raw_data={'search': search_result, 'download': download_result}, file_size='NULL',
                )
                song_info.download_url_status['probe_status'] = self.audio_link_tester.probe(song_info.download_url, request_overrides)
                song_info.file_size = song_info.download_url_status['probe_status']['file_size']
                if copyright_id == song_id and song_info.with_valid_download_url: return song_info
            except:
                continue
        return SongInfo(source=self.source)
    '''_parsewithcggapi'''
    def _parsewithcggapi(self, keyword: str, search_result: dict, request_overrides: dict = None, n: int = 1):
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
        if not song_info.with_valid_download_url:
            download_url = safeextractfromdict(download_result, ['data', 'url'], '')
            song_info = SongInfo(
                source=self.source, download_url=download_url, download_url_status=self.audio_link_tester.test(download_url, request_overrides),
                ext=download_url.split('?')[0].split('.')[-1], raw_data={'search': search_result, 'download': download_result},
            )
        # return
        return song_info
    '''_constructsearchurls'''
    def _constructsearchurls(self, keyword: str, rule: dict = None, request_overrides: dict = None):
        # init
        rule, request_overrides = rule or {}, request_overrides or {}
        # search rules
        default_rule = {"text": keyword, 'pageNo': 1, 'pageSize': 20, 'isCopyright': 1, 'sort': 1, 'searchSwitch': {"song":1,"album":0,"singer":0,"tagSong":1,"mvSong":0,"bestShow":1}}
        default_rule.update(rule)
        # construct search urls based on search rules
        base_url = 'https://c.musicapp.migu.cn/v1.0/content/search_all.do?'
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
        page_no = str(parse_qs(urlparse(search_url).query, keep_blank_values=True).get('pageNo', ['1'])[0])
        # _safefetchfilesize
        def _safefetchfilesize(meta: dict):
            file_size = meta.get('size') or meta.get('iosSize') or meta.get('androidSize') or 0
            if byte2mb(file_size) == 'NULL': file_size = 0
            return file_size
        # successful
        try:
            # --search results
            resp = self.get(search_url, **request_overrides)
            resp.raise_for_status()
            search_results = resp2json(resp)['songResultData']['result']
            for n, search_result in enumerate(search_results):
                # --download results
                if not isinstance(search_result, dict) or ('copyrightId' not in search_result) or ('contentId' not in search_result):
                    continue
                song_info = SongInfo(source=self.source)
                # ----try thirdpart apis first
                candidated_thirdpart_apis = [self._limitedparsetries, self._parsewithcggapi] if page_no == '1' else [self._parsewithcggapi]
                for imp_func in candidated_thirdpart_apis:
                    try:
                        song_info_flac = imp_func(keyword, search_result, request_overrides, n=n+1)
                        if song_info_flac.with_valid_download_url: break
                    except:
                        song_info_flac = SongInfo(source=self.source)
                # ----general parse with official API
                for rate in sorted(search_result.get('rateFormats', []) + search_result.get('newRateFormats', []), key=lambda x: int(_safefetchfilesize(x)), reverse=True):
                    if not isinstance(rate, dict): continue
                    if byte2mb(_safefetchfilesize(rate)) == 'NULL' or (not rate.get('formatType', '')) or (not rate.get('resourceType', '')): continue
                    ext = {'LQ': 'mp3', 'PQ': 'mp3', 'HQ': 'mp3', 'SQ': 'flac', 'ZQ24': 'flac', 'ZQ': 'flac'}.get(rate['formatType'], 'mp3')
                    url = (
                        f"https://c.musicapp.migu.cn/MIGUM3.0/strategy/listen-url/v2.4?resourceType={rate['resourceType']}&netType=01&scene="
                        f"&toneFlag={rate['formatType']}&contentId={search_result['contentId']}&copyrightId={search_result['copyrightId']}"
                        f"&lowerQualityContentId={search_result['contentId']}"
                    )
                    try:
                        resp = self.get(url, **request_overrides)
                        resp.raise_for_status()
                        download_result = resp2json(resp=resp)
                    except:
                        continue
                    download_url = safeextractfromdict(download_result, ['data', 'url'], "") or \
                                   f"https://app.pd.nf.migu.cn/MIGUM3.0/v1.0/content/sub/listenSong.do?channel=mx&copyrightId={search_result['copyrightId']}&contentId={search_result['contentId']}&toneFlag={rate['formatType']}&resourceType={rate['resourceType']}&userId=15548614588710179085069&netType=00"
                    if not download_url: continue
                    song_info = SongInfo(
                        source=self.source, download_url=download_url, download_url_status=self.audio_link_tester.test(download_url, request_overrides),
                        ext=ext, raw_data={'search': search_result, 'download': download_result}, duration_s=safeextractfromdict(download_result, ['data', 'song', 'duration'], 0),
                        duration=seconds2hms(safeextractfromdict(download_result, ['data', 'song', 'duration'], 0))
                    )
                    song_info_flac.duration_s = song_info.duration_s
                    song_info_flac.duration = song_info.duration
                    if not song_info.with_valid_download_url: continue
                    song_info.download_url_status['probe_status'] = self.audio_link_tester.probe(song_info.download_url, request_overrides)
                    ext, file_size = song_info.download_url_status['probe_status']['ext'], song_info.download_url_status['probe_status']['file_size']
                    if file_size and file_size != 'NULL': song_info.file_size = file_size
                    if not song_info.file_size: song_info.file_size = 'NULL'
                    if ext and ext != 'NULL': song_info.ext = ext
                    if song_info_flac.with_valid_download_url and song_info_flac.file_size != 'NULL':
                        file_size_cgg = float(song_info_flac.file_size.removesuffix('MB').strip())
                        file_size_official = float(song_info.file_size.removesuffix('MB').strip()) if song_info.file_size != 'NULL' else 0
                        if file_size_cgg + 1 >= file_size_official: song_info = song_info_flac; break
                    if song_info.with_valid_download_url: break
                if not song_info.with_valid_download_url: song_info = song_info_flac
                if not song_info.with_valid_download_url: continue
                # ----parse more information
                song_info.update(dict(
                    song_name=legalizestring(search_result.get('name', 'NULL'), replace_null_string='NULL'), 
                    singers=legalizestring(', '.join([singer.get('name', 'NULL') for singer in search_result.get('singers', [])]), replace_null_string='NULL'), 
                    album=legalizestring(', '.join([singer.get('name', 'NULL') for singer in search_result.get('albums', [])]), replace_null_string='NULL'),
                    identifier=f"{search_result['contentId']}"
                ))
                # --lyric results, TODO: fix the bugs in lyric fetch
                try:
                    lyric_url = safeextractfromdict(search_result, ['lyricUrl'], '') or safeextractfromdict(search_result, ['trcUrl'], '')
                    lyric_url = lyric_url.replace('http://', 'https://')
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
                        "Accept": "*/*", "Accept-Encoding": "identity", "Referer": "https://y.migu.cn/",
                    }
                    resp = self.get(lyric_url, headers=headers, allow_redirects=True, **request_overrides)
                    resp.raise_for_status()
                    resp.encoding = 'utf-8'
                    lyric, lyric_result = resp.text, {'lyric': resp.text}
                except:
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