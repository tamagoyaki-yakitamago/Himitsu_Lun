# ひみつるん

## 概要

ひみつるんは、秘密分散を利用した安全なファイル共有サイトです。
( K , N ) しきい値法に基づき、N個のシェア情報を作成し、K個入力することで元のファイルを取得できます。
サーバー側は秘密分散で暗号化されたファイルのみを保持し、アップロードされた元のファイルは保持しません。

## アクティビティ図

### アップロード概要

```plantuml
@startuml

start
:File upload;

start

if (File can upload?) then (yes)
  :create and share shares;
else (no)
  :alert error message;
endif

stop

@enduml
```
