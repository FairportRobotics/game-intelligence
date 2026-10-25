# web/static/vendor/ - Libraries saved locally (NO CDN links!)

Competition wifi is unreliable, so every JavaScript/CSS/font file our pages use
must live in THIS folder and be linked with `url_for('static', filename='vendor/...')`.
A page that loads a file from the internet will look broken at the event.

## Download these once (while you have internet), then commit them

| File to save here        | Where to get it                                   | Used for                   |
|--------------------------|---------------------------------------------------|----------------------------|
| `pico.min.css`           | https://picocss.com  (the "classless/minified" CSS) | Basic phone-friendly styles |
| `htmx.min.js`            | https://htmx.org  (download the minified file)    | Auto-refresh, form submits |
| `plotly.min.js`          | https://plotly.com/javascript/  (later, for charts) | Charts                     |
| `Sortable.min.js`        | https://sortablejs.github.io/Sortable/ (later)    | Drag-to-reorder pick list  |
| fonts (optional)         | Save any web font files here and use @font-face   | Look and feel              |

## Test it
Turn the wifi OFF, run `python run.py`, and open the site. If a page looks plain or
a button does nothing, a file is missing from this folder.

(This is a great Beginner task: download the files, commit them, and check the pages.)
