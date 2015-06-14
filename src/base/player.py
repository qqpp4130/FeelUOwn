# -*- coding:utf8 -*-

from PyQt5.QtMultimedia import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from base.common import singleton
from base.logger import LOG
import setting


@singleton
class Player(QMediaPlayer):
    """allows the playing of a media source

    The Ui interact with the player with specification.
    make each Mediacontent correspond to a certain music model data

    它也需要维护一个 已下载歌曲的数据库，防止重复下载或者缓存歌曲（暂时这样）
    """

    signal_player_media_changed = pyqtSignal([dict], [QMediaContent])

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__music_list = list()      # 和播放列表同步，保存歌曲名，歌手等信息。（里面的对象是music_model）
        self.__cache_list = list()      # key:music_id, value: media_content
        self.__playlist = QMediaPlaylist()  # 播放列表。里面的对象是qmediacontent

        self.setPlaylist(self.__playlist)

        self.init()

    def init(self):
        self.set_play_mode()
        self.init_signal_binding()

    def init_signal_binding(self):
        self.__playlist.currentIndexChanged.connect(self.on_current_index_changed)
        pass

    def set_play_mode(self, mode=3):
        # item once: 0
        # item in loop: 1
        # sequential: 2
        # loop: 3
        # random: 4
        self.__playlist.setPlaybackMode(mode)

    def add_music(self, music_model):
        self.__music_list.append(music_model)
        media_content = self.get_media_content_from_model(music_model)
        self.__playlist.addMedia(media_content)

    def remove_music(self, music_id):
        for i, music_model in enumerate(self.__music_list):
            if music_id in music_model['id']:
                self.__music_list.remove(music_model)
                return self.__playlist.removeMedia(i)
            else:
                return False

    def get_media_content_from_model(self, music_model):
        # if music_model['id'] in downloaded
        mid = music_model['id']

        # 判断之前是否播放过，是否已经缓存下来，以后需要改变缓存的算法
        for i, each in enumerate(self.__cache_list):
            if mid == each['id']:
                LOG.info(music_model['name'] + ' has been cached')
                return self.__cache_list[i]['content']

        url = music_model['url']
        media_content = QMediaContent(QUrl(url))

        cache = dict()
        cache['id'] = mid
        cache['content'] = media_content
        self.__cache_list.append(cache)

        return media_content

    def cache_music(self, music_index):
        music_model = self.__music_list[music_index]
        # if mid in downloaded
        media_content = self.get_media_content_from_model(music_model)
        return media_content

    def set_music_list(self, music_list):
        self.__music_list = music_list

    def play(self, music_model=None):
        if music_model is None:
            super().play()
            return

        # 播放一首特定的音乐
        self.add_music(music_model)
        super().stop()
        self.__playlist.setCurrentIndex(len(self.__music_list) - 1)
        super().play()

    def play_or_pause(self):
        if self.state() == QMediaPlayer.PlayingState:
            self.pause()
        elif self.state() == QMediaPlayer.PausedState:
            self.play()
        return

    def play_next(self):
        self.__playlist.next()

    def play_last(self):
        self.__playlist.previous()

    @pyqtSlot(int)
    def on_current_index_changed(self, index):
        music_model = self.__music_list[index]
        self.signal_player_media_changed.emit(music_model)



if __name__ == "__main__":
    import sys
    from base.models import MusicModel

    app = QApplication(sys.argv)
    w = QWidget()
    
    p = Player()

    url = 'http://m1.music.126.net/ci1d94nRmgrWaF4IxpZXLQ==/2022001883489851.mp3'  # way back into love
    url = 'http://m1.music.126.net/Gybpf5bX9zfNesjXxZl3qw==/2053887720715417.mp3'  # secret base
    url = 'http://m1.music.126.net/3wDUT2VE7NLeb8ceq9ejFA==/1164382813825096.mp3'

    data = {
        'id': 1234,
        'name': 'secret base',
        'artists': ['unknown'],
        'album': {'name': 'test'},
        'duration': 2000,
        'url': url
    }
    music_model1 = MusicModel(data)
    p.add_music(music_model1)

    url = 'http://m1.music.126.net/ci1d94nRmgrWaF4IxpZXLQ==/2022001883489851.mp3'  # way back into love
    data = {
        'id': 1234,
        'name': 'secret base',
        'artists': ['unknown'],
        'album': {'name': 'test'},
        'duration': 2000,
        'url': url
    }
    music_model2 = MusicModel(data)
    p.add_music(music_model2)

    p.play()
    
    w.show()
    sys.exit(app.exec_())