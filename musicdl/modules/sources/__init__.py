'''initialize'''
from .qq import QQMusicClient
from .mitu import MituMusicClient
from .joox import JooxMusicClient
from .base import BaseMusicClient
from .kuwo import KuwoMusicClient
from .migu import MiguMusicClient
# from .tidal import TIDALMusicClient
from .lizhi import LizhiMusicClient
# from .apple import AppleMusicClient
from .kugou import KugouMusicClient
from .buguyy import BuguyyMusicClient
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
        'QQMusicClient': QQMusicClient, 'MituMusicClient': MituMusicClient, 'BuguyyMusicClient': BuguyyMusicClient, 'GequbaoMusicClient': GequbaoMusicClient,
        'MP3JuiceMusicClient': MP3JuiceMusicClient, 'YinyuedaoMusicClient': YinyuedaoMusicClient, 'LizhiMusicClient': LizhiMusicClient, 'XimalayaMusicClient': XimalayaMusicClient,
        'JooxMusicClient': JooxMusicClient, 'KuwoMusicClient': KuwoMusicClient, 'KugouMusicClient': KugouMusicClient, 'FiveSingMusicClient': FiveSingMusicClient,
        'QianqianMusicClient': QianqianMusicClient, 'MiguMusicClient': MiguMusicClient, 'NeteaseMusicClient': NeteaseMusicClient, 'YouTubeMusicClient': YouTubeMusicClient,
    }


'''BuildMusicClient'''
BuildMusicClient = MusicClientBuilder().build