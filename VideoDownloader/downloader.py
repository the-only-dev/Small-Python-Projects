import yt_dlp, sys
from yt_dlp.utils import DownloadError
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit, QProgressBar, QComboBox, QCheckBox
from PyQt5.QtCore import Qt, pyqtSignal, QThread

class Downloader(QThread):
  try:
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str)
    speed_signal = pyqtSignal(str)
    time_signal = pyqtSignal(str)
    qualityVideo = ''
    print(f'Video Received is : {qualityVideo}')

    def __init__(self, url, playlistDownload):
      super().__init__()
      self.url = url
      self.playlistDownload = playlistDownload
      
    def format_eta(self, seconds):
      if seconds is None:
          return "N/A"
      minutes, sec = divmod(int(seconds), 60)
      return f"{minutes}m {sec}s" if minutes else f"{sec}s"
    
    def progress_hook(self, d):
      if d['status'] == 'downloading':
        playlistCurrentIndex = d.get('playlist_index')
        playlistTotalCount = d.get('playlist_count')

        if playlistCurrentIndex and playlistTotalCount:
          self.status_signal.emit(f'Downloading {playlistCurrentIndex} of {playlistTotalCount}')
        else:
          self.status_signal.emit('Downloading...')
          
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
        self.status_signal.emit('Download Finished')
    
    
    def run(self):
      try:
        options = {
          'format':f'bestvideo[height<={self.qualityVideo}]+bestaudio',
          'merge_output_format':'mp4',
          'outtmpl': '%(title)s.%(ext)s',
          'progress_hooks': [self.progress_hook],
          'quiet': True,  # Prevent terminal output
          'noplaylist': not self.playlistDownload
        }
        with yt_dlp.YoutubeDL(options) as ydl:
          ydl.download([self.url])
          self.progress_signal.emit(0)
          self.speed_signal.emit('N/A')
          self.time_signal.emit('N/A')
          self.status_signal.emit('All Done!')
      except DownloadError as e:
        self.status_signal.emit(f'Unexpected Error : {e}')

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
  try:
    def __init__(self):
      super().__init__()
      self.setWindowTitle('Portable Video Downloader')
      self.setGeometry(100, 100, 480, 60)  # x, y, width, height

      self.label = QLabel('Enter a Download Link')
      self.label.setAlignment(Qt.AlignLeft)

      self.link = QLineEdit()
      self.link.setAlignment(Qt.AlignLeft)
      self.link.setPlaceholderText('Paste Link Here...')

      #Allow Playlist 
      self.allowPlaylist = QCheckBox('Enable Playlist Download (Will Download Entire Playlist) ')
      self.allowPlaylist.setChecked(False)

      #Adding a Quality Selector Dropdown
      self.selectQuality = QLabel('Select Quality : 8k (Use Video Max if selected quality isnt available)')
      self.qualityDropdown = QComboBox()
      for quality in videoQuality:
        self.qualityDropdown.addItem(quality)
      self.qualityDropdown.currentIndexChanged.connect(self.setQuality)

      self.button = QPushButton('Download')
      self.button.clicked.connect(self.startDownload)

      self.progress = QProgressBar()
      self.progress.setValue(0)

      self.status = QLabel('')
      self.status.setAlignment(Qt.AlignLeft)

      self.estimatedTime = QLabel('ETA : N/A')
      self.estimatedTime.setAlignment(Qt.AlignLeft)

      self.speed = QLabel('Speed : N/A')
      self.speed.setAlignment(Qt.AlignLeft)

      self.layout = QVBoxLayout()
      self.layout.addWidget(self.label)
      self.layout.addWidget(self.link)
      self.layout.addWidget(self.selectQuality)
      self.layout.addWidget(self.qualityDropdown)
      self.layout.addWidget(self.allowPlaylist)
      self.layout.addWidget(self.button)
      self.layout.addWidget(self.progress)
      self.layout.addWidget(self.status)
      self.layout.addWidget(self.speed)
      self.layout.addWidget(self.estimatedTime)
      self.setLayout(self.layout)
      self.show()

      
    def setQuality(self):
      selectedQuality = self.qualityDropdown.currentText()
      self.selectQuality.setText(f'Select Quality : {selectedQuality}')

    def startDownload(self):
      url = self.link.text()
      if not url:
          self.status.setText('Please enter a link')
          return
      playlist = self.allowPlaylist.isChecked()
      self.downloader = Downloader(url, playlist)
      selectedQuality = self.qualityDropdown.currentText()
      self.downloader.qualityVideo = int(videoQuality[selectedQuality])
      self.link.setText('')
      self.downloader.progress_signal.connect(self.progress.setValue)
      self.downloader.status_signal.connect(self.status.setText)
      self.downloader.speed_signal.connect(self.speed.setText)
      self.downloader.time_signal.connect(self.estimatedTime.setText)
      self.status.setText('Establisihing Connection...')
      self.downloader.start()

  except Exception as e:
    print(f'Found Exception in Class VideoDownloader : {e}')


if __name__ == '__main__':
  app = QApplication(sys.argv)
  window = VideoDownloader()
  sys.exit(app.exec_())
