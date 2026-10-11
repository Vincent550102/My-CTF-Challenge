# AIS3 PreExam 2026

| Name | Category | Solve | Keywords |
|------------------|----------|-------------|----------|
| [LinkedOut](LinkedOut) | Web |  | `Flask` `Jinja2` `Python sandbox` |

## LinkedOut

LinkedOut 是以 Flask 建置的社群網站題目，包含貼文模板、獨立 renderer 與 Recruiter Labs。

題目原始碼、Docker 設定、既有解題腳本及驗證腳本收錄於 [LinkedOut](LinkedOut)；詳細部署方式見 [題目 README](LinkedOut/README.md)。

本機啟動：

```sh
cd LinkedOut
docker compose up --build
```

開啟 http://localhost:8000，並註冊自己的帳號。

另附 Instancer，可為每個帳號建立獨立的 web 與 renderer 容器；設定範例位於 [instancer/.env.example](LinkedOut/instancer/.env.example)。
