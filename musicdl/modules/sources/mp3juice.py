'''
Function:
    Implementation of MP3JuiceMusicClient: https://mp3juice.co/
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
import re
import json
import copy
import time
import base64
from bs4 import BeautifulSoup
from urllib.parse import quote
from .base import BaseMusicClient
from urllib.parse import urlencode
from rich.progress import Progress
from ..utils import legalizestring, usesearchheaderscookies, usedownloadheaderscookies, touchdir, resp2json, SongInfo, MusicInfoUtils


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
    '''_download'''
    @usedownloadheaderscookies
    def _download(self, song_info: SongInfo, request_overrides: dict = None, downloaded_song_infos: list = [], progress: Progress = None, song_progress_id: int = 0):
        request_overrides = request_overrides or {}
        try:
            touchdir(song_info.work_dir)
            total_size = song_info.downloaded_contents.__sizeof__()
            progress.update(song_progress_id, total=total_size)
            with open(song_info.save_path, "wb") as fp:
                fp.write(song_info.downloaded_contents)
            progress.advance(song_progress_id, total_size)
            progress.update(song_progress_id, description=f"{self.source}.download >>> {song_info.song_name} (Success)")
            downloaded_song_infos.append(MusicInfoUtils.fillsongtechinfo(copy.deepcopy(song_info)))
        except Exception as err:
            progress.update(song_progress_id, description=f"{self.source}.download >>> {song_info.song_name} (Error: {err})")
        return downloaded_song_infos
    '''_decodebin'''
    def _decodebin(self, bin_str: str):
        return [int(b, 2) for b in bin_str.split() if b]
    '''_decodehex'''
    def _decodehex(self, hex_str: str):
        bytes_tokens = re.findall(r'0x[0-9a-fA-F]{2}', hex_str)
        return ''.join(chr(int(h, 16)) for h in bytes_tokens)
    '''_authorization'''
    def _authorization(self, gc: dict) -> str:
        bin_str, secret_b64 = gc["Ffw"]
        flag_reverse, offset, max_len, case_mode = gc["LUy"]
        hex_str = gc["Ixn"][0]
        secret = base64.b64decode(secret_b64).decode("utf-8", errors="ignore")
        if flag_reverse > 0: secret = secret[::-1]
        idx_list = self._decodebin(bin_str)
        t = "".join(secret[i - offset] for i in idx_list)
        if max_len > 0: t = t[:max_len]
        if case_mode == 1: t = t.lower()
        elif case_mode == 2: t = t.upper()
        suffix = self._decodehex(hex_str)
        raw = f"{t}_{suffix}"
        return base64.b64encode(raw.encode("utf-8")).decode("ascii")
    '''_constructsearchurls'''
    def _constructsearchurls(self, keyword: str, rule: dict = None, request_overrides: dict = None):
        # init
        rule, request_overrides = rule or {}, request_overrides or {}
        resp = self.get('https://mp3juice.co/', **request_overrides)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        gc_script_text = None
        for script in soup.find_all("script"):
            text = script.string or ""
            if "var gC" in text and "dfU" in text:
                gc_script_text = text; break
        if not gc_script_text: raise RuntimeError('gC script not found in HTML')
        m = re.search(r"var\s+j\s*=\s*(\{.*?});", gc_script_text, flags=re.S)
        if not m: raise RuntimeError("j object not found in gC script")
        j_obj_str = m.group(1)
        j_dict = json.loads(j_obj_str)
        key_names = [base64.b64decode(x).decode("utf-8") for x in j_dict["dfU"]]
        gc = {name: j_dict[name] for name in key_names}
        auth_code = self._authorization(gc=gc)
        # search rules
        default_rule = {'a': auth_code, 'y': 's', 'q': keyword, 't': str(int(time.time()))}
        default_rule.update(rule)
        default_rule['q'] = base64.b64encode(quote(keyword, safe="").encode("utf-8")).decode("utf-8")
        # construct search urls based on search rules
        base_url = 'https://mp3juice.co/api/v1/search?'
        page_rule = copy.deepcopy(default_rule)
        search_urls = [{'search_url': base_url + urlencode(page_rule), 'auth_code': auth_code}]
        self.search_size_per_page = self.search_size_per_source
        # return
        return search_urls
    '''_search'''
    @usesearchheaderscookies
    def _search(self, keyword: str = '', search_url: dict = None, request_overrides: dict = None, song_infos: list = [], progress: Progress = None, progress_id: int = 0):
        # init
        request_overrides, search_meta = request_overrides or {}, copy.deepcopy(search_url)
        search_url, auth_code = search_meta['search_url'], search_meta['auth_code']
        # successful
        try:
            # --search results
            resp = self.get(search_url, **request_overrides)
            resp.raise_for_status()
            search_results = resp2json(resp)
            search_results = list({item.get("id"): item for item in (search_results["yt"] + search_results["sc"])}.values())
            for search_result in search_results:
                # --download results
                if not isinstance(search_result, dict) or ('id' not in search_result):
                    continue
                song_info, download_result = SongInfo(source=self.source), dict()
                # ----init
                params = {'o': auth_code, 't': str(int(time.time()))}
                try:
                    resp = self.get('https://www1.eooc.cc/api/v1/init?', params=params, **request_overrides)
                    resp.raise_for_status()
                    download_result['init'] = resp2json(resp=resp)
                    convert_url = download_result['init'].get('convertURL', '')
                    if not convert_url: continue
                except:
                    continue
                # ----convert
                convert_url = f'{convert_url}&v={search_result["id"]}&f=mp3&t={str(int(time.time()))}'
                try:
                    resp = self.get(convert_url, **request_overrides)
                    resp.raise_for_status()
                    download_result['conver'] = resp2json(resp=resp)
                    redirect_url = download_result['conver'].get('redirectURL', '')
                    if not redirect_url: continue
                except:
                    continue
                # ----redirect
                try:
                    resp = self.get(redirect_url, **request_overrides)
                    resp.raise_for_status()
                    download_result['redirect'] = resp2json(resp=resp)
                    download_url: str = download_result['redirect'].get('downloadURL', '')
                    if not download_url: continue
                except:
                    continue
                # ----test and probe
                download_url_status = self.audio_link_tester.test(download_url, request_overrides)
                download_url_status['probe_status'] = self.audio_link_tester.probe(download_url, request_overrides)
                ext = download_url_status['probe_status']['ext']
                if ext == 'NULL': download_url.split('.')[-1].split('?')[0] or 'mp3'
                song_info.update(dict(
                    download_url=download_url, download_url_status=download_url_status, raw_data={'search': search_result, 'download': download_result},
                    use_quark_default_download_headers=False, ext=ext, file_size=download_url_status['probe_status']['file_size']
                ))
                if not song_info.with_valid_download_url: continue
                # ----download should be directly conducted otherwise will have 404 errors
                song_info.downloaded_contents = self.get(download_url, **request_overrides).content
                # ----parse more infos
                lyric_result, lyric = dict(), 'NULL'
                singers_song_name = search_result.get('title', 'NULL-NULL').split('-')
                if len(singers_song_name) == 1:
                    singers, song_name = 'NULL', singers_song_name[0].strip()
                elif len(singers_song_name) > 1:
                    singers, song_name = singers_song_name[0].strip(), singers_song_name[1].strip()
                song_info.raw_data['lyric'] = lyric_result
                song_info.update(dict(
                    lyric=lyric, duration='-:-:-', song_name=legalizestring(song_name, replace_null_string='NULL'), singers=legalizestring(singers, replace_null_string='NULL'), 
                    album='NULL', identifier=search_result['id'],
                ))
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