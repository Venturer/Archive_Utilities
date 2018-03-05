# -*- mode: python -*-

block_cipher = None


a = Analysis(['ArchiveUtilities3.py'],
             pathex=['C:\\Users\\steph\\OneDrive\\Documents\\QtPython\\ArchiveEditor\\ArchiveEditor'],
             binaries=None,
             datas=[('*.ui', '.'), ('*.py', './sources'), ('*.qhc', '.'), ('*.qch', '.'), ('*.ini', '.'), ('*.json', '.')],
             hiddenimports=['*.ui'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='ArchiveUtilities',
          debug=False,
          strip=False,
          upx=False,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='ArchiveUtilities')
