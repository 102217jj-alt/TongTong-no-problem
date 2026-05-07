本資料夾用來放置「真實」的大自然錄音（雨聲、海浪、鳥鳴、森林等），供通通的「去睡覺 / 大自然聲音」功能播放。

建議流程：
- 取得授權合適的音檔（推薦：CC0 / Public Domain / 有明確允許非商用/商用的授權）。
- 轉成常見的網頁播放格式（MP3或OGG），取樣率 44.1kHz 或 48kHz，位元率 128kbps 以上以確保音質。
- 將檔案放到本資料夾，並使用以下實際檔名：
  - rain_thunder1.mp3
  - fall_morning_river.mp3
  - ocean_wave1.mp3

程式行為：
- 當使用者輸入「大自然」或「聲音」時，系統會依關鍵字播放以下檔案：
  - 森林 / 微雨 / 雨 / 雷 -> `/static/audio/nature/rain_thunder1.mp3`
  - 溪流 / 鳥鳴 / 溪水 / 河流 -> `/static/audio/nature/fall_morning_river.mp3`
  - 海浪 / 海邊 / 海風 / 浪聲 -> `/static/audio/nature/ocean_wave1.mp3`
- 若沒有命中關鍵字，預設播放 `/static/audio/nature/rain_thunder1.mp3`。
- 如果該檔案不存在，後端會自動退回到文字轉語音的語音檔（TTS）。

授權提示：
- 上傳或放置音檔前，請確認來源與授權；若使用線上資源（如 freesound.org），請記得標註作者與授權，或選擇 CC0 範例以免有法律風險。

如果需要，我可以幫你：
- 撰寫自動下載腳本（你提供來源 URL）
- 幫你整理可用的免費聲音素材來源（並標註授權）
