WallpaperChanger
================

Python Wallpaper Changer

大量にあるヲ級ちゃんの壁紙をさくっと選びたい！

↓

WMのショートカットキーだけだといろいろできない

↓

GUIで眺めながら選びたいよね！

↓

マウスでクリックとかめんどくさいやん

↓

でもどこでも使いたいから依存ライブラリ少ないほうがいいよね！

↓

つくった


## Features
- GUIでプレビューしながら選べる
- キーボードだけの操作が可能
- Tabによる補完


要は、WMとかからショートカットキーで呼び出す感じのグルー剤のようなものです。

## Screenshot
![main](https://raw.github.com/cocu/WallpaperChanger/master/pic/main.jpg)
![main](https://raw.github.com/cocu/WallpaperChanger/master/pic/filtered.jpg)
![main](https://raw.github.com/cocu/WallpaperChanger/master/pic/review.jpg)

## 注意
- プレビューのみPILが必要
- configに使用するコマンドなどを指定する必要がある。デフォルトはfeh。
- 改造したければどうぞ。
- 私「changerじゃないじゃん、selectorじゃん」


## config
初回起動後、`~/.config/wallpaperchanger.conf` が生成される

```
[Main]
path = ~/picture/wallpaper
command = feh --bg-fill {filepath}

[Wallpaper]
current = illya.jpg
default = saya.jpg
```

`path`に壁紙を保管しているディレクトリ。`command`に壁紙を切り替えるためのコマンド(`{filepath}`がパスに置き換えられる)


## 天望
- 画像によってコマンドのオプションを変えられるようにする。
- EntryでのTabを殺してるからキーボードからlistboxをアクセスする方法がないので作る。
- jpg,pngのデコーダーを内蔵させて標準ライブラリのみにする
