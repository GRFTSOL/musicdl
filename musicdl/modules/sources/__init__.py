'''initialize'''
from .qq import QQMusicClient
from .mitu import MituMusicClient
from .joox import JooxMusicClient
from .base import BaseMusicClient
from .kuwo import KuwoMusicClient
from .migu import MiguMusicClient
from .tidal import TIDALMusicClient
from .lizhi import LizhiMusicClient
from .apple import AppleMusicClient
from .kugou import KugouMusicClient
from ..utils import BaseModuleBuilder
from .netease import NeteaseMusicClient
from .youtube import YouTubeMusicClient
from .gequbao import GequbaoMusicClient
from .mp3juice import MP3JuiceMusicClient
from .fivesing import FiveSingMusicClient
from .qianqian import QianqianMusicClient
from .ximalaya import XimalayaMusicClient
from .yinyuedao import YinyuedaoMusicClient


'''MusicClientBuilder'''
class MusicClientBuilder(BaseModuleBuilder):
    REGISTERED_MODULES = {
        'FiveSingMusicClient': FiveSingMusicClient, 'KuwoMusicClient': KuwoMusicClient, 'KugouMusicClient': KugouMusicClient,
        'QianqianMusicClient': QianqianMusicClient, 'QQMusicClient': QQMusicClient, 'MiguMusicClient': MiguMusicClient,
        'JooxMusicClient': JooxMusicClient, 'LizhiMusicClient': LizhiMusicClient, 'NeteaseMusicClient': NeteaseMusicClient,
        'XimalayaMusicClient': XimalayaMusicClient, 'TIDALMusicClient': TIDALMusicClient, 'YouTubeMusicClient': YouTubeMusicClient,
        'AppleMusicClient': AppleMusicClient, 'MP3JuiceMusicClient': MP3JuiceMusicClient, 'MituMusicClient': MituMusicClient,
        'GequbaoMusicClient': GequbaoMusicClient, 'YinyuedaoMusicClient': YinyuedaoMusicClient,
    }


'''BuildMusicClient'''
BuildMusicClient = MusicClientBuilder().build