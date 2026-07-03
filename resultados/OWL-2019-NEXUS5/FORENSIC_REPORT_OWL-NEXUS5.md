# FORENSIC REPORT
## Case VIGIA-OWL-2019-NEXUS5 — Project OWL: Illegal Owl Trade
### LGE Nexus 5 Mobile Device — Full Image Analysis

---

**Report Date:** 2026-07-03  
**Examiner:** VIGIA Forensic Intentionality Analysis Engine v2.0  
**Operator:** Anna Tchijova  
**Case Reference:** VIGIA-OWL-2019-NEXUS5  
**Classification:** SUSPICION (Manual Override — see Section 7)

---

## 1. EVIDENCE IDENTIFICATION

| Field | Value |
|-------|-------|
| **Image File** | LGE Nexus 5 Full Image.raw |
| **SHA-1** | F46EE05CE1A2210501EA512ED9E4C7EC59222CCA |
| **MD5** | B334843A07A9E16494EEBDF3079E6BC6 |
| **Imaging Tool** | Magnet ACQUIRE v2.0.0.5412 |
| **Imaging Date (UTC)** | 2017-02-06 20:51:09 — 22:13:08 |
| **Evidence Number** | MD1 |
| **Device** | LGE Nexus 5 (hammerhead) |
| **OS** | Android 6.0.1 (M4B30Z) |
| **Serial** | 08ebf545d00af782 |
| **Encryption Status** | Unencrypted (FDE disabled by root) |

### 1.1 Partition Table (GPT, 29 partitions)

| Partition | Name | Size | Filesystem | Forensic Value |
|-----------|------|------|-----------|----------------|
| P1 | modem | 64 MB | FAT16 | Firmware radio |
| P16 | persist | 16 MB | ext4 | WiFi/BT/DRM/sensor config |
| P19 | boot | 22 MB | ANDROID! | Boot image |
| P20 | recovery | 22 MB | ANDROID! | Recovery image |
| P25 | system | 1 GB | ext4 | Android system, build.prop |
| P26 | crypto | 30 MB | Empty | FDE footer (wiped) |
| P27 | cache | 700 MB | ext4 | TWRP recovery logs |
| **P28** | **userdata** | **27.2 GB** | **ext4** | **Primary evidence — full /data** |

### 1.2 Device Modification State

The device was **rooted** via TWRP custom recovery with SuperSU v2.79:
- `su.img` present at `/data/su.img` (100 MB)
- TWRP backup metadata: `/data/media/0/TWRP/BACKUPS/08ebf545d00af782`
- SuperSU flasheado via `openrecoveryscript`
- BusyBox installed at `/system/xbin/busybox`
- FDE encryption was disabled (crypto partition wiped)

---

## 2. SUBJECT IDENTIFICATION

| Field | Value |
|-------|-------|
| **Name** | Sarah McAvoy |
| **Primary Email** | mcavoys87@gmail.com |
| **Google UID** | 101797553944830818468 |
| **Phone Number** | 1(304)638-8446 |
| **Musical.ly User** | sarahmcavoy (ID: 190719500932296704) |
| **Twitter** | @mcavoys87 |
| **Skype** | mcavoys87@gmail.com |
| **TikTok Accounts** | SarahMcavoy, sarahmcavoy |

### 2.1 Account Creation Timeline

| Date (UTC) | Account | Platform |
|------------|---------|----------|
| 2017-01-24 14:28 | mcavoys87@gmail.com | Google |
| 2017-01-30 22:03 | SarahMcavoy | Musical.ly (TikTok) |
| 2017-01-30 22:27 | sarahmcavoy | Musical.ly (TikTok) |
| 2017-01-30 23:01 | mcavoys87@gmail.com | Skype |
| 2017-02-01 17:04 | mcavoys87 | Twitter |

---

## 3. COUNTERPARTY IDENTIFICATION

| Field | Value |
|-------|-------|
| **Name** | Layla Aster |
| **Musical.ly** | layster82 (ID: 190723800861179904) |
| **Email** | Layster82@gmail.com |
| **Role** | Owl seller/trader |

---

## 4. EVIDENCE ANALYSIS

### 4.1 Web Search Activity (Chrome / Google Search)

Recovered from raw partition string analysis of userdata:

| Search Query | Source | Significance |
|-------------|--------|--------------|
| "where to buy owls" | Google Search | Direct purchase intent |
| "how to take care of owls" | Google Search | Pre-purchase husbandry research |
| "harry potter bird name" | Google Search | Pop-culture owl interest (Hedwig) |
| "snowy owl facts" | Facebook Search | Owl species research |
| "Green sea turtle" | Chrome (task 105) | Distractor/noise |
| "Tina and password" | Google Search (task 95) | Anomalous — potential credential seeking |

### 4.2 Birdtrader.co.uk Browsing

Cookies and browsing history confirm visits to owl marketplace:

| URL | Listing |
|-----|---------|
| `m.birdtrader.co.uk/birds-of-prey-for-sale/owls` | Owls for sale index |
| `m.birdtrader.co.uk/birds-of-prey-for-sale/owls?sstr=Baby%20owl` | Search: "Baby owl" |
| `m.birdtrader.co.uk/owls/barn-owls-for-sale/557933` | Barn Owls — Lincolnshire, East Midlands |
| `m.birdtrader.co.uk/owls/bonding-pair-asian-wood-owls/558006` | Asian Wood Owls — Northamptonshire |
| `m.birdtrader.co.uk/owls/tawny-owls-for-sale/557493` | Tawny Owls — Londonderry, Northern Ireland |

Google Analytics cookie confirms visit: `_gaGA1.3.1312370630.1485310916` (timestamp: 2017-01-25).

### 4.3 Musical.ly Chat Messages (Critical Evidence)

Recovered from raw partition string extraction. Messages between `sarahmcavoy` (buyer) and `layster82` / Layla Aster (seller):

**Message 1 — Sarah to Layla:**
> "Hi Layla I accidentally deleted the string of emails we sent so I lost your contact. do you. are to send me your email again sorry for the inconvenience. also if it's easier you can send me information through here as well"

**Significance:** Confirms prior email correspondence about the transaction. Sarah references deleted emails — either accidental or deliberate anti-forensic action.

**Message 2 — Layla to Sarah:**
> "The email is Layster82gmail"

**Significance:** Seller provides email contact for transaction coordination.

**Message 3 — Layla to Sarah:**
> [IMAGE] `66560c50-e73f-11e6-be73-fff3b1707aec` (220x310 px)

**Significance:** Image of owl being offered for sale. Hosted on `a1.hyphenate.io/musically/musically/chatfiles/`.

**Message 4 — Layla to Sarah:**
> "How do you like him"

**Significance:** Seller presenting specific live animal ("him") to buyer.

**Message 5 — Sarah to Layla:**
> "is that an image of the exact one you have or is it a photo of what it will look like?"

**Significance:** Buyer verifying authenticity of the specific animal. This constitutes active purchase negotiation.

### 4.4 Facebook Activity

Owl-related content viewed:
- `beautiful_owl_photos_featured.jpg` (shareably.net)
- `familyowlscameraden.jpg` (owlday.com)
- Snowy Owl Wikipedia images (Barrow Alaska, Schnee-Eule)
- "Snowy Owl Facts" community page

### 4.5 Anti-Forensic Measures

| Measure | Evidence |
|---------|----------|
| CM Security AppLock | Installed to protect Musical.ly and Snapchat behind secondary PIN |
| CM Locker | Additional screen lock layer |
| Email Deletion | Sarah states she "accidentally deleted the string of emails" with Layla |
| Device Rooting | TWRP + SuperSU v2.79 — enables data wipe/manipulation |
| FDE Disabled | Crypto partition wiped — facilitates access but also potential reset |
| Communication Compartmentalization | Owl trade on Musical.ly only; Skype used for unrelated chat |

### 4.6 Installed Applications

Key apps relevant to the investigation:

| Package | App | Forensic Role |
|---------|-----|---------------|
| com.zhiliaoapp.musically | Musical.ly (TikTok) | **Primary communication channel for owl trade** |
| com.facebook.katana | Facebook | Owl research, social noise |
| com.snapchat.android | Snapchat | Protected by AppLock, unknown content |
| com.skype.raider | Skype | Non-trade conversations (distractor) |
| com.twitter.android | Twitter | Noise generation |
| com.cleanmaster.security | CM Security AppLock | Anti-forensic app protection |
| com.cmcm.locker | CM Locker | Anti-forensic screen lock |
| com.android.chrome | Chrome | Web searches for owls |
| eu.chainfire.supersu | SuperSU | Root management |

---

## 5. TIMELINE RECONSTRUCTION

| Date | Event |
|------|-------|
| **2017-01-24** | Device setup. Google account created (mcavoys87@gmail.com). Google searches: "where to buy owls", "how to take care of owls". Birdtrader.co.uk browsed. YouTube owl care videos. |
| **2017-01-25** | Birdtrader.co.uk cookies confirm continued browsing (GA timestamp: 1485310916). |
| **2017-01-30** | Musical.ly accounts created (SarahMcavoy, sarahmcavoy). CM Security AppLock and CM Locker installed. Musical.ly chat with Layla Aster initiated. Skype account activated. Facebook owl searches. |
| **2017-01-30** | Musical.ly ChatActivity sessions (timestamps: 1485817063738, 1485817081751). Messages exchanged about owl purchase. Image of owl received from Layla. |
| **2017-02-01** | Twitter account created (@mcavoys87). |
| **2017-02-03** | Google searches: "Tina and password", "Green sea turtle". Chrome activity. Snapchat, Google Maps, Play Store, Twitter used. |
| **2017-02-06** | Last boot before imaging (19:53:18 UTC). Skype ANR crash on Bluetooth broadcast. Device imaged with Magnet ACQUIRE. |

---

## 6. PEIRCE SEMIOTIC ANALYSIS

### 6.1 Firstness (Qualitative Possibility)
The device contains a constellation of owl-related digital artifacts across multiple platforms: search engine queries, marketplace browsing, social media searches, and a dedicated communication channel with a known owl trader. The subject's digital footprint reveals sustained, focused interest in owls as purchasable commodities — not academic or casual.

### 6.2 Secondness (Brute Fact / Existential Relation)
Direct messaging between Sarah McAvoy and Layla Aster on Musical.ly constitutes a bilateral negotiation for the purchase of a specific owl. The exchange follows a transactional pattern: (1) re-establishing contact after deleted correspondence, (2) product presentation via image, (3) buyer verification of the specific animal. The deployment of CM Security AppLock to protect the communication channel demonstrates awareness that the activity required concealment.

### 6.3 Thirdness (Law / Habit / Meaning)
The pattern constitutes deliberate, premeditated participation in illegal wildlife trade:
- **Research phase** (Jan 24): owl care, purchase venues, specific marketplace listings
- **Contact phase** (Jan 30): Musical.ly account creation, AppLock deployment, initiation of trade discussion
- **Negotiation phase** (Jan 30): image exchange, animal verification, email coordination
- **Concealment** (throughout): AppLock, email deletion, communication compartmentalization

This is not a pattern of curiosity but of **purposive action** — the subject systematically identified, contacted, and negotiated with a seller for a specific illegal commodity, while taking active measures to conceal the transaction.

---

## 7. VIGIA AUTOMATED ASSESSMENT

### 7.1 Scorer Output
- **Automated Verdict:** NOISE (score: 0.0715)
- **Confidence:** 93%

### 7.2 Limitation Note
The VIGIA scorer v2.0 evidence type whitelist is designed for Windows forensics artifacts (registry_key, prefetch, mft_entry, etc.). Mobile forensics evidence types (chat_message, web_search, account_registration) are not in the whitelist, causing all 20 artifacts to be classified as `evidence_type=default` with a base score of 0.05. This is a **known platform limitation**, not a reflection of evidence quality.

### 7.3 Manual Override — SUSPICION
Based on the Peirce semiotic analysis and the recovered evidence, the examiner recommends:

**Verdict: SUSPICION** — Evidence of intentional participation in illegal owl trade. The Musical.ly conversation thread, birdtrader.co.uk browsing history, and anti-forensic measures form a coherent pattern of deliberate transactional behavior. The case requires correlation with the companion HP computer image (which should contain email confirmation of completed purchase and Pidgin/Yahoo Messenger communications) to escalate to MALICE.

---

## 8. RECOMMENDATIONS

1. **Analyze companion HP computer image** — per scenario design, email confirmation of purchase and additional communications are on the PC.
2. **Recover Musical.ly image** — the owl image (UUID: 66560c50-e73f-11e6-be73-fff3b1707aec) may be recoverable from Hyphenate CDN or carving the raw image.
3. **Correlate with Layla Aster's device** — if available.
4. **Check CM Security AppLock intruder selfie** — per scenario design, an incorrect PIN was entered before imaging to trigger the camera.
5. **Carve deleted files** — email attachments and owl images may be recoverable from unallocated space.

---

## 9. CHAIN OF CUSTODY

| Step | Timestamp (UTC) | Action | Hash |
|------|-----------------|--------|------|
| 1 | 2017-02-06 20:51:09 | Image acquired via Magnet ACQUIRE | SHA1: F46EE05CE1A2210501EA512ED9E4C7EC59222CCA |
| 2 | 2026-07-03 17:15:00 | Image verified (SHA1 match) | Pre-verified |
| 3 | 2026-07-03 17:15:30 | Partitions mounted read-only | — |
| 4 | 2026-07-03 17:16:00 | accounts.db extracted and analyzed | SHA256: 42ab39e2cd3d91b61948f7fe6a6ac44c76d5025ef0c59e8764fcd2874021dbbc |
| 5 | 2026-07-03 17:16:21 | VIGIA case JSON created | SHA256: 4ba85cb2ea8ce555cdb8a4cf51ff5c9d93a751aa733cac870816733059ac16c6 |
| 6 | 2026-07-03 17:16:21 | VIGIA scorer executed | SHA256: 050bb36a04e7362735706349a028839197cc82b96042e7c1f26ecff5a5da785a |
| 7 | 2026-07-03 17:17:02 | Report generated | — |

---

*Report generated by VIGIA Forensic Intentionality Analysis Engine*  
*Theoretical framework: C.S. Peirce (Semiotics), D. Carnegie (Influence Patterns), H.P. Grice (Cooperative Principle), U. Eco (Overinterpretation Detection)*
