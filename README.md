<div align="center">
  <img src="https://raw.githubusercontent.com/CharlesPikachu/musicdl/master/docs/logo.png" width="600" alt="musicdl logo" />
  <br />

  <a href="https://musicdl.readthedocs.io/">
    <img src="https://img.shields.io/badge/docs-latest-blue" alt="docs" />
  </a>
  <a href="https://pypi.org/project/musicdl/">
    <img src="https://img.shields.io/pypi/pyversions/musicdl" alt="PyPI - Python Version" />
  </a>
  <a href="https://pypi.org/project/musicdl">
    <img src="https://img.shields.io/pypi/v/musicdl" alt="PyPI" />
  </a>
  <a href="https://github.com/CharlesPikachu/musicdl/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/CharlesPikachu/musicdl.svg" alt="license" />
  </a>
  <a href="https://pypi.org/project/musicdl/">
    <img src="https://static.pepy.tech/badge/musicdl" alt="PyPI - Downloads">
  </a>
  <a href="https://pypi.org/project/musicdl/">
    <img src="https://static.pepy.tech/badge/musicdl/month" alt="PyPI - Downloads">
  </a>
  <a href="https://github.com/CharlesPikachu/musicdl/issues">
    <img src="https://isitmaintained.com/badge/resolution/CharlesPikachu/musicdl.svg" alt="issue resolution" />
  </a>
  <a href="https://github.com/CharlesPikachu/musicdl/issues">
    <img src="https://isitmaintained.com/badge/open/CharlesPikachu/musicdl.svg" alt="open issues" />
  </a>
</div>

<p align="center">
	<a href="https://musicdl.readthedocs.io/" target="_blank"><strong>📚 Documents: musicdl.readthedocs.io</strong></a>
</p>

<div align="center">
<p>
<strong>🎧 Live Demo · MusicSquare (音乐广场)</strong><br />
<a href="https://charlespikachu.github.io/musicsquare/" target="_blank">
  <img
	alt="demo"
	src="https://img.shields.io/badge/demo-online-brightgreen?style=for-the-badge"
  />
</a> <br />
<a href="https://github.com/CharlesPikachu/musicsquare" target="_blank"><strong>🛠 Source Code (MusicSquare)</strong></a> 
</p>

<p>
<em>
  MusicSquare is a browser-based music playground — search, play, and download tracks directly in your browser.<br />
  ⚠️ For learning and testing only: please respect copyright and the terms of each music platform.
</em>
</p>
</div>


# 🎉 What's New

- 2025-12-01: Released musicdl v2.6.1 — we have provided more comprehensive documentation and added four new music search and download sources, *i.e.*, `MituMusicClient`, `GequbaoMusicClient`, `YinyuedaoMusicClient`, and `BuguyyMusicClient`, which allow you to download a large collection of lossless tracks.
- 2025-11-30: Released musicdl v2.6.0 — by tuning and improving the search arguments, we have significantly increased the search efficiency for some music sources, added support for searching and downloading music from Apple Music and MP3 Juice, and made several other minor optimizations.
- 2025-11-25: Released musicdl v2.5.0 — supports searching and downloading from YouTube Music and make musicdl more robust. 
- 2025-11-21: Released musicdl v2.4.6 — fixed bugs caused by mismatched arguments in MusicClient.download and optimized music sources.
- 2025-11-19: Released musicdl v2.4.5 — fix potential in-place modified bugs in HTTP requests.
- 2025-11-19: Released musicdl v2.4.4 — some minor improvements and bug fixes.


# 🎵 Introduction

A lightweight music downloader written in pure Python. Like it? ⭐ Star the repository to stay up to date. Thanks!


# ⚠️ Disclaimer

This project is for educational use only and is not intended for commercial purposes. It interacts with publicly available web endpoints and does not host or distribute copyrighted content.
To access paid tracks, please purchase or subscribe to the relevant music service—do not use this project to bypass paywalls or DRM.
If you are a rights holder and believe this repository infringes your rights, please contact me and I will promptly address it.


# 🎧 Supported Music Client

|  MusicClient (EN)                                                    |  MusicClient (CN)                                                      |   Search           |  Download            |    Code Snippet                                                                                                    |
|  :----:                                                              |  :----:                                                                |   :----:           |  :----:              |    :----:                                                                                                          |
|  [FiveSingMusicClient](https://5sing.kugou.com/index.html)           |  [5SING音乐](https://5sing.kugou.com/index.html)                       |   ✓                |  ✓                   |    [fivesing.py](https://github.com/CharlesPikachu/musicdl/blob/master/musicdl/modules/sources/fivesing.py)        |
|  [KugouMusicClient](http://www.kugou.com/)                           |  [酷狗音乐](http://www.kugou.com/)                                     |   ✓                |  ✓                   |    [kugou.py](https://github.com/CharlesPikachu/musicdl/blob/master/musicdl/modules/sources/kugou.py)              |
|  [KuwoMusicClient](http://www.kuwo.cn/)                              |  [酷我音乐](http://www.kuwo.cn/)                                       |   ✓                |  ✓                   |    [kuwo.py](https://github.com/CharlesPikachu/musicdl/blob/master/musicdl/modules/sources/kuwo.py)                |
|  [LizhiMusicClient](https://www.lizhi.fm/)                           |  [荔枝FM](https://www.lizhi.fm/)                                       |   ✓                |  ✓                   |    [lizhi.py](https://github.com/CharlesPikachu/musicdl/blob/master/musicdl/modules/sources/lizhi.py)              |
|  [MiguMusicClient](https://music.migu.cn/v5/#/musicLibrary)          |  [咪咕音乐](https://music.migu.cn/v5/#/musicLibrary)                   |   ✓                |  ✓                   |    [migu.py](https://github.com/CharlesPikachu/musicdl/blob/master/musicdl/modules/sources/migu.py)                |
|  [NeteaseMusicClient](https://music.163.com/)                        |  [网易云音乐](https://music.163.com/)                                  |   ✓                |  ✓                   |    [netease.py](https://github.com/CharlesPikachu/musicdl/blob/master/musicdl/modules/sources/netease.py)          |
|  [QianqianMusicClient](http://music.taihe.com/)                      |  [千千音乐](http://music.taihe.com/)                                   |   ✓                |  ✓                   |    [qianqian.py](https://github.com/CharlesPikachu/musicdl/blob/master/musicdl/modules/sources/qianqian.py)        |
|  [QQMusicClient](https://y.qq.com/)                                  |  [QQ音乐](https://y.qq.com/)                                           |   ✓                |  ✓                   |    [qq.py](https://github.com/CharlesPikachu/musicdl/blob/master/musicdl/modules/sources/qq.py)                    |
|  [XimalayaMusicClient](https://www.ximalaya.com/)                    |  [喜马拉雅](https://www.ximalaya.com/)                                 |   ✓                |  ✓                   |    [ximalaya.py](https://github.com/CharlesPikachu/musicdl/blob/master/musicdl/modules/sources/ximalaya.py)        |
|  [JooxMusicClient](https://www.joox.com/intl)                        |  [JOOX (QQ音乐海外版)](https://www.joox.com/intl)                      |   ✓                |  ✓                   |    [joox.py](https://github.com/CharlesPikachu/musicdl/blob/master/musicdl/modules/sources/joox.py)                |
|  [TIDALMusicClient](https://tidal.com/)                              |  [TIDAL (提供HiFi音质的流媒体平台)](https://tidal.com/)                |   ✓                |  ✓                   |    [tidal.py](https://github.com/CharlesPikachu/musicdl/blob/master/musicdl/modules/sources/tidal.py)              |
|  [YouTubeMusicClient](https://music.youtube.com/)                    |  [油管音乐](https://music.youtube.com/)                                |   ✓                |  ✓                   |    [youtube.py](https://github.com/CharlesPikachu/musicdl/blob/master/musicdl/modules/sources/youtube.py)          |
|  [AppleMusicClient](https://music.apple.com/)                        |  [苹果音乐](https://music.apple.com/)                                  |   ✓                |  ✓                   |    [apple.py](https://github.com/CharlesPikachu/musicdl/blob/master/musicdl/modules/sources/apple.py)              |
|  [MP3JuiceMusicClient](https://mp3juice.co/)                         |  [MP3 Juice (SoundCloud+YouTube源)](https://mp3juice.co/)              |   ✓                |  ✓                   |    [mp3juice.py](https://github.com/CharlesPikachu/musicdl/blob/master/musicdl/modules/sources/mp3juice.py)        |
|  [MituMusicClient](https://www.qqmp3.vip/)                           |  [米兔音乐](https://www.qqmp3.vip/)                                    |   ✓                |  ✓                   |    [mitu.py](https://github.com/CharlesPikachu/musicdl/blob/master/musicdl/modules/sources/mitu.py)                |
|  [GequbaoMusicClient](https://www.gequbao.com/)                      |  [歌曲宝](https://www.gequbao.com/)                                    |   ✓                |  ✓                   |    [gequbao.py](https://github.com/CharlesPikachu/musicdl/blob/master/musicdl/modules/sources/gequbao.py)          |
|  [YinyuedaoMusicClient](https://1mp3.top/)                           |  [音乐岛](https://1mp3.top/)                                           |   ✓                |  ✓                   |    [yinyuedao.py](https://github.com/CharlesPikachu/musicdl/blob/master/musicdl/modules/sources/yinyuedao.py)      |
|  [BuguyyMusicClient](https://buguyy.top/)                            |  [布谷音乐](https://buguyy.top/)                                       |   ✓                |  ✓                   |    [buguyy.py](https://github.com/CharlesPikachu/musicdl/blob/master/musicdl/modules/sources/buguyy.py)            |


# 🧪 Playground

Here are some projects built on top of musicdl,

|  Project (EN)                                  |   Project (CN)          |   WeChat Article                                             |  Project Location                                                                                                |
|  :----:                                        |   :----:                |   :----:                                                     |  :----:                                                                                                          |
|  Music downloader GUI                          |   音乐下载器GUI界面     |   [click](https://mp.weixin.qq.com/s/fN1ORyI6lzQFqxf6Zk1oIg) |  [musicdlgui](https://github.com/CharlesPikachu/musicdl/tree/master/examples/musicdlgui)                         |
|  Singer lyrics analysis                        |   歌手歌词分析          |   [click](https://mp.weixin.qq.com/s/I8Dy7CoM2ThnSpjoUaPtig) |  [singerlyricsanalysis](https://github.com/CharlesPikachu/musicdl/tree/master/examples/singerlyricsanalysis)     |
|  Lyric-based song snippet retrieval            |   歌词获取歌曲片段      |   [click](https://mp.weixin.qq.com/s/Vmc1IhuhMJ6C5vBwBe43Pg) |  [searchlyrics](https://github.com/CharlesPikachu/musicdl/tree/master/examples/searchlyrics)                     |

For example, the Music Downloader GUI looks/works like this,

<div align="center">
  <img src="https://raw.githubusercontent.com/CharlesPikachu/musicdl/master/examples/musicdlgui/screenshot.png" width="600" alt="musicdl logo" />
</div>


# 📦 Install

You have three installation methods to choose from,

```sh
# from pip
pip install musicdl
# from github repo method-1
pip install git+https://github.com/CharlesPikachu/musicdl.git@master
# from github repo method-2
git clone https://github.com/CharlesPikachu/musicdl.git
cd musicdl
python setup.py install
```

Some of the music downloaders supported by `musicdl` require additional CLI tools to function properly, mainly for decrypting encrypted search/download requests and audio files.
These CLI tools include [FFmpeg](https://www.ffmpeg.org/) and [Node.js](https://nodejs.org/en). Specifically,

- [FFmpeg](https://www.ffmpeg.org/): At the moment, only `TIDALMusicClient` depends on FFmpeg for audio file decoding.
  If you don’t need to use `TIDALMusicClient` when working with `musicdl`, you don’t need to install FFmpeg.
  After installing it, you should run the following command in a terminal (Command Prompt / PowerShell on Windows, Terminal on macOS/Linux) to check whether FFmpeg is on your system `PATH`:
  ```bash
  ffmpeg -version
  ```
  If FFmpeg is installed correctly and on your `PATH`, this command will print the FFmpeg version information (*e.g.*, a few lines starting with `ffmpeg version ...`).
  If you see an error like `command not found` or `'ffmpeg' is not recognized as an internal or external command`, then FFmpeg is either not installed or not added to your `PATH`.

- [Node.js](https://nodejs.org/en): Currently, only `YouTubeMusicClient` in `musicdl` depends on Node.js, so if you don’t need `YouTubeMusicClient`, you don’t have to install Node.js.
  Similar to FFmpeg, after installing Node.js, you should run the following command to check whether Node.js is on your system `PATH`:
  ```bash
  node -v (npm -v)
  ```
  If Node.js is installed correctly, `node -v` will print the Node.js version (*e.g.*, `v22.11.0`), and `npm -v` will print the npm version.
  If you see a similar `command not found` / `not recognized` error, Node.js is not installed correctly or not available on your `PATH`.


# 🚀 Quick Start

#### Typical Examples

Here, we provide some common musicdl use cases to help you quickly get started with the tool.

If you want the quickest way to run musicdl to verify that your environment meets its basic requirements and that musicdl has been installed successfully, you can write and run the following code,

```python
from musicdl import musicdl

music_client = musicdl.MusicClient(music_sources=['MiguMusicClient', 'NeteaseMusicClient', 'QQMusicClient'])
music_client.startcmdui()
```

The above code runs musicdl using `MiguMusicClient`, `NeteaseMusicClient`, and `QQMusicClient` as both the search sources and download sources.

Of course, you can also run musicdl by entering the following equivalent command directly in the command line,

```bash
musicdl -m NeteaseMusicClient,MiguMusicClient,QQMusicClient
```

The demonstration is as follows,

<div align="center">
  <div>
    <img src="https://github.com/CharlesPikachu/musicdl/raw/master/docs/screenshot.png" width="600"/>
  </div>
  <div>
    <img src="https://github.com/CharlesPikachu/musicdl/raw/master/docs/screenshot.gif" width="600"/>
  </div>
</div>
<br />

You can also use `musicdl --help` to see the detailed usage of the musicdl command-line tool, as follows:

```bash
Usage: musicdl [OPTIONS]

Options:
  --version                       Show the version and exit.
  -k, --keyword TEXT              The keywords for the music search. If left
                                  empty, an interactive terminal will open
                                  automatically.
  -m, --music-sources, --music_sources TEXT
                                  The music search and download sources.
                                  [default: MiguMusicClient,NeteaseMusicClient
                                  ,QQMusicClient]
  -i, --init-music-clients-cfg, --init_music_clients_cfg TEXT
                                  Config such as `work_dir` for each music
                                  client as a JSON string.
  -r, --requests-overrides, --requests_overrides TEXT
                                  Requests.get kwargs such as `headers` and
                                  `proxies` for each music client as a JSON
                                  string.
  -c, --clients-threadings, --clients_threadings TEXT
                                  Number of threads used for each music client
                                  as a JSON string.
  -s, --search-rules, --search_rules TEXT
                                  Search rules for each music client as a JSON
                                  string.
  --help                          Show this message and exit.
```

If you want to change the download path for the music files, you can write the following code:

```python
from musicdl import musicdl

init_music_clients_cfg = dict()
init_music_clients_cfg['MiguMusicClient'] = {'work_dir': 'migu'}
init_music_clients_cfg['NeteaseMusicClient'] = {'work_dir': 'netease'}
init_music_clients_cfg['QQMusicClient'] = {'work_dir': 'qq'}
music_client = musicdl.MusicClient(music_sources=['MiguMusicClient', 'NeteaseMusicClient', 'QQMusicClient'])
music_client.startcmdui()
```

Alternatively, you can equivalently run the following command directly in the command line:

```bash
musicdl -m NeteaseMusicClient,MiguMusicClient,QQMusicClient -i "{'MiguMusicClient': {'work_dir': 'migu'}, {'NeteaseMusicClient': {'work_dir': 'netease'}, {'QQMusicClient': {'work_dir': 'qq'}}"
```

If you are a VIP user on a particular music platform, you can pass the cookies from your logged-in web session on that platform to musicdl to improve the quality of song search and downloads. 
Specifically, for example, if you have a membership on `QQMusicClient`, your code can be written as follows:

```python
from musicdl import musicdl

your_vip_cookies_with_str_or_dict_format = ""
init_music_clients_cfg = dict()
init_music_clients_cfg['QQMusicClient'] = {'default_search_cookies': your_vip_cookies_with_str_or_dict_format, 'default_download_cookies': your_vip_cookies_with_str_or_dict_format}
music_client = musicdl.MusicClient(music_sources=['NeteaseMusicClient', 'QQMusicClient'], init_music_clients_cfg=init_music_clients_cfg)
music_client.startcmdui()
```

Of course, you can also achieve the same effect by running the following command directly in the command line:

```bash
musicdl -m NeteaseMusicClient,QQMusicClient -i "{'QQMusicClient': {'default_search_cookies': your_vip_cookies_with_str_or_dict_format, 'default_download_cookies': your_vip_cookies_with_str_or_dict_format}}"
```

If you want to search for more songs on a specific music platform (*e.g.*, `QQMusicClient`), you can do the following:

```python
from musicdl import musicdl

init_music_clients_cfg = dict()
init_music_clients_cfg['QQMusicClient'] = {'search_size_per_source': 20}
music_client = musicdl.MusicClient(music_sources=['NeteaseMusicClient', 'QQMusicClient'], init_music_clients_cfg=init_music_clients_cfg)
music_client.startcmdui()
```

Or enter the following in the command line:

```bash
musicdl -m NeteaseMusicClient,QQMusicClient -i "{'QQMusicClient': {'search_size_per_source': 20}}"
```

In this way, you can see up to 20 search results from `QQMusicClient`.

If you want to use the [pyfreeproxy](https://github.com/CharlesPikachu/freeproxy) library to automatically leverage free online proxies for music search and download, you can do it as follows:

```python
from musicdl import musicdl

init_music_clients_cfg = dict()
init_music_clients_cfg['NeteaseMusicClient'] = {'search_size_per_source': 1000, 'auto_set_proxies': True, 'proxy_sources': ['QiyunipProxiedSession', 'ProxydailyProxiedSession']}
music_client = musicdl.MusicClient(music_sources=['NeteaseMusicClient'], init_music_clients_cfg=init_music_clients_cfg)
music_client.startcmdui()
```

The command-line usage is similar:

```bash
musicdl -m NeteaseMusicClient -i "{'NeteaseMusicClient': {'search_size_per_source': 1000, 'auto_set_proxies': True, 'proxy_sources': ['QiyunipProxiedSession', 'ProxydailyProxiedSession']}}"
```

#### Separating Search and Download Results

You can also call the `.search` and `.download` interfaces of musicdl separately to inspect its intermediate results or perform secondary development,

```python
from musicdl import musicdl

# instance
music_client = musicdl.MusicClient(music_sources=['NeteaseMusicClient'])
# search
search_results = music_client.search(keyword='尾戒')
print(search_results)
song_infos = []
for song_infos_per_source in list(search_results.values()):
    song_infos.extend(song_infos_per_source)
# download
music_client.download(song_infos=song_infos)
```

You can also choose not to use the unified `MusicClient` interface and instead directly import the definition class for a specific music platform for secondary development. 
For example, to import the definition class for `NeteaseMusicClient`:

```python
from musicdl.modules.sources import NeteaseMusicClient

netease_music_client = NeteaseMusicClient()
# search
search_results = netease_music_client.search(keyword='那些年')
print(search_results)
# download
netease_music_client.download(song_infos=search_results)
```

All supported classes can be obtained by printing `MusicClientBuilder.REGISTERED_MODULES`, *e.g*,

```python
from musicdl.modules import MusicClientBuilder

print(MusicClientBuilder.REGISTERED_MODULES)
```

#### TIDAL High-Quality Music Download

If you want to download lossless-quality music from [TIDAL](https://tidal.com/), you need to make sure that [PyAV](https://github.com/PyAV-Org/PyAV) is available or that [FFmpeg](https://www.ffmpeg.org/) is in your environment variables, 
and then use musicdl as follows:

```python
from musicdl import musicdl

music_client = musicdl.MusicClient(music_sources=['TIDALMusicClient'])
music_client.startcmdui()
```

Running the above code will automatically open your default browser and prompt you to log in to TIDAL. Once you have successfully logged in, musicdl will automatically capture the tokens from your session to support subsequent music search and download.

If you are running on a remote server where the browser cannot be opened automatically, you can instead copy the URL printed in the terminal and open it in your local browser to complete the login process.

Note that if the account you log in with is not a paid TIDAL subscription, you will still be unable to download the full lossless audio files.

#### YouTube Music Download

If you want to use musicdl to search for and download music from `YouTubeMusicClient`, you must have [Node.js](https://nodejs.org/en) installed, *e.g.*, on Linux, you can install Node.js using the following script:

```bash
#!/usr/bin/env bash
set -e

# Install nvm (Node Version Manager)
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash

# Load nvm for this script
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

# Install and use latest LTS Node.js
nvm install --lts
nvm use --lts

# Print versions
node -v
npm -v
```

On macOS, you can install Node.js using the following script:

```bash
#!/usr/bin/env bash
set -e

# Install nvm (Node Version Manager)
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash

# Load nvm for this script
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

# Install and use latest LTS Node.js
nvm install --lts
nvm use --lts

# Print versions
node -v
npm -v
```

On Windows (PowerShell), you can install Node.js using the following script:

```bash
# Install Node.js LTS via winget
winget install --id OpenJS.NodeJS.LTS -e --source winget

# Print hint for version check
Write-Output ""
Write-Output "Please reopen PowerShell and run:"
Write-Output "  node -v"
Write-Output "  npm -v"
```

A simple example of searching for and downloading music from `YouTubeMusicClient` is as follows,

```python
from musicdl import musicdl

music_client = musicdl.MusicClient(music_sources=['YouTubeMusicClient'])
music_client.startcmdui()
```

#### WhisperLRC

On some music platforms, it’s not possible to obtain the lyric files corresponding to the audio, *e.g*, `XimalayaMusicClient` and `MituMusicClient`. 
To handle this, we provide a faster-whisper interface that can automatically generate lyrics for tracks whose lyrics are unavailable for download.

For audio files that have already been downloaded, you can use the following invocation to automatically generate lyrics for the local file,

```python
from musicdl.modules import WhisperLRC

your_local_music_file_path = 'xxx.flac'
WhisperLRC(model_size_or_path='base').fromfilepath(your_local_music_file_path)
```

The available `model_size_or_path`, ordered from smallest to largest, are:

```python
tiny, tiny.en, base, base.en, small, small.en, distil-small.en, medium, medium.en, distil-medium.en, large-v1, large-v2, large-v3, large, distil-large-v2, distil-large-v3, large-v3-turbo, turbo
```

In general, the larger the model, the better the generated lyrics (transcription/translation) will be, but this also means it will take longer to run.

If you want to automatically generate lyric files during the download process, 
you can set the environment variable `ENABLE_WHISPERLRC=True` (for example, by running `export ENABLE_WHISPERLRC=True`). 
However, this is generally not recommended, as it may cause a single run of the program to take a very long time,
unless you set `search_size_per_source` to `1` and `model_size_or_path` to `tiny`.

Of course, you can also directly call `.fromurl` to generate a lyrics file for a song given by a direct URL:

```python
from musicdl.modules import WhisperLRC

music_file_link = ''
WhisperLRC(model_size_or_path='base').fromurl(music_link)
```

#### Scenarios Where Quark Netdisk Login Cookies Are Required

Some websites share high-quality or lossless music files via [Quark Netdisk](https://pan.quark.cn/) links, for example, `MituMusicClient`, `GequbaoMusicClient`, `YinyuedaoMusicClient`, and `BuguyyMusicClient`.

If you want to download high-quality or lossless audio files from these music platforms, you need to provide the cookies from your logged-in Quark Netdisk web session when calling musicdl. 
For example, you can do the following: 

```python
from musicdl import musicdl

init_music_clients_cfg = dict()
init_music_clients_cfg['YinyuedaoMusicClient'] = {'quark_parser_config': {'cookies': your_cookies_with_str_or_dict_format}}
init_music_clients_cfg['GequbaoMusicClient'] = {'quark_parser_config': {'cookies': your_cookies_with_str_or_dict_format}}
init_music_clients_cfg['MituMusicClient'] = {'quark_parser_config': {'cookies': your_cookies_with_str_or_dict_format}}
init_music_clients_cfg['BuguyyMusicClient'] = {'quark_parser_config': {'cookies': your_cookies_with_str_or_dict_format}}

music_client = musicdl.MusicClient(music_sources=['MituMusicClient', 'YinyuedaoMusicClient', 'GequbaoMusicClient', 'BuguyyMusicClient'], init_music_clients_cfg=init_music_clients_cfg)
music_client.startcmdui()
```

Please note that musicdl does not provide any speed-limit bypass for Quark Netdisk. 
If the cookies you supply belong to a non-VIP Quark account, the download speed may be limited to only a few hundred KB/s.

#### Apple Music Download

Support for `AppleMusicClient` is currently incomplete, so even users with an Apple Music subscription cannot yet use musicdl to download full high-quality source audio files.

For more details, please refer to the [official documentation](https://musicdl.readthedocs.io/).


# ⭐ Recommended Projects

- [Games](https://github.com/CharlesPikachu/Games): Create interesting games in pure python.
- [DecryptLogin](https://github.com/CharlesPikachu/DecryptLogin): APIs for loginning some websites by using requests.
- [Musicdl](https://github.com/CharlesPikachu/musicdl): A lightweight music downloader written in pure python.
- [Videodl](https://github.com/CharlesPikachu/videodl): A lightweight video downloader written in pure python.
- [Pytools](https://github.com/CharlesPikachu/pytools): Some useful tools written in pure python.
- [PikachuWeChat](https://github.com/CharlesPikachu/pikachuwechat): Play WeChat with itchat-uos.
- [Pydrawing](https://github.com/CharlesPikachu/pydrawing): Beautify your image or video.
- [ImageCompressor](https://github.com/CharlesPikachu/imagecompressor): Image compressors written in pure python.
- [FreeProxy](https://github.com/CharlesPikachu/freeproxy): Collecting free proxies from internet.
- [Paperdl](https://github.com/CharlesPikachu/paperdl): Search and download paper from specific websites.
- [Sciogovterminal](https://github.com/CharlesPikachu/sciogovterminal): Browse "The State Council Information Office of the People's Republic of China" in the terminal.
- [CodeFree](https://github.com/CharlesPikachu/codefree): Make no code a reality.
- [DeepLearningToys](https://github.com/CharlesPikachu/deeplearningtoys): Some deep learning toys implemented in pytorch.
- [DataAnalysis](https://github.com/CharlesPikachu/dataanalysis): Some data analysis projects in charles_pikachu.
- [Imagedl](https://github.com/CharlesPikachu/imagedl): Search and download images from specific websites.
- [Pytoydl](https://github.com/CharlesPikachu/pytoydl): A toy deep learning framework built upon numpy.
- [NovelDL](https://github.com/CharlesPikachu/noveldl): Search and download novels from some specific websites.


# 📚 Citation

If you use this project in your research, please cite the repository.

```
@misc{musicdl2020,
    author = {Zhenchao Jin},
    title = {Musicdl: A lightweight music downloader written in pure python},
    year = {2020},
    publisher = {GitHub},
    journal = {GitHub repository},
    howpublished = {\url{https://github.com/CharlesPikachu/musicdl}},
}
```


# 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=CharlesPikachu/musicdl&type=date&legend=top-left)](https://www.star-history.com/#CharlesPikachu/musicdl&type=date&legend=top-left)


# ☕ Appreciation (赞赏 / 打赏)

| WeChat Appreciation QR Code (微信赞赏码)                                                                                       | Alipay Appreciation QR Code (支付宝赞赏码)                                                                                     |
| :--------:                                                                                                                     | :----------:                                                                                                                   |
| <img src="https://raw.githubusercontent.com/CharlesPikachu/musicdl/master/.github/pictures/wechat_reward.jpg" width="260" />   | <img src="https://raw.githubusercontent.com/CharlesPikachu/musicdl/master/.github/pictures/alipay_reward.png" width="260" />   |


# 📢 WeChat Official Account (微信公众号):

Charles的皮卡丘 (*Charles_pikachu*)  
![img](https://raw.githubusercontent.com/CharlesPikachu/musicdl/master/docs/pikachu.jpg)