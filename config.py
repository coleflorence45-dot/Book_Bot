# config.py — Vinted Books Bot
# Tuned for Victorian first editions (1860–1898 sweet spot)

# ── TELEGRAM ──────────────────────────────────────────────────────────────────
TELEGRAM_TOKEN   = "8800795670:AAFpgVF-XSGNcuvzHOxHFXsHPdrja07ZDyo"
TELEGRAM_CHAT_ID = "5737361602"

# ── VINTED SESSION COOKIE ─────────────────────────────────────────────────────
VINTED_COOKIE = "v_udt=am1CQldZcTVuU213Znp4R25EVDBySkNSdEsxdS0tZjdTeVFlc0tqNEwyV2dkdC0tanp5dm5sdjNPTEN0eVpwTlNDVWQvUT09; anon_id=91761982-52b2-451b-bf75-13395b91c575; anonymous-locale=en-uk-fr; anonymous-iso-locale=en-GB; non_dot_com_www_domain_cookie_buster=1; is_shipping_fees_applied_info_banner_dismissed=false; v_sid=6a3ec4325c9f5c376e2b7384327927d9; domain_selected=true; OptanonAlertBoxClosed=2026-05-15T09:29:05.236Z; eupubconsent-v2=CQkP0dgQkP0dgAcABBENCfFsAP_gAEPgAAwILNtR_G__bWlr-Tb3abpkeYxP99hr7sQxBgbIkm4FzLvW7JwCx2EZNAzatiIKmRIAu3TBIQNlHIDURUCgKIgFryDMaEyUoTNKJ6BkiBMRI2JQCFxvm4pjWQCY4ur_5kc1mB-N7dr82dzyy4hHn3a5fmS1UJCcIYetDfn8ZBKT-9IEd-x8v4v4_EbpEm8eS1n_pGtp4jc6YlM_dBmxt-TyffzPn_f7k_e7X_vc_n3zv8oXH7rr_4LMgAmGh0QRlkQCBAoCAECABQVhABQIAgAASAogIATBgQ5AwAXWESAEAKAAYIAQAAgwABAAAJAAhEAEABAIAQIBAoAAwAIAgIAGBgADABQiAQAAgOgYpgQQCBYAJEZUBpgQgAJBAS2VCCQBAgrhCkWOAQQIiYKAAAEAAoAAAB8LAQklBKxIIAuILoAEAAAAKIEGBFIWYAgoDNFoKwJOAyNMASPMEiSnQRAEwQkZBkQmqCQeKYogAAAA.f_wACHwAAAAA.ILNtR_G__bXlv-Tb36bpkeYxf99hr7sQxBgbIsm4FzLvW7JwC32EbNEzatiYKmRIAu3TBIQNtHIjURUChKIgVrzDsaEyUoTtKJ-BkiDMRY2JQCFxvm4pjWQCZ4ur_50d9mR-N7dr-2dzyy5hnv3a9fuS1UJicKYetHfn8ZBKT-_IU9_x-_4v4_MbpEm8eS1v_tGtt43c64tP_dpuxt-Tyffzfv_f72_e7X__c__33_-qXX_r7_4A; OTAdditionalConsentString=2~20.43.55.57.61.70.83.89.93.108.117.122.124.135.143.144.147.149.159.161.184.192.196.211.228.230.236.239.255.259.266.272.286.291.311.313.314.320.322.323.327.358.367.370.371.385.407.415.424.429.430.436.445.469.486.491.494.495.522.523.540.550.560.568.574.576.584.587.591.621.723.737.797.798.803.820.827.839.864.899.904.922.938.955.959.979.981.985.986.1003.1027.1031.1033.1046.1047.1048.1051.1053.1067.1092.1095.1097.1099.1107.1109.1126.1135.1143.1149.1152.1162.1166.1186.1188.1192.1205.1215.1220.1226.1227.1230.1252.1268.1270.1276.1284.1290.1301.1307.1312.1329.1342.1345.1356.1365.1403.1415.1416.1419.1421.1423.1440.1449.1455.1495.1512.1514.1516.1525.1540.1548.1555.1558.1570.1577.1579.1583.1584.1598.1603.1616.1638.1651.1653.1659.1660.1667.1677.1678.1682.1697.1699.1703.1712.1716.1720.1721.1725.1732.1735.1745.1750.1753.1765.1782.1786.1800.1808.1810.1825.1827.1832.1838.1840.1843.1845.1859.1870.1878.1880.1882.1889.1898.1911.1917.1928.1929.1942.1944.1958.1962.1963.1964.1967.1968.1969.1978.1985.1987.2003.2027.2035.2038.2039.2044.2047.2052.2056.2064.2068.2069.2072.2074.2084.2088.2090.2103.2107.2109.2115.2124.2130.2133.2135.2137.2140.2141.2147.2156.2166.2177.2186.2205.2213.2216.2219.2220.2222.2223.2224.2225.2227.2234.2251.2253.2271.2275.2279.2282.2295.2299.2309.2312.2316.2322.2325.2328.2331.2335.2336.2343.2354.2358.2359.2370.2373.2376.2377.2400.2403.2405.2406.2410.2411.2414.2415.2416.2418.2425.2427.2440.2447.2453.2461.2465.2468.2472.2477.2484.2486.2488.2498.2506.2510.2517.2526.2527.2531.2532.2534.2535.2542.2552.2559.2564.2567.2568.2569.2571.2572.2575.2577.2579.2583.2584.2589.2595.2596.2604.2605.2608.2609.2610.2612.2614.2621.2624.2627.2628.2629.2633.2636.2642.2643.2645.2646.2650.2651.2652.2656.2657.2658.2660.2661.2669.2670.2677.2681.2684.2686.2687.2689.2690.2695.2698.2713.2714.2729.2739.2767.2768.2770.2772.2778.2784.2787.2791.2792.2798.2801.2805.2812.2813.2814.2816.2817.2821.2822.2824.2827.2830.2831.2832.2833.2834.2838.2839.2844.2846.2849.2850.2852.2854.2860.2862.2863.2865.2867.2869.2872.2874.2875.2878.2880.2881.2882.2884.2886.2887.2888.2889.2891.2893.2894.2895.2897.2898.2900.2901.2908.2909.2916.2917.2918.2920.2922.2923.2927.2929.2930.2931.2940.2941.2947.2949.2950.2956.2958.2961.2963.2964.2965.2966.2968.2970.2972.2973.2974.2975.2979.2980.2981.2983.2985.2986.2987.2994.2995.2997.2999.3000.3001.3002.3003.3005.3008.3009.3010.3012.3016.3017.3018.3019.3023.3028.3031.3034.3038.3043.3051.3052.3053.3055.3058.3059.3063.3066.3070.3073.3074.3075.3076.3077.3089.3090.3093.3094.3095.3097.3099.3100.3106.3107.3109.3112.3117.3119.3126.3127.3128.3130.3133.3135.3136.3137.3145.3149.3150.3151.3153.3155.3163.3165.3167.3169.3172.3173.3177.3182.3183.3184.3185.3186.3187.3188.3189.3190.3194.3196.3200.3201.3209.3210.3211.3213.3214.3215.3217.3218.3222.3223.3225.3226.3227.3228.3230.3231.3233.3234.3235.3236.3237.3238.3240.3244.3245.3250.3251.3253.3254.3257.3260.3266.3270.3272.3281.3286.3288.3289.3290.3292.3293.3296.3299.3300.3306.3307.3309.3314.3315.3316.3318.3323.3324.3328.3330.3331.3531.3631.3731.3831.4131.4331.4531.4631.4731.4831.5231.6931.7131.7235.7831.7931.8931.9731.10231.10631.10831.11031.11531.11631.13431.13632.14034.14133.14237.14332.15731.16831.16931.21233.21731.23031.25131.25931.26031.26631.26831.27731.27831.28031.28332.28731.28831.29631.30331.30532.30732.32531.33931.34231.34631.34731.36831.39131.39531.40632.41131.41531.43631.43731.43831.45931.47232.47531.48131.49231.49332.49431.50831.52831.54231.56831.56931.57131.57231.57531~dv; _gcl_au=1.1.2076337829.1778837429; __ps_r=https://www.google.com/; __ps_lu=https://www.vinted.co.uk/; __ps_did=pscrb_1dd00416-7dd1-4a95-cde6-02d00b73a748; __ps_fva=1778837429468; _ga=GA1.1.640137307.1778837429; _fbp=fb.2.1778837429681.75417560529669780; _pubcid=cf43ab08-88d4-45c2-8fe1-a8b7f031130b; _cc_id=1bfeeaec8cb5015f2fbe940b5f8bd647; __gads=ID=b883b2ed7f618376:T=1778918774:RT=1778918774:S=ALNI_MZ4lgjn55E95XCjU3LVwFUiqGueag; __gpi=UID=0000138e7a0c0c55:T=1778918774:RT=1778918774:S=ALNI_MbVFGR7KXgvAJ2wHQRMWkWO8YUPoQ; __eoi=ID=fd3805eaa42b07ee:T=1778918774:RT=1778918774:S=AA-AfjawYaZpJaLQHQRgvVs94-4_; refresh_token_web=eyJhbGciOiJQUzI1NiIsImtpZCI6IkU1N1lkcnVIcGxBanUyY05vMURvckgzajI3QnU1LXNfT1A1UHdQaWhuNU0ifQ.eyJhcHBfaWQiOjQsImF1ZCI6ImZyLmNvcmUuYXBpLnZpbnRlZC5jb20iLCJjbGllbnRfaWQiOiJ3ZWIiLCJleHAiOjE3Nzk0ODg4NDYsImlhdCI6MTc3OTQ0NTY0NiwiaXNzIjoidmludGVkLWlhbS1zZXJ2aWNlIiwicHVycG9zZSI6InJlZnJlc2giLCJzY29wZSI6InB1YmxpYyIsInNpZCI6IjQ1OTBjYzEyLTE3Nzk0NDU2NDYifQ.GMCcU0t4B52OQFaT2jau-TlkZ3H4ufujLZyX_WbrUZhxcEUQSbiC2UG3g-qSr0otsV5mrprKRFszFXafTEO4VPA_IQ6SsMNvNoip3fJSB0fNpVisWMOTj0ObJJBsgfjt9AiqwlMz70ZA7vMxNP5hXsvLbuYB0ahLN30f-evn8iJPk_hul23lukKRyzCBEiLoJR4ClAqTtVfWujy6cGZidNJGaTWM7W5wm8ijNPsSrqGZz4ay9dNgKcLrsQNnkHmoNohRzExcpH_Ypl8-Sr6Ld_IY3wOjY4QCb-H_h1Eu7slaZC27gDf1AhVcgGD0M-mBfnk2pOJNFZfb6B5NElljnQ; access_token_web=eyJhbGciOiJQUzI1NiIsImtpZCI6IkU1N1lkcnVIcGxBanUyY05vMURvckgzajI3QnU1LXNfT1A1UHdQaWhuNU0ifQ.eyJhcHBfaWQiOjQsImF1ZCI6ImZyLmNvcmUuYXBpLnZpbnRlZC5jb20iLCJjbGllbnRfaWQiOiJ3ZWIiLCJleHAiOjE3Nzk0ODg4NDYsImlhdCI6MTc3OTQ0NTY0NiwiaXNzIjoidmludGVkLWlhbS1zZXJ2aWNlIiwicHVycG9zZSI6ImFjY2VzcyIsInNjb3BlIjoicHVibGljIiwic2lkIjoiNDU5MGNjMTItMTc3OTQ0NTY0NiJ9.yd_KW9CZ7kAJk93g8xuRe8mzcUNZ0MLv1CxcxtIfvfPgsu2j54DJviNipxYuVO8DvVM4qSjur0sk7b27htcYO-Nk_dwwS7wmi_WiUEkLZwIl1TRdniZTWaw5BiKxAuYPu7F9LjhWXwSrYG4JF-VB0TTz4Rxg46fQvkMfItYlxsBjKjV3dwjA_w2m7K6n754QcTGqoZO_Hwa73-GDaUPGaCNkIoj-DY8GoKSpFiVaN22l2RUD4F327mJp8LUt_qixJjfrApjD-gYWbHVVV6vUlpIzvfSq3AzmGzhakVULsX94iGGFprs5M4-vDrqOLYrL0J09lGkXQuRj1QTaiFCBMg; consent_version=eu; panoramaId_expiry=1780050508012; panoramaId=bdcd173b3e73435571569897e70f4945a70287603fc10be2ade5e36af75b91af; panoramaIdType=panoIndiv; viewport_size=977; OptanonConsent=isGpcEnabled=0&datestamp=Fri+May+22+2026+12%3A34%3A56+GMT%2B0100+(British+Summer+Time)&version=202602.1.0&browserGpcFlag=0&isIABGlobal=false&consentId=91761982-52b2-451b-bf75-13395b91c575&isAnonUser=1&hosts=&interactionCount=1&prevHadToken=0&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1%2CC0005%3A1%2CV2STACK42%3A1%2CC0035%3A1%2CC0038%3A1&genVendors=V5%3A1%2CV2%3A1%2CV1%3A1%2C&intType=1&crTime=1778837345403&geolocation=GB%3BENG&AwaitingReconsent=false; cf_clearance=2jxnUZ.HOm50ghVtoi._YTpimK03j54sqvFHYYHrY_s-1779449697-1.2.1.1-ZR1ByB_fJ7sBLDZG7jDsvNa4xeUlLAfQbZk4qBYeawaqMM07RFoF.VkdMGRnGUU81dRiWBfVNIEfj2SOzQGihw5OsnCja0PftYqep3D.mFObGhD_5G9ER79ROjOKFzetP4dFBgtawTfNQi7bu7A_ujVTVGd8VrAEcU1qvUK569swPre.Fqujas.M_FwSheioJze9mAY.p6dCyJWW72.25gStEVTISplA87wjascLD54TFo29TRPG.mELBZzH8xgaCBwzTDqI0qx9hvOzPYANYA9XaRYHMO_LWFIGZbYqNRwJd7O3htxZNpDhOYSqgipTL.fEOhs0AFWUz5aKjE7ynYJlJ1J6X4PNOx9Jkui1TF7xXQG9Ae361l9RhzeYUBHEaG3kyM9VRHbpAsUODXRzOqE9gRjFaSIEkA3mkKJnf2Y; _vinted_fr_session=UEYwNkowMjFneWk5UnB5RUhMdUJxVU5RZ09yS29NMFdIeFgyM0laUWtqc0FuTTVJaVhCekhFeWVyTlUyQXJWVmJBQUpKR3B0WkVCdWVHQnpINWl1cTZMdnNOOGovS0FXVC9DcGc0RjUvejdrOTNsdUwvTDZzWitqVGJ5ZDdXMU1jUnpCOXVQZC9iZ2hQU0ZhZG5IR1d5TWthai95K0N2MkNMUko0YUdFbjlQY3AxOWRQcDVEbHZCSWN2WTJiT05HU2xBQjlCNjZLb1ZQZ0hKSmJPNWgxNmxNVkgweUxmRW10d2V4L0VRN2JWbDFteS9PWldzbmxiSHR3WGxhUVVETi0tendUWmpIOEpuYjFYUnlxSkppWmIyZz09--771a89cc760dfdcca6f939028af5e5ba8dc9713b; __ps_sr=_; __ps_slu=https://www.vinted.co.uk/; _ga_ZJHK1N3D75=GS2.1.s1779449695$o24$g1$t1779449697$j58$l0$h0; _ga_C1K5578GF1=GS2.1.s1779449695$o23$g1$t1779449697$j58$l0$h0; datadome=pab1ZONuNvoPrjGWGDjeebMClp8yzEFDnY~O4reGjsA2JYCg_tGyf~TtYo4jqHL_XiIw9XrC_PASVM9oMCTjbYduHe1VxGt5bIEPgNQgnZbmjM1NNpvp2MgCPUT60FNm; cto_bundle=8f_Iml82VSUyRm1ndG9qdHBoQ2xpQjJqMERTc3ZrRWJpbSUyQkpGWHRESEgzclZnRUQydmMlMkZTUDZBd1N0OXZnTzJ6alZUQyUyQmVDbDdUY0xxRXVIVlYlMkZlNEhsQ3pRZHhCSW4lMkJRanp3bFlYRmdVVmFEJTJCTjB2OW9reFJYMEZUTU0yYXc3NTllTDcxbFdQN2tJanMxNG9oYktlNno1WXBUUSUzRCUzRA; __cf_bm=pTMMCh74P3LXk4b5yxiumBu0KeztAHRMYXO_lqnGPNE-1779450963.6980178-1.0.1.1-EXdfpDaLo5n1zmeAGuMY9iG5UJXXM3R2ESyuZu59Kue2AF2V1Cbe57S2XEsE8Bcdj4.W9UXgxcKkgM8_xkc2O.tUaiB0JdRd.YzqZDlZQTeGeF8fdY2hPyOB4uLHZdl8mVEOGnhBIFgGsi_tLO28vA"

# ── ANTHROPIC API KEY (image analysis) ───────────────────────────────────────
ANTHROPIC_API_KEY = "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"

# ── POLLING INTERVAL ──────────────────────────────────────────────────────────
CHECK_INTERVAL_MINUTES_MIN = 25
CHECK_INTERVAL_MINUTES_MAX = 40

# ── SEARCH KEYWORDS ───────────────────────────────────────────────────────────
SEARCH_KEYWORDS = [
    # Broadest vague listings — catches the most uninformed sellers
    "old book",
    "old books",
    "old hardback",
    "vintage book",
    "vintage hardback",
    "antique book",

    # Physical descriptions — seller describing what they see
    "leather bound book",
    "old illustrated book",
    "gilt book",
    "decorative book",

    # House clearance — highest unawareness signal, best flip source
    "house clearance books",
    "job lot books",
    "old book bundle",

    # Publisher-based searches — "john murray" proven to find genuine Victorian books
    # Other publisher names removed: cassell sons → returns pottery, sampson low →
    # returns Puma trainers, richard bentley → returns cars, frederick warne →
    # returns 90%+ modern Peter Rabbit merchandise
    "john murray",
]

# ── PRICE RANGE (£) ───────────────────────────────────────────────────────────
MIN_PRICE =  1.00
MAX_PRICE = 20.00

# ── MINIMUM SCORE TO TRIGGER AN ALERT ─────────────────────────────────────────
MIN_SCORE = 6

# ── CONDITIONS TO ACCEPT ──────────────────────────────────────────────────────
GOOD_CONDITIONS = [
    "new with tags",
    "new without tags",
    "very good",
    "good",
    "satisfactory",
]

# ── PUBLISHER TIERS ───────────────────────────────────────────────────────────
# Tier 1 publishers score +3 — the most prestigious Victorian imprints.
# Their name alone on a spine adds significant collector value.
# All other publishers in PUBLISHER_SIGNALS score +2 as before.
PUBLISHER_TIER_1 = [
    "john murray",       # Darwin, Byron, Livingstone, Austen
    "macmillan",         # Tennyson, Hardy, Carroll (via Macmillan)
    "chapman & hall",    # Dickens's primary publisher
    "chapman hall",
    "smith elder",       # Brontës, Thackeray, Browning
    "blackwood",         # George Eliot, Conrad, Stevenson
    "kegan paul",        # Strong on science, travel, philosophy
]

# ── GREEN FLAG PUBLISHERS ─────────────────────────────────────────────────────
# Each match scores +2 (or +3 if in PUBLISHER_TIER_1 above).
PUBLISHER_SIGNALS = [
    "john murray",
    "george routledge",
    "routledge",
    "macmillan",
    "longmans green",
    "longmans",
    "cassell",
    "cassell & co",
    "cassell sons",
    "chapman & hall",
    "chapman hall",
    "frederick warne",     # full name only — "warne" alone too ambiguous
    "sampson low",
    "isbister",
    "isbister & co",
    "richard bentley",     # full name only — "bentley" alone matches the car brand
    "smith elder",
    "blackwood",
    "kegan paul",
    "trübner",
    "w h allen",
    "edward arnold",
    "methuen",
    "heinemann",
    "o'donoghue",
    "bradbury agnew",
    "henry holt",
    "harper brothers",
    "routledge sons",
]

# ── AUTHOR WHITELIST ──────────────────────────────────────────────────────────
# Victorian and Edwardian authors whose work commands strong resale prices.
# Any match scores +3. First match wins — points awarded once per listing.
# Use the most distinctive form of the name to avoid false positives.
AUTHOR_WHITELIST = [
    # Major Victorian novelists
    "charles dickens", "dickens",
    "thomas hardy",
    "george eliot",
    "anthony trollope", "trollope",
    "wilkie collins",
    "elizabeth gaskell", "gaskell",
    "charlotte brontë", "emily brontë", "anne brontë",
    "charlotte bronte", "emily bronte", "anne bronte", "brontë", "bronte",
    "william makepeace thackeray", "thackeray",
    "george meredith",
    "george gissing",
    "benjamin disraeli",
    "george borrow",
    # Adventure / genre fiction
    "robert louis stevenson",
    "rudyard kipling", "kipling",
    "h rider haggard", "rider haggard",
    "arthur conan doyle", "conan doyle",
    "h g wells", "h.g. wells",
    "lewis carroll",
    "andrew lang",
    # Poets
    "alfred tennyson", "lord tennyson",
    "robert browning",
    "elizabeth barrett browning",
    "algernon swinburne", "swinburne",
    "dante gabriel rossetti", "rossetti",
    "matthew arnold",
    "edward lear",
    "william morris",
    "walter pater",
    "oscar wilde",
    # Science / Natural History
    "charles darwin", "darwin",
    "alfred russel wallace",
    "philip henry gosse", "philip gosse",
    "henry walter bates",
    "william yarrell",
    "richard south",
    "st george mivart",
    "frank buckland",
    # Exploration & Travel
    "david livingstone", "livingstone",
    "henry morton stanley",
    "richard francis burton",
    "samuel baker",
    "john hanning speke",
    "frederick selous",
    # Critics / Essayists
    "john ruskin", "ruskin",
    "thomas carlyle", "carlyle",
    "john henry newman", "cardinal newman",
    "john stuart mill",
    # Occult / Esoteric
    "madame blavatsky", "blavatsky",
    "edward bulwer-lytton", "bulwer lytton", "bulwer-lytton",
    "aleister crowley",
]

# ── PHYSICAL DESCRIPTOR SIGNALS ───────────────────────────────────────────────
# Binding and physical condition terms used by knowledgeable sellers.
# Each appearance scores +2 — these indicate a seller who has actually
# examined the book and knows what they're describing.
# Capped at 2 matches to avoid stacking.
PHYSICAL_DESCRIPTOR_SIGNALS = [
    "bevelled boards",
    "beveled boards",
    "raised bands",          # leather binding feature on spine
    "original cloth",        # original publisher's binding, not rebound
    "original binding",
    "publishers cloth",
    "publisher's cloth",
    "tight copy",            # binding intact, no sag or lean
    "tight and clean",
    "square and tight",
    "clean and tight",
    "fore-edge painting",    # rare decorative feature, significant value
    "foredge painting",
    "fore edge painting",
    "uncut pages",           # book never read — pages still joined at edges
    "unopened pages",
    "unopened copy",
    "deckle edges",          # handmade paper edge, adds period authenticity
    "vellum binding",
    "contemporary binding",  # bound at time of publication
    "original wrappers",     # paperback original — very rare survival
]

# ── EDITION & AGE SIGNALS ─────────────────────────────────────────────────────
AGE_SIGNALS = [
    "first edition",
    "1st edition",
    "first printing",
    "1st printing",
    "first published",
    "victorian",
    "antique",
    "vintage",
    "rare",
    "scarce",
    "out of print",
    "collectible",
    "collectable",
    "cloth boards",
    "original boards",
    "gilt",
    "gilt lettering",
    "gilt edges",
    "gilt decoration",
    "decorative spine",
    "leather bound",
    "half leather",
    "quarter bound",
    "marbled",
    "vellum",
    "morocco",
    "illustrated",
    "plates",
    "engravings",
    "lithographs",
    "woodcuts",
    "chromolithograph",
    "tight spine",
    "intact boards",
    "clean pages",
    "presentation copy",
    "gift inscription",
    "inscribed",
    "signed",
    "named copy",
    "provenance",
    "bookplate",
    "armorial",
    "limited edition",
    "privately printed",
    "folio society",
    "oxford",
    "cambridge university press",
]

# ── MASSIVE BONUS ILLUSTRATION SIGNALS ───────────────────────────────────────
ILLUSTRATION_BONUS_SIGNALS = [
    "colour plates",
    "colored plates",
    "coloured plates",
    "colour illustrations",
    "hand coloured",
    "hand colored",
    "chromolithograph",
    "fold out map",
    "folding map",
    "fold-out map",
    "foldout map",
    "folding plate",
    "fold-out plate",
    "named illustrator",
    "all plates present",
    "complete plates",
]

# ── AESTHETIC BONUS SIGNALS ───────────────────────────────────────────────────
AESTHETIC_BONUS_SIGNALS = [
    "gilt cover",
    "gilt covers",
    "gilt boards",
    "gilt decorated",
    "gilt decoration",
    "gilt lettering",
    "gilt spine",
    "gilt edges",
    "gilt page edges",
    "all edges gilt",
    "top edge gilt",
    "heavily gilt",
    "rich gilt",
    "pictorial cover",
    "pictorial boards",
    "decorative cover",
    "decorative boards",
    "illustrated cover",
    "illustrated boards",
    "embossed cover",
    "embossed boards",
    "relief decoration",
    "art nouveau",
    "arts and crafts",
    "pre-raphaelite",
    "aesthetic movement",
    "decorative binding",
    "ornate binding",
    "elaborate binding",
    "stunning binding",
    "beautiful binding",
    "attractive binding",
    "striking cover",
    "gorgeous cover",
    "decorative cloth",
    "ornate cloth",
    "richly decorated",
    "highly decorative",
    "red cloth",
    "blue cloth",
    "green cloth",
    "purple cloth",
    "olive cloth",
    "crimson cloth",
    "navy cloth",
    "coloured cloth",
    "colored cloth",
    "marbled boards",
    "marbled endpapers",
    "marbled edges",
    "sprinkled edges",
    "tree calf",
    "tree marbled",
    "dark academia",
    "cottagecore",
    "aesthetic book",
    "display book",
    "shelf decor",
    "shelf decoration",
    "beautiful book",
    "stunning book",
    "gorgeous book",
]

YEAR_SWEET_SPOT_START = 1800
YEAR_SWEET_SPOT_END   = 1898
VALUABLE_BEFORE_YEAR  = 1900
YEAR_RANGE_START      = 1800

# ── TARGET GENRES ─────────────────────────────────────────────────────────────
TARGET_GENRE_SIGNALS = [
    "natural history", "ornithology", "botany", "flora", "fauna",
    "zoology", "entomology", "geology", "conchology", "ichthyology",
    "fungi", "lichens", "mosses", "ferns", "wildflowers",
    "astronomy", "celestial", "stellar", "telescope", "atlas of the heavens",
    "star atlas", "natural philosophy", "optics",
    "voyage", "voyages", "exploration", "expedition", "travels in",
    "journey to", "african", "arctic", "antarctic", "himalaya",
    "nile", "amazon", "pacific", "terra incognita",
    "occult", "alchemy", "alchemical", "magic", "magical",
    "witchcraft", "demonology", "kabbalah", "cabala", "hermetic",
    "rosicrucian", "freemasonry", "theosophy", "spiritualism",
    "astrology", "divination", "esoteric", "mysticism", "mystical",
    "folklore", "folk lore", "superstition",
]

# ── PRIORITY GENRES ───────────────────────────────────────────────────────────
PRIORITY_GENRE_ASTRONOMY = [
    "astronomy", "celestial", "stellar", "telescope",
    "atlas of the heavens", "star atlas", "natural philosophy",
    "optics", "astronomer", "astronomical",
]

PRIORITY_GENRE_NATURAL_HISTORY = [
    "natural history", "ornithology", "botany", "flora", "fauna",
    "zoology", "entomology", "geology", "conchology", "ichthyology",
    "naturalist", "naturalists", "species", "birds", "bird",
    "insects", "insect", "botanical", "wildlife",
]

PRIORITY_GENRE_OCCULT = [
    "occult", "alchemy", "alchemical", "magic", "magical",
    "witchcraft", "witches", "sorcery", "sorcerer",
    "demonology", "kabbalah", "cabala", "hermetic", "hermeticism",
    "rosicrucian", "freemasonry", "freemason", "theosophy",
    "divination", "esoteric", "mysticism", "mystical",
    "folklore", "folk lore", "superstition",
    "supernatural", "paranormal", "apparitions", "apparition",
    "ghost", "ghosts", "haunted", "haunting", "spectre", "spectres",
    "phantoms", "phantom", "spirit world", "spirit manifestation",
    "second sight", "clairvoyance", "mesmerism", "magnetism",
    "spiritualism", "spiritualist", "medium", "séance", "seance",
    "table turning", "automatic writing", "psychical research",
    "society for psychical research", "telepathy", "thought transference",
    "astrology", "astrological", "horoscope",
    "prophecy", "prophetic", "oracle", "augury",
    "black magic", "white magic", "witchery",
    "necromancy", "necromancer",
]

# ── RED FLAGS — HARD WALK AWAY ────────────────────────────────────────────────
BAD_TITLE_KEYWORDS = [
    "ex library",
    "ex-library",
    "ex libris",
    "library stamp",
    "library stamps",
    "library sticker",
    "library plate",
    "shelf number",
    "shelf mark",
    "detached boards",
    "boards detached",
    "board detached",
    "missing plates",
    "plates missing",
    "plates removed",
    "single volume",
    "volume only",
    "part of set",
    "incomplete set",
    "heavy foxing",
    "foxing throughout",
    "heavily foxed",
    "cracked gutter",
    "cracked gutters",
    "gutters cracked",
    "spine split",
    "spine broken",
    "broken spine",
    "pages loose",
    "loose pages",
    "water damage",
    "water stain",
    "water stained",
    "mould",
    "mold",
    "mildew",
    "torn pages",
    "missing pages",
    "pages missing",
    "writing throughout",
    "heavily annotated",
    "falling apart",
    "poor condition",
    "not readable",
    "reproduction",
    "facsimile",
    "reprint",
    "modern reprint",
    "fascimile",
    # ── Modern / non-Victorian topics ─────────────────────────────────────────
    # These phrases almost never appear on genuine Victorian books.
    # -2 penalty each — knocks clearly modern books below MIN_SCORE.
    "sleep training",
    "baby sleep",
    "gentle sleep",
    "mindfulness",
    "self-help",
    "coloring book",
    "colouring book",
    "activity book",
    "puzzle book",
    "quiz book",
    "adult colouring",
    "adult coloring",
    "affirmations",
    "gratitude journal",
    "bullet journal",
    "fitness journal",
    "wellness journal",
]

# ── POST-1900 HARD BLOCK ──────────────────────────────────────────────────────
HARD_BLOCK_AFTER_YEAR = 1900
HARD_BLOCK_AFTER_YEAR_PRIORITY = 1910