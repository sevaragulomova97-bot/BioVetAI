# 5. Database strukturasi (SQLite → keyin PostgreSQL)

## species
| maydon | tur | izoh |
|---|---|---|
| id | INTEGER PK | |
| name_uz | TEXT | o'zbekcha nom |
| name_latin | TEXT | ilmiy nom (unikal) |
| class_name, order_name, family | TEXT | taksonomiya |
| description | TEXT | qisqa tavsif |
| iucn_status | TEXT | holat (sana bilan tekshiriladi) |
| source_name, source_url | TEXT | **majburiy manba** |

## Keyingi versiyalar uchun jadvallar
- `facts(id, species_id, text, source_id, verified_by, verified_at)` — alohida faktlar
- `sources(id, name, url, license, accessed_at)`
- `users`, `quiz_results` (o'qituvchi paneli bilan)

## Qoida
Manbasi bo'lmagan yozuv bazaga kiritilmaydi (`NOT NULL`).
