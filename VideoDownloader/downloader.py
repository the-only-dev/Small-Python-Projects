import yt_dlp, sys, json
from yt_dlp.utils import DownloadError
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton,QHBoxLayout, QVBoxLayout, QLineEdit, QProgressBar, QComboBox, QCheckBox
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
    self.setObjectName('mainWindow')

    # Item 1 : 
    # 1.1 : Paste Link Layout ------------------------------------------------
    self.label = QLabel('Paste Link')
    self.label.setObjectName('labels')
    self.label.setAlignment(Qt.AlignLeft)

    self.link = QLineEdit()
    self.link.setAlignment(Qt.AlignLeft)
    self.link.setPlaceholderText('Paste Link Here...')

    self.LinkLayout = QHBoxLayout() #LinkLayout
    self.LinkLayout.addWidget(self.label)
    self.LinkLayout.addWidget(self.link)

    # Item 2 : 
    # 2.1 : Progressbar and Speed Layout -------------------------------------
    self.progress = QProgressBar()
    self.progress.setValue(0)

    self.status = QLabel('Status : --- ')
    self.status.setAlignment(Qt.AlignLeft)

    self.estimatedTime = QLabel('ETA : N/A')
    self.estimatedTime.setAlignment(Qt.AlignLeft)

    self.speed = QLabel('Speed : N/A')
    self.speed.setAlignment(Qt.AlignLeft)

    self.downloadInfoLayout = QVBoxLayout()  #downloadInfoLayout
    self.downloadInfoLayout.addWidget(self.progress)
    self.downloadInfoLayout.addWidget(self.status)
    self.downloadInfoLayout.addWidget(self.speed)
    self.downloadInfoLayout.addWidget(self.estimatedTime)
   
    # 2.2 : Options Section --------------------------------------------------
    #Allow Playlist Download
    self.allowPlaylist = QCheckBox('Playlist Download')
    self.allowPlaylist.setObjectName('labels')
    self.allowPlaylist.setChecked(False)

    #Adding a Quality Selector Dropdown
    self.selectQuality = QLabel('Select Quality : 8k (Default)')
    self.qualityDropdown = QComboBox()
    self.selectQuality.setObjectName('labels')
    self.qualityDropdown.setObjectName('smallDropdown')
    for quality in videoQuality:
      self.qualityDropdown.addItem(quality)
    self.qualityDropdown.currentIndexChanged.connect(self.setQuality)

    self.qualityLayout = QHBoxLayout() #qualityLayout
    self.qualityLayout.addWidget(self.selectQuality)
    self.qualityLayout.addWidget(self.qualityDropdown)

    self.groupOptionLayout = QVBoxLayout() 
    self.groupOptionLayout.addWidget(self.allowPlaylist)
    self.groupOptionLayout.addWidget(self.qualityLayout)
    
    self.InfoAndOptionLayout = QHBoxLayout()
    self.InfoAndOptionLayout.addWidget(self.downloadInfoLayout)
    self.InfoAndOptionLayout.addWidget(self.groupOptionLayout)
    self.InfoAndOptionLayout = QHBoxLayout()
    
    self.downloadButton = QPushButton('Download')
    self.downloadButton.clicked.connect(self.startDownload)
    self.downloadButton.setObjectName('downloadButton')

    self.cancelButton = QPushButton('Cancel')
    self.cancelButton.setObjectName('cancelBtn')
    self.cancelButton.clicked.connect(self.cancelDownload)
    self.cancelButton.setEnabled(False)

    self.hLayout = QHBoxLayout()
    self.hLayout.addWidget(self.downloadButton)
    self.hLayout.addWidget(self.cancelButton)



    self.layout = QVBoxLayout()
    self.layout.addWidget(self.label)
    self.layout.addWidget(self.link)
    self.layout.addWidget(self.selectQuality)
    self.layout.addWidget(self.qualityDropdown)
    self.layout.addWidget(self.allowPlaylist)

    self.layout.addLayout(self.infoLayout)
    self.layout.addLayout(self.hLayout)
    
    self.setLayout(self.layout)
    self.setStyleSheet(self.load_styles())
    self.show()

  def load_styles(self):
    return """

    #mainWindow {
      background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                        stop: 0 #313131, stop: 1 #4A4A4A);
      font-family: 'Segoe UI';
      font-size: 12px;
    }

    #smallDropdown {
        background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                        stop: 0 red, stop: 1 blue);
      max-width: 80px;
      font-family: arial;
      font-weight: bold;
    }

    #labels {
      font-size: 12px; 
      font-weight: bold; 
      font-family: arial;
    }

    #downloadButton {
      color: black;
      font-family: arial;
    }

    #downloadButton:hover {
      backgrouond-color: skyblue;
      font-family: arial;
      color: blue;
    }

    #downloadButton:pressed {
    border-radius: 4px;
    background-color: blue;
    color: white;
    }

    #cancelBtn {
      font-family: arial;
    }

    #cancelBtn:hover {
      border-radius: 4px;
      background-color: darkred;
      font-family: arial;
      color: white;
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
