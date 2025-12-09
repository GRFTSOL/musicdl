'''
Function:
    Implementation of KuwoMusicClient: http://www.kuwo.cn/
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
import copy
import uuid
from .base import BaseMusicClient
from urllib.parse import urlencode
from rich.progress import Progress
from ..utils import legalizestring, resp2json, seconds2hms, usesearchheaderscookies, SongInfo


'''KuwoMusicClient'''
class KuwoMusicClient(BaseMusicClient):
    source = 'KuwoMusicClient'
    def __init__(self, **kwargs):
        super(KuwoMusicClient, self).__init__(**kwargs)
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
        default_rule = {
            "vipver": "1", "client": "kt", "ft": "music", "cluster": "0", "strategy": "2012", "encoding": "utf8",
            "rformat": "json", "mobi": "1", "issubtitle": "1", "show_copyright_off": "1", "pn": "0", "rn": "10",
            "all": keyword,
        }
        default_rule.update(rule)
        # construct search urls based on search rules
        base_url = 'http://www.kuwo.cn/search/searchMusicBykeyWord?'
        search_urls, page_size, count = [], self.search_size_per_page, 0
        while self.search_size_per_source > count:
            page_rule = copy.deepcopy(default_rule)
            page_rule['rn'] = page_size
            page_rule['pn'] = str(int(count // page_size))
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
            search_results = resp2json(resp)['abslist']
            for search_result in search_results:
                # --download results
                if not isinstance(search_result, dict) or ('MUSICRID' not in search_result):
                    continue
                song_info = SongInfo(source=self.source)
                brs = ['4000kflac', '2000kflac', 'flac', '320kmp3', '192kmp3', '128kmp3']
                # ----try "https://mobi.kuwo.cn/mobi.s" first
                for br in brs:
                    try:
                        resp = self.get(f"https://mobi.kuwo.cn/mobi.s?f=web&source=kwplayercar_ar_6.0.0.9_B_jiakong_vh.apk&from=PC&type=convert_url_with_sign&br={br}&rid={search_result['MUSICRID'].removeprefix('MUSIC_')}&&user=C_APK_guanwang_12609069939969033731", **request_overrides)
                        resp.raise_for_status()
                        download_result = resp2json(resp=resp)
                        download_url = download_result['data']['url']
                        song_info = SongInfo(
                            source=self.source, download_url=download_url, download_url_status=self.audio_link_tester.test(download_url, request_overrides),
                            ext=download_result['data']['format'], duration_s=download_result['data']['duration'], duration=seconds2hms(download_result['data']['duration']),
                            raw_data={'search': search_result, 'download': download_result},
                        )
                        if song_info.with_valid_download_url: break
                    except:
                        continue
                # ----try "https://www.kuwo.cn/api/v1/www/music/playUrl", second
                if not song_info.with_valid_download_url:
                    headers = {
                        "Cookie": (
                            "Hm_lvt_cdb524f42f0ce19b169a8071123a4797=1747998937; HMACCOUNT=3E88140C4BD6BF25; _ga=GA1.2.2122710619.1747998937; _gid=GA1.2.1827944406.1747998937; "
                            "gtoken=RNbrzHWRp6DY; gid=d55a4884-42aa-4733-98eb-e7aaffc6122e; JSESSIONID=us1icx6617iy1k1ksiuykje71; Hm_lpvt_cdb524f42f0ce19b169a8071123a4797=1748000521; "
                            "_gat=1; _ga_ETPBRPM9ML=GS2.2.s1747998937$o1$g1$t1748000535$j45$l0$h0; Hm_Iuvt_cdb524f42f23cer9b268564v7y735ewrq2324=jbikFazGJzBjt2bhSJGMxGfkM5zNYcis"
                        ),
                        "secret": "4932e2c95746126c945fe2fb3f88d3455b85b69a4fbdfa6c44b501d7dfe50cff04eb9a8e",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0",
                    }
                    for br in brs:
                        params = {'mid': search_result['MUSICRID'].removeprefix('MUSIC_'), 'type': 'music', 'httpsStatus': '1', 'br': br}
                        try:
                            resp = self.get('https://www.kuwo.cn/api/v1/www/music/playUrl', params=params, headers=headers, **request_overrides)
                            resp.raise_for_status()
                            download_result = resp2json(resp=resp)
                            download_url = download_result['data']['url']
                            ext = download_url.split('.')[-1].split('?')[0] or 'mp3'
                            song_info = SongInfo(
                                source=self.source, download_url=download_url, download_url_status=self.audio_link_tester.test(download_url, request_overrides),
                                ext=ext, duration_s=search_result.get('DURATION', 0), duration=seconds2hms(search_result.get('DURATION', 0)),
                                raw_data={'search': search_result, 'download': download_result},
                            )
                            if song_info.with_valid_download_url: break
                        except:
                            continue
                # ----try "http://antiserver.kuwo.cn/anti.s" finally (br only up to 320kmp3)
                if not song_info.with_valid_download_url:
                    params = {'format': 'aac|mp3', 'rid': search_result['MUSICRID'].removeprefix('MUSIC_'), 'type': 'convert_url3', 'response': 'url', 'br': '320kmp3'}
                    try:
                        resp = self.get('http://antiserver.kuwo.cn/anti.s', params=params, **request_overrides)
                        resp.raise_for_status()
                        download_result = resp2json(resp=resp)
                        download_url = download_result['url']
                        ext = download_url.split('.')[-1].split('?')[0] or 'mp3'
                        song_info = SongInfo(
                            source=self.source, download_url=download_url, download_url_status=self.audio_link_tester.test(download_url, request_overrides),
                            ext=ext, duration_s=search_result.get('DURATION', 0), duration=seconds2hms(search_result.get('DURATION', 0)),
                            raw_data={'search': search_result, 'download': download_result},
                        )
                    except:
                        continue
                if not song_info.with_valid_download_url: continue
                # ----parse other information
                song_info.update(dict(
                    song_name=legalizestring(search_result.get('SONGNAME', 'NULL'), replace_null_string='NULL'), 
                    singers=legalizestring(search_result.get('ARTIST', 'NULL'), replace_null_string='NULL'), 
                    album=legalizestring(search_result.get('ALBUM', 'NULL'), replace_null_string='NULL'),
                    identifier=search_result['MUSICRID'],
                ))
                song_info.download_url_status['prob_status'] = self.audio_link_tester.probe(song_info.download_url, request_overrides)
                ext, file_size = song_info.download_url_status['prob_status']['ext'], song_info.download_url_status['prob_status']['file_size']
                if file_size and file_size != 'NULL': song_info.file_size = file_size
                if not song_info.file_size: song_info.file_size = 'NULL'
                if ext and ext != 'NULL': song_info.ext = ext
                # --lyric results
                params = {'musicId': search_result['MUSICRID'].removeprefix('MUSIC_'), 'httpsStatus': '1'}
                try:
                    resp = self.get('http://m.kuwo.cn/newh5/singles/songinfoandlrc', params=params, **request_overrides)
                    resp.raise_for_status()
                    lyric_result: dict = resp2json(resp)
                    lyric = lyric_result.get('data', {}).get('lrclist', []) or 'NULL'
                except:
                    lyric_result, lyric = {}, 'NULL'
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