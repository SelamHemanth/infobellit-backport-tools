# 🔗 gen_hyperlink.sh

A lightweight shell script to generate HTML files with hyperlinks to commit IDs, using indexed base links. Designed for kernel developers, maintainers, and anyone who needs to organize commit references efficiently.

---

## 🚀 Features

- Add and manage multiple base links with index references
- Generate HTML files with clickable commit links
- Colorful, styled HTML output
- Interactive commit ID input
- Persistent storage of base links in `~/.gen_hyperlink_links`

---

## 📦 Usage

### Add a base link
```bash
./gen_hyperlink.sh --add/-a <link> #Adds the base link to the internal list and assigns it an index.
```
### List saved base links
```bash
./gen_hyperlink.sh --list/-l #Displays all saved base links with their index numbers.
```
### Remove a base link
```bash
./gen_hyperlink.sh --remove/-r <index> #Deletes the base link at the specified index.
```
### Generate HTML with commit links
```bash
./gen_hyperlink.sh <index> #Uses the base link at the given index. Paste commit IDs (one per line), then type done to finish.
```

## 📝 Example

```bash
./gen_hyperlink.sh -a <URL>
./gen_hyperlink.sh -l
./gen_hyperlink.sh 1
🔗 Using base link [1]: <URL>
Paste IDs (one per line). Type 'done' when finished:
ea825523d48c
a1b2c3d4e5f6
done
✅ HTML file generated: links_file.html
```

## 🤝 Author
`Name` : Hemanth Selam



