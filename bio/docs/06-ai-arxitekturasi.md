# 6. AI tizimi arxitekturasi

## Tamoyil
AI **o'zi bilgan narsani emas, bazadagi tekshirilgan ma'lumotni** javob qiladi (RAG yondashuvi).

## MVP (bepul, LLMsiz)
1. Foydalanuvchi savoli → kalit so'zlarga ajratiladi.
2. Bazadan mos turlar qidiriladi (nom, tavsif, taksonomiya bo'yicha).
3. Topilsa: ma'lumot + manba havolasi qaytariladi.
4. Topilmasa: "Bu haqda bazamda tasdiqlangan ma'lumot yo'q."

## 2-versiya (LLM bilan)
```
Savol → embedding qidiruv (bazadan top-3 parcha)
      → LLM ga: "Faqat shu parchalardan javob ber, manba keltir"
      → javob + manbalar → foydalanuvchi
```
- Javobda manba bo'lmasa, javob ko'rsatilmaydi.
- Xato javoblar uchun "Xatoni xabar qilish" tugmasi.
- LLM xizmati narxi va o'zbek tili sifatini tanlashdan oldin sinab ko'ring.

## Xavflar
Gallyutsinatsiya (cheklov: faqat berilgan matn), eskirgan holat (sana belgisi), til sifati (o'zbekcha testlar).
