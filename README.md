# gemini-youtube-killer

[Читать на русском (README.ru.md)](README.ru.md)

A zero-dependency surgical CLI utility that fixes fatal **HTTP 500 "Internal Error"** crashes in **Google AI Studio** caused by deleted or privatized YouTube video embeds.

Performs **in-place (`r+`)** JSON AST pruning of dead `youtubeVideo` chunks while preserving the underlying OS inode and Google Drive file handle (`googleId`), allowing the web client to instantly hot-reload the healed session without state loss.

---

## The Bug: Death by a Broken Video

When working on long multimodal sessions in Google AI Studio, attaching YouTube URLs is a common workflow. However, the platform possesses a critical validation vulnerability:

1. You attach a YouTube video as a multimodal context chunk.
2. Months later, the author of that video deletes it or switches its visibility to **Private**.
3. **The Disaster:** Google's backend validates all external media assets upon each new turn. When an asset becomes inaccessible, backend validation crashes with an unhandled exception.
4. The web UI loads the chat history normally, but **any subsequent query instantly fails** with:
   An internal error has occurred.
5. The Google AI Studio web interface provides no mechanism to selectively excise historical chunks from deep within the conversation tree. The entire multi-month project becomes locked.

---

## The Fix: In-Place r+ Surgical Pruning

Google AI Studio prompts are synchronized locally via Google Drive as JSON files containing `chunkedPrompt.chunks`. Videos reside in chunks marked with the `youtubeVideo` key.

### Why Naive Scripts Fail
Opening the file with `open(path, 'w')` replaces the OS file descriptor/inode. The Google Drive desktop sync client interprets this as a file deletion followed by creation, severing the cloud `googleId` link and corrupting the browser session.

### The r+ Inode Preservation Strategy
`gemini_youtube_killer.py` mutates the file strictly **in-place**:
1. Opens the file in `r+` mode.
2. Identifies all chunks containing `youtubeVideo`.
3. Backs up removed chunks into a sidecar file (`<log>_youtube.json`) so zero metadata is lost.
4. Rewrites the cleaned payload using `f.seek(0)` and `f.truncate()`.

The file descriptor, inode, and Google Drive ID remain identical. Google Drive instantly synchronizes the byte delta, and refreshing the AI Studio browser tab (`F5`) brings the dead chat back to life.

---

## Usage

Simply run the script pointing to your synced Google AI Studio JSON file:

python gemini_youtube_killer.py "G:\My Drive\Google AI Studio\My_Project.json"

Example Output:
[+] Удалено роликов: 1, осталось чанков: 42. Копия: 'G:\My Drive\Google AI Studio\My_Project_youtube.json'

Switch to Google AI Studio in your browser, hit F5, and continue your conversation.

---

## Author & License
* **Author:** Alexey D. Zaitsev (alexeydzaitsev3749) — Systems Architect | 40+ Years in Systems Programming (RSX-11, C++, UNIX)
* **License:** MIT
