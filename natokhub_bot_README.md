# 🎬 Natokhub Bot — সেটআপ গাইড

## ফাইল স্ট্রাকচার
```
natokhub_bot/
├── bot.py              # মেইন বট
├── server.py           # ওয়েব সার্ভার (Mini App)
├── webapp/
│   └── index.html      # অ্যাড পেজ
├── requirements.txt
├── render.yaml         # Render deploy config
└── episodes.json       # ডেটা (auto তৈরি হবে)
```

---

## ধাপ ১ — Render.com এ Deploy করো (ফ্রি)

1. [render.com](https://render.com) এ account করো
2. GitHub এ এই ফোল্ডার আপলোড করো
3. Render এ "New Web Service" → GitHub repo সিলেক্ট করো
4. **server.py** deploy হলে একটা URL পাবে যেমন:
   `https://natokhub-webapp.onrender.com`

---

## ধাপ ২ — bot.py তে URL দাও

`bot.py` এর উপরে:
```python
WEB_URL = "https://natokhub-webapp.onrender.com"  # তোমার URL
```

---

## ধাপ ৩ — BotFather এ Mini App সেট করো

1. [@BotFather](https://t.me/BotFather) এ যাও
2. `/mybots` → তোমার বট → **Bot Settings** → **Menu Button**
3. URL দাও: `https://natokhub-webapp.onrender.com/ad`

---

## ধাপ ৪ — বট চালু করো

```bash
pip install -r requirements.txt
python bot.py
```

---

## অ্যাডমিন কমান্ড

| কমান্ড | কাজ |
|--------|-----|
| `/add` | নতুন এপিসোড অ্যাড (নম্বর → টাইটেল → থাম্বনেইল → ভিডিও) |
| `/delete 88` | এপিসোড ডিলিট |
| `/list` | সব এপিসোড লিস্ট |

---

## এপিসোড অ্যাড করার নিয়ম

1. `/add` দাও
2. এপিসোড নম্বর দাও (যেমন: `88`)
3. টাইটেল দাও
4. থাম্বনেইল ছবি পাঠাও (Photo হিসেবে)
5. ভিডিও ফাইল পাঠাও

ব্যস! ইউজাররা `/start` দিলে নতুন এপিসোড দেখতে পাবে।

---

## ইউজার ফ্লো

```
/start
  → থাম্বনেইল সহ ৮টা এপিসোড দেখায়
  → "Episode দেখুন" বাটন
  → Mini App খোলে
  → ১ম অ্যাড (১৫ সেকেন্ড টাইমার)
  → Continue বাটন
  → ২য় অ্যাড
  → "সফলভাবে সম্পন্ন" স্ক্রিন
  → "ইনবক্স চেক করুন" বাটন
  → বটে সরাসরি ভিডিও আসে ✅
```
