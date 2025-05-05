import yt_dlp, sys, json
from yt_dlp.utils import DownloadError
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QFrame, QPushButton,QHBoxLayout, QVBoxLayout, QLineEdit, QProgressBar, QComboBox, QCheckBox
from PyQt5.QtCore import Qt, pyqtSignal, QThread

class DownloadCancelled(Exception):
  pass

class Downloader(QThread):
  progress_signal = pyqtSignal(int)
  status_signal = pyqtSignal(str)
  speed_signal = pyqtSignal(str)
  time_signal = pyqtSignal(str)

  def __init__(self, url, playlistDownload, qualityVideo):
    super().__init__()
    self.url = url
    self.playlistDownload = playlistDownload
    self.cancelled = False
    self.qualityVideo = qualityVideo
    
  def format_eta(self, seconds):
    if seconds is None:
        return "N/A"
    minutes, sec = divmod(int(seconds), 60)
    return f"{minutes}m {sec}s" if minutes else f"{sec}s"
  
  def progress_hook(self, d):
    
    if self.cancelled:
      print('Called self.cancelled')
      self.status_signal.emit('Status : Download Cancelled')
      raise DownloadCancelled()
       
    if d['status'] == 'downloading':
      info = d.get('info_dict', {})
      currentItem = info.get('playlist_index')
      totalItems = info.get('playlist_count')
    
      if currentItem is not None and totalItems is not None:
        self.status_signal.emit(f'Status : Downloading {currentItem} of {totalItems}')
      else:
        self.status_signal.emit(f'Status : Downloading...')

      downloaded = d.get('downloaded_bytes', 0)
      total = d.get('total_bytes') or d.get('total_bytes_estimate')
      speed = "Speed :" + d.get('_speed_str','N/A')
      eta = d.get('eta')
      eta = "ETA : " + self.format_eta(eta)
      self.time_signal.emit(eta)
      self.speed_signal.emit(speed)
      if total:
        percent = int(downloaded * 100/total)
        self.progress_signal.emit(percent)
    
    elif d['status'] == 'finished':
      self.status_signal.emit('Status : Download Finished')

    elif d['status'] == 'postprocessing':
      self.status_signal.emit("Status : Postprocessing...")
    
  def run(self):
    try:  
      options = {
        'format':f'bestvideo[height<={self.qualityVideo}]+bestaudio',
        'merge_output_format':'mp4',
        'outtmpl': '%(title)s.%(ext)s',
        'progress_hooks': [self.progress_hook],
        'quiet': True,  # Prevent terminal output
        'noplaylist': not self.playlistDownload,
        # 'cookiesfrombrowser' : 'chrome',
      }
      with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([self.url])
        self.progress_signal.emit(0)
        self.speed_signal.emit('N/A')
        self.time_signal.emit('N/A')
        self.status_signal.emit('All Done!')
    except DownloadCancelled:
      self.progress_signal.emit(0)
      self.status_signal.emit('Status : Download Cancelled')

    except DownloadError as e:
      self.status_signal.emit(f'Status : Unexpected Error : {e}')

    except Exception as e:
      print(f'Found Exception in Class Downloader : {e}')

videoQuality = {
  '8k'    : '4320',
  '4k'    : '2160',
  '1440p' : '1440',
  '1080p' : '1080',
  '720p'  : '720',
  '480p'  : '480',
  '360p'  : '360',
  '240p'  : '240',
  '144p'  : '144',
}

class VideoDownloader(QWidget):
  def __init__(self):
    super().__init__()

    self.setWindowTitle('Portable Video Downloader')
    self.setGeometry(100, 100, 1280, 720)  # x, y, width, height
    # self.setObjectName('mainWindow')

    # Item 1 : Paste Layout ---- 1st layer

    # 1.1 : Paste Link Layout ------------------------------------------------
    self.paste_container = QFrame()
    self.paste_layout = QHBoxLayout() 
    self.label = QLabel('Paste Link')
    self.link = QLineEdit()
    self.link.setPlaceholderText('Paste Link Here...')

    self.paste_layout.addWidget(self.label)
    self.paste_layout.addWidget(self.link)
    self.paste_container.setLayout(self.paste_layout)
    self.paste_container.setObjectName('paste_container')

    # # Item 2 : Download Information and Options ---- 2nd layer

    # # 2.1 : Progressbar and Speed Layout --------------- let side
    self.info_container = QFrame()
    self.progress = QProgressBar()
    self.progress.setValue(0)

    self.status = QLabel('Status : --- ')
    self.estimatedTime = QLabel('ETA : N/A')
    self.speed = QLabel('Speed : N/A')

    self.downloadInfoLayout = QVBoxLayout()
    self.downloadInfoLayout.addWidget(self.progress)
    self.downloadInfoLayout.addWidget(self.status)
    self.downloadInfoLayout.addWidget(self.speed)
    self.downloadInfoLayout.addWidget(self.estimatedTime)

    self.info_container.setLayout(self.downloadInfoLayout)
    self.info_container.setObjectName('info_container')
   
    # # 2.2 : Options Section ---------------------------- right side

    self.options_container = QFrame()

    # Adding a Quality Selector Dropdown
    self.selectQuality = QLabel('Select Quality : 8k (Default)')
    self.qualityDropdown = QComboBox()
    self.qualityDropdown.setObjectName('quality_dropdown')
    for quality in videoQuality:
      self.qualityDropdown.addItem(quality)
    self.qualityDropdown.currentIndexChanged.connect(self.setQuality)

    self.qualityBlock = QHBoxLayout() 
    self.qualityBlock.addWidget(self.selectQuality)
    self.qualityBlock.addWidget(self.qualityDropdown)

    # Allow Playlist Download
    self.allowPlaylist = QCheckBox('Playlist Download')
    self.allowPlaylist.setChecked(False)

    # Allow Sound Only Download
    self.soundOnlyCheckbox = QCheckBox('Sound Only')
    self.soundOnlyCheckbox.setChecked(False)

    # Making a block, added in option_container for style
    self.groupOption = QVBoxLayout() 
    self.groupOption.addLayout(self.qualityBlock)
    self.groupOption.addWidget(self.allowPlaylist)
    self.groupOption.addWidget(self.soundOnlyCheckbox)
    self.options_container.setLayout(self.groupOption)
    self.options_container.setObjectName('options_container')

    self.InfoAndOptionLayout = QHBoxLayout()
    self.InfoAndOptionLayout.addWidget(self.info_container)
    self.InfoAndOptionLayout.addWidget(self.options_container)

    # The Second Container containing download and options
    self.second_container = QFrame()
    self.second_container.setLayout(self.InfoAndOptionLayout)
    self.second_container.setObjectName('second_container')
    # self.second_container.

    # #Item 3 : ( In Development )
    # # 3.1 : Download Location
    self.third_container = QFrame()
    self.locationLabel = QLabel('Select Location')

    self.storageLayout = QHBoxLayout()      # Third Layer
    self.storageLayout.addWidget(self.locationLabel)
    self.third_container.setLayout(self.storageLayout)
    self.third_container.setObjectName('third_container')


    # #Item 4 : Download Buttons
    self.fourth_container = QFrame()
    # # 4.1 : Buttons
    self.downloadButton = QPushButton('Download')
    self.downloadButton.clicked.connect(self.startDownload)
    self.downloadButton.setObjectName('downloadButton')

    self.pauseButton = QPushButton('Pause')
    self.pauseButton.setObjectName('pauseButton')

    self.cancelButton = QPushButton('Cancel')
    self.cancelButton.clicked.connect(self.cancelDownload)
    self.cancelButton.setEnabled(False)
    self.cancelButton.setObjectName('cancelBtn')

    self.buttonLayout = QHBoxLayout()
    self.buttonLayout.addWidget(self.downloadButton)
    self.buttonLayout.addWidget(self.pauseButton)
    self.buttonLayout.addWidget(self.cancelButton)

    self.fourth_container.setLayout(self.buttonLayout)
    self.fourth_container.setObjectName('fourth_container')


    # #Item 5 :
    # #5.1 : History
    self.history_container = QFrame()

    self.historyLabel = QLabel('History Layout')
    self.historyItems = QLabel("Item name")

    self.historyLayout = QVBoxLayout()
    self.historyLayout.addWidget(self.historyLabel)
    self.historyLayout.addWidget(self.historyItems)

    self.history_container.setLayout(self.historyLayout)
    self.history_container.setObjectName('history_container')

    self.leftLayout = QVBoxLayout()
    self.leftLayout.addWidget(self.paste_container)
    self.leftLayout.addWidget(self.second_container)
    self.leftLayout.addWidget(self.third_container)
    self.leftLayout.addWidget(self.fourth_container)


    #Main Layout Setup
    self.main_container = QFrame()
    self.mainLayout = QHBoxLayout()

    self.mainLayout.addLayout(self.leftLayout)
    self.mainLayout.addWidget(self.history_container)

    self.main_container.setLayout(self.mainLayout)
    self.setObjectName('main_layout')

    self.setLayout(self.mainLayout)
    self.setStyleSheet(self.load_styles())
    self.show()

  def load_styles(self):
    return """

    #main_layout {
      max-width: 1280px;
      max-height: 720px;
      background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                        stop: 0 #313131, stop: 1 #4A4A4A);
      font-family: 'Segoe UI';
      font-size: 12px;
    }

    #paste_container{ 
      max-width: 740px;
      max-height: 80px;
      background-color: gray; 
      color: white; 
      border-radius: 8px;
      box-shadow: 0px 0px 12px 0px;
    }
    
    #info_container{
      max-width: 200px;
      max-height: 210px;
      background-color: gray;
      border-radius: 8px;
    }

    #options_container{
      max-width: 528px;
      max-height: 210px;
      background-color: gray;
      border-radius: 8px;
    }

    #second_container{
      padding: 0px;
      gap: 12px;
      max-width: 740px;
      max-height: 210px;
    }

    #third_container{
      max-width: 740px;
      max-height: 244px;
      background-color: gray;
      border-radius: 8px;
    }

    #fourth_container{
      max-width: 740px;
      max-height: 80px;
      background-color: gray;
      border-radius: 8px;
    }

    #history_container{
      max-width: 500px;
      max-height: 680px;
      background-color: gray;
      border-radius: 8px;
    }
    """
  
  def setQuality(self):
    selectedQuality = self.qualityDropdown.currentText()
    self.selectQuality.setText(f'Select Quality : {selectedQuality}')

  def startDownload(self):
    url = self.link.text()
    if not url:
        self.status.setText('Please enter a link')
        return
    playlist = self.allowPlaylist.isChecked()
    selectedQuality = int(videoQuality[self.qualityDropdown.currentText()])
    self.downloader = Downloader(url, playlist, selectedQuality)
    self.link.setText('')
    self.downloader.progress_signal.connect(self.progress.setValue)
    self.downloader.status_signal.connect(self.status.setText)
    self.downloader.speed_signal.connect(self.speed.setText)
    self.downloader.time_signal.connect(self.estimatedTime.setText)
    self.status.setText('Status : Establisihing Connection...')
    self.downloader.start()
    self.cancelButton.setEnabled(True)

  def cancelDownload(self):
    if self.downloader:
      self.downloader.cancelled = True
      self.cancelButton.setEnabled(False)

if __name__ == '__main__':
  app = QApplication(sys.argv)
  window = VideoDownloader()
  sys.exit(app.exec_())
