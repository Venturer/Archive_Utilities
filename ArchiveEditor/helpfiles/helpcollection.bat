

"C:\Qt5\5.9.1\mingw53_32\bin\qhelpgenerator" archiveutilities.qhp
"C:\Qt5\5.9.1\mingw53_32\bin\qcollectiongenerator" archiveutilities.qhcp
copy archiveutilities.qhc ..\archiveutilities.qhc
copy archiveutilities.qch ..\archiveutilities.qch

"C:\Qt5\5.9.1\mingw53_32\bin\assistant.exe" -collectionFile archiveutilities.qhc
pause