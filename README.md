# Taiwan-Tech-GPA-Saviour
http://gpa.taiwan-te.ch/ 

## 功能
- 用來查詢歷年課程的 GPA
- 查詢結果以 GPA 由高至低排序
- 以圖表方式呈現

## 資料來源
初等黑魔法。

## For Developer

### `jsonparser.py`
將 https://querycourse.ntust.edu.tw/querycourse/ 查詢回傳的 ajax 結果處理後存入資料庫。

### `pdfparser.py`
處理下載下來的成績分布表（pdf 格式）。

