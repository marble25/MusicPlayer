from distutils.core import setup
import py2exe
 
setup(windows=['MusicPlayer3.py'], options={"py2exe": {"includes": ["sip", "PyQt4.QtGui"]}})