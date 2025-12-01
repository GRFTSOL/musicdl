'''
Function:
    Implementation of AppleMusicClient: https://music.apple.com/{geo}/new
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
import re
import os
import copy
import shutil
from .base import BaseMusicClient
from urllib.parse import urlencode
from rich.progress import Progress
from ..utils.appleutils import AppleMusicClientUtils
from ..utils import touchdir, legalizestring, resp2json, isvalidresp, seconds2hms, usesearchheaderscookies, safeextractfromdict, usedownloadheaderscookies, AudioLinkTester, WhisperLRC


'''AppleMusicClient'''
class AppleMusicClient(BaseMusicClient):
    source = 'AppleMusicClient'
    def __init__(self, **kwargs):
        super(AppleMusicClient, self).__init__(**kwargs)
        # headers setting
        self.default_search_headers = {
            "authorization": f"Bearer {self._fetchtoken()}",
            "accept": "*/*",
            "accept-language": "en-US",
            "origin": "https://music.apple.com",
            "priority": "u=1, i",
            "referer": "https://music.apple.com",
            "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        }
        self.default_download_headers = copy.deepcopy(self.default_search_headers)
        self.default_headers = self.default_search_headers
        # account info (whether a VIP user)
        self.account_info = {}
        if not self.default_cookies or 'media-user-token' not in self.default_cookies: 
            self.logger_handle.warning(f'{self.source}.__init__ >>> "media-user-token" is not configured, so song downloads are restricted and only the preview portion of the track can be downloaded.')
        else:
            self.account_info = self._fetchaccountinfo()
        # init session
        self._initsession()
    '''_download'''
    @usedownloadheaderscookies
    def _download(self, song_info: dict, request_overrides: dict = None, downloaded_song_infos: list = [], progress: Progress = None, song_progress_id: int = 0):
        if isinstance(song_info['download_url'], str): return super()._download(song_info=song_info, request_overrides=request_overrides, downloaded_song_infos=downloaded_song_infos, progress=progress, song_progress_id=song_progress_id)
        request_overrides = request_overrides or {}
        try:
            touchdir(song_info['work_dir'])
            tmp_dir = os.path.join(self.work_dir.replace(' ', ''), self.source.replace(' ', ''), song_info['identifier'].replace(' ', '')) # replace space to avoid bugs
            touchdir(tmp_dir)
            download_item = song_info['download_url']
            save_path, same_name_file_idx = os.path.join(song_info['work_dir'], f"{song_info['song_name']}.{song_info['ext']}"), 1
            while os.path.exists(save_path):
                save_path = os.path.join(song_info['work_dir'], f"{song_info['song_name']}_{same_name_file_idx}.{song_info['ext']}")
                same_name_file_idx += 1
            download_item.final_path = save_path
            AppleMusicClientUtils.download(download_item, work_dir=tmp_dir)
            progress.update(song_progress_id, description=f"{self.source}.download >>> {song_info['song_name']} (Success)")
            downloaded_song_info = copy.deepcopy(song_info)
            downloaded_song_info['save_path'] = save_path
            downloaded_song_infos.append(downloaded_song_info)
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception as err:
            progress.update(song_progress_id, description=f"{self.source}.download >>> {song_info['song_name']} (Error: {err})")
        return downloaded_song_infos
    '''_fetchtoken'''
    def _fetchtoken(self, request_overrides: dict = None):
        request_overrides = request_overrides or {}
        resp = self.get('https://music.apple.com', **request_overrides)
        resp.raise_for_status()
        home_page = resp.text
        index_js_uri_match = re.search(r"/(assets/index-legacy[~-][^/\"]+\.js)", home_page)
        index_js_uri = index_js_uri_match.group(1)
        resp = self.get(f"https://music.apple.com/{index_js_uri}", **request_overrides)
        resp.raise_for_status()
        index_js_page = resp.text
        token_match = re.search('(?=eyJh)(.*?)(?=")', index_js_page)
        token = token_match.group(1)
        return token
    '''_fetchaccountinfo'''
    def _fetchaccountinfo(self, request_overrides: dict = None):
        if self.account_info or (not self.default_cookies or 'media-user-token' not in self.default_cookies): return self.account_info
        request_overrides = request_overrides or {}
        resp = self.get('https://amp-api.music.apple.com/v1/me/account?meta=subscription', **request_overrides)
        resp.raise_for_status()
        account_info = resp2json(resp=resp)
        self.account_info = account_info
        return self.account_info
    '''_constructsearchurls'''
    def _constructsearchurls(self, keyword: str, rule: dict = None, request_overrides: dict = None):
        # init
        rule, request_overrides = rule or {}, request_overrides or {}
        account_info = self._fetchaccountinfo(request_overrides=request_overrides)
        geo = safeextractfromdict(account_info, ['meta', 'subscription', 'storefront'], 'us')
        # search rules
        default_rule = {
            "groups": "song", "l": "en-US", "offset": "0", "term": keyword, "types": "activities,albums,apple-curators,artists,curators,editorial-items,music-movies,music-videos,playlists,record-labels,songs,stations,tv-episodes,uploaded-videos",
            "art[url]": "f", "extend": "artistUrl", "fields[albums]": "artistName,artistUrl,artwork,contentRating,editorialArtwork,editorialNotes,name,playParams,releaseDate,url,trackCount", "fields[artists]": "url,name,artwork",
            "format[resources]": "map", "include[editorial-items]": "contents", "include[songs]": "artists", "limit": "10", "omit[resource]": "autos", "platform": "web", "relate[albums]": "artists", "relate[editorial-items]": "contents",
            "relate[songs]": "albums", "types": "activities,albums,apple-curators,artists,curators,music-movies,music-videos,playlists,songs,stations,tv-episodes,uploaded-videos", "with": "lyrics,serverBubbles", 
        }
        default_rule.update(rule)
        geo = default_rule.pop('geo', geo)
        # construct search urls based on search rules
        base_url = f'https://amp-api-edge.music.apple.com/v1/catalog/{geo}/search?'
        search_urls, page_size, count = [], self.search_size_per_page, 0
        while self.search_size_per_source > count:
            page_rule = copy.deepcopy(default_rule)
            page_rule['limit'] = page_size
            page_rule['offset'] = str(int(count // page_size) * page_size)
            search_urls.append(base_url + urlencode(page_rule))
            count += page_size
        # return
        return search_urls
    '''_fetchlicenseexchange'''
    def _fetchlicenseexchange(self, track_id: str, track_uri: str, challenge: str, key_system: str = "com.widevine.alpha", request_overrides: dict = None):
        request_overrides = request_overrides or {}
        json_data = {"challenge": challenge, "key-system": key_system, "uri": track_uri, "adamId": track_id, "isLibrary": False, "user-initiated": True}
        resp = self.post("https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/acquireWebPlaybackLicense", json=json_data, **request_overrides)
        resp.raise_for_status()
        license_exchange = resp2json(resp)
        return license_exchange
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
            search_results: dict = resp2json(resp)['resources']['songs']
            for song_key, search_result in search_results.items():
                # --download results
                search_result['song_key'] = song_key
                if 'id' not in search_result:
                    continue
                # ----non-vip users
                if not self.default_cookies or 'media-user-token' not in self.default_cookies:
                    download_result = safeextractfromdict(search_result, ['attributes', 'previews', 0], {})
                    download_url = download_result.get('url')
                    if not download_url: continue
                    download_url_status = AudioLinkTester(headers=self.default_download_headers, cookies=self.default_download_cookies).test(download_url, request_overrides)
                    if not download_url_status['ok']: continue
                    try:
                        download_result_suppl = AudioLinkTester(headers=self.default_download_headers, cookies=self.default_download_cookies).probe(download_url, request_overrides)
                    except:
                        download_result_suppl = {'download_url': download_url, 'file_size': 'NULL', 'ext': 'NULL'}
                    ext, file_size = download_url.split('.')[-1].split('?')[0], download_result_suppl['file_size']
                    if download_result_suppl['ext'] != 'NULL': ext = download_result_suppl['ext']
                    download_result['download_result_suppl'] = download_result_suppl
                    lyric_result, lyric = {}, 'NULL'
                # ----vip users
                else:
                    account_info = self._fetchaccountinfo(request_overrides=request_overrides)
                    geo = safeextractfromdict(account_info, ['meta', 'subscription', 'storefront'], 'us')
                    params = {"extend": "extendedAssetUrls", "include": "lyrics,albums"}
                    resp = self.get(f'https://amp-api.music.apple.com/v1/catalog/{geo}/songs/{search_result["id"]}', params=params, **request_overrides)
                    if not isvalidresp(resp=resp): continue
                    download_result = resp2json(resp=resp)
                    song_metadata = download_result['data'][0]
                    resp = self.post("https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/webPlayback", json={"salableAdamId": search_result["id"], "language": "en-US"}, **request_overrides)
                    if not isvalidresp(resp=resp): continue
                    webplayback = resp2json(resp=resp)
                    download_result['webplayback'] = webplayback
                    download_item = AppleMusicClientUtils.getsongdownloaditem(song_metadata=song_metadata, webplayback=webplayback, get_license_exchange_func=self._fetchlicenseexchange, request_overrides=request_overrides)
                    lyric_result, lyric = download_item.lyrics_results if download_item.lyrics_results else {}, download_item.lyrics.synced if download_item.lyrics.synced else 'NULL'
                    download_url, ext = download_item, download_item.stream_info.file_format.value
                    download_url_status = AudioLinkTester(headers=self.default_download_headers, cookies=self.default_download_cookies).test(download_url.stream_info.audio_track.stream_url, request_overrides)
                    if not download_url_status['ok']: continue
                    try:
                        download_result_suppl = AudioLinkTester(headers=self.default_download_headers, cookies=self.default_download_cookies).probe(download_url.stream_info.audio_track.stream_url, request_overrides)
                    except:
                        download_result_suppl = {'download_url': download_url.stream_info.audio_track.stream_url, 'file_size': 'NULL', 'ext': 'NULL'}
                    file_size = download_result_suppl['file_size']
                    download_result['download_result_suppl'] = download_result_suppl
                # --lyric results
                if not self.default_cookies or 'media-user-token' not in self.default_cookies:
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
                duration = seconds2hms(float(safeextractfromdict(search_result, ['attributes', 'durationInMillis'], '0')) / 1000)
                song_info = dict(
                    source=self.source, raw_data=dict(search_result=search_result, download_result=download_result, lyric_result=lyric_result), 
                    download_url_status=download_url_status, download_url=download_url, ext=ext, file_size=file_size, lyric=lyric, duration=duration, 
                    song_name=legalizestring(safeextractfromdict(search_result, ['attributes', 'name'], 'NULL'), replace_null_string='NULL'), 
                    singers=legalizestring(safeextractfromdict(search_result, ['attributes', 'artistName'], 'NULL'), replace_null_string='NULL'), 
                    album=legalizestring(safeextractfromdict(search_result, ['attributes', 'albumName'], 'NULL'), replace_null_string='NULL'),
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