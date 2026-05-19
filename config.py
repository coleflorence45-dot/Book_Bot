# config.py — Vinted Books Bot
# Tuned for Victorian first editions (1860–1898 sweet spot)

# ── TELEGRAM ──────────────────────────────────────────────────────────────────
TELEGRAM_TOKEN   = "8800795670:AAFpgVF-XSGNcuvzHOxHFXsHPdrja07ZDyo"
TELEGRAM_CHAT_ID = "5737361602"

# ── VINTED SESSION COOKIE ─────────────────────────────────────────────────────
VINTED_COOKIE = "v_udt=am1CQldZcTVuU213Znp4R25EVDBySkNSdEsxdS0tZjdTeVFlc0tqNEwyV2dkdC0tanp5dm5sdjNPTEN0eVpwTlNDVWQvUT09; anon_id=91761982-52b2-451b-bf75-13395b91c575; anonymous-locale=en-uk-fr; anonymous-iso-locale=en-GB; non_dot_com_www_domain_cookie_buster=1; consent_version=us-ca; is_shipping_fees_applied_info_banner_dismissed=false; v_sid=6a3ec4325c9f5c376e2b7384327927d9; domain_selected=true; OptanonAlertBoxClosed=2026-05-15T09:29:05.236Z; eupubconsent-v2=CQkP0dgQkP0dgAcABBENCfFsAP_gAEPgAAwILNtR_G__bWlr-Tb3abpkeYxP99hr7sQxBgbIkm4FzLvW7JwCx2EZNAzatiIKmRIAu3TBIQNlHIDURUCgKIgFryDMaEyUoTNKJ6BkiBMRI2JQCFxvm4pjWQCY4ur_5kc1mB-N7dr82dzyy4hHn3a5fmS1UJCcIYetDfn8ZBKT-9IEd-x8v4v4_EbpEm8eS1n_pGtp4jc6YlM_dBmxt-TyffzPn_f7k_e7X_vc_n3zv8oXH7rr_4LMgAmGh0QRlkQCBAoCAECABQVhABQIAgAASAogIATBgQ5AwAXWESAEAKAAYIAQAAgwABAAAJAAhEAEABAIAQIBAoAAwAIAgIAGBgADABQiAQAAgOgYpgQQCBYAJEZUBpgQgAJBAS2VCCQBAgrhCkWOAQQIiYKAAAEAAoAAAB8LAQklBKxIIAuILoAEAAAAKIEGBFIWYAgoDNFoKwJOAyNMASPMEiSnQRAEwQkZBkQmqCQeKYogAAAA.f_wACHwAAAAA.ILNtR_G__bXlv-Tb36bpkeYxf99hr7sQxBgbIsm4FzLvW7JwC32EbNEzatiYKmRIAu3TBIQNtHIjURUChKIgVrzDsaEyUoTtKJ-BkiDMRY2JQCFxvm4pjWQCZ4ur_50d9mR-N7dr-2dzyy5hnv3a9fuS1UJicKYetHfn8ZBKT-_IU9_x-_4v4_MbpEm8eS1v_tGtt43c64tP_dpuxt-Tyffzfv_f72_e7X__c__33_-qXX_r7_4A; OTAdditionalConsentString=2~20.43.55.57.61.70.83.89.93.108.117.122.124.135.143.144.147.149.159.161.184.192.196.211.228.230.236.239.255.259.266.272.286.291.311.313.314.320.322.323.327.358.367.370.371.385.407.415.424.429.430.436.445.469.486.491.494.495.522.523.540.550.560.568.574.576.584.587.591.621.723.737.797.798.803.820.827.839.864.899.904.922.938.955.959.979.981.985.986.1003.1027.1031.1033.1046.1047.1048.1051.1053.1067.1092.1095.1097.1099.1107.1109.1126.1135.1143.1149.1152.1162.1166.1186.1188.1192.1205.1215.1220.1226.1227.1230.1252.1268.1270.1276.1284.1290.1301.1307.1312.1329.1342.1345.1356.1365.1403.1415.1416.1419.1421.1423.1440.1449.1455.1495.1512.1514.1516.1525.1540.1548.1555.1558.1570.1577.1579.1583.1584.1598.1603.1616.1638.1651.1653.1659.1660.1667.1677.1678.1682.1697.1699.1703.1712.1716.1720.1721.1725.1732.1735.1745.1750.1753.1765.1782.1786.1800.1808.1810.1825.1827.1832.1838.1840.1843.1845.1859.1870.1878.1880.1882.1889.1898.1911.1917.1928.1929.1942.1944.1958.1962.1963.1964.1967.1968.1969.1978.1985.1987.2003.2027.2035.2038.2039.2044.2047.2052.2056.2064.2068.2069.2072.2074.2084.2088.2090.2103.2107.2109.2115.2124.2130.2133.2135.2137.2140.2141.2147.2156.2166.2177.2186.2205.2213.2216.2219.2220.2222.2223.2224.2225.2227.2234.2251.2253.2271.2275.2279.2282.2295.2299.2309.2312.2316.2322.2325.2328.2331.2335.2336.2343.2354.2358.2359.2370.2373.2376.2377.2400.2403.2405.2406.2410.2411.2414.2415.2416.2418.2425.2427.2440.2447.2453.2461.2465.2468.2472.2477.2484.2486.2488.2498.2506.2510.2517.2526.2527.2531.2532.2534.2535.2542.2552.2559.2564.2567.2568.2569.2571.2572.2575.2577.2579.2583.2584.2589.2595.2596.2604.2605.2608.2609.2610.2612.2614.2621.2624.2627.2628.2629.2633.2636.2642.2643.2645.2646.2650.2651.2652.2656.2657.2658.2660.2661.2669.2670.2677.2681.2684.2686.2687.2689.2690.2695.2698.2713.2714.2729.2739.2767.2768.2770.2772.2778.2784.2787.2791.2792.2798.2801.2805.2812.2813.2814.2816.2817.2821.2822.2824.2827.2830.2831.2832.2833.2834.2838.2839.2844.2846.2849.2850.2852.2854.2860.2862.2863.2865.2867.2869.2872.2874.2875.2878.2880.2881.2882.2884.2886.2887.2888.2889.2891.2893.2894.2895.2897.2898.2900.2901.2908.2909.2916.2917.2918.2920.2922.2923.2927.2929.2930.2931.2940.2941.2947.2949.2950.2956.2958.2961.2963.2964.2965.2966.2968.2970.2972.2973.2974.2975.2979.2980.2981.2983.2985.2986.2987.2994.2995.2997.2999.3000.3001.3002.3003.3005.3008.3009.3010.3012.3016.3017.3018.3019.3023.3028.3031.3034.3038.3043.3051.3052.3053.3055.3058.3059.3063.3066.3070.3073.3074.3075.3076.3077.3089.3090.3093.3094.3095.3097.3099.3100.3106.3107.3109.3112.3117.3119.3126.3127.3128.3130.3133.3135.3136.3137.3145.3149.3150.3151.3153.3155.3163.3165.3167.3169.3172.3173.3177.3182.3183.3184.3185.3186.3187.3188.3189.3190.3194.3196.3200.3201.3209.3210.3211.3213.3214.3215.3217.3218.3222.3223.3225.3226.3227.3228.3230.3231.3233.3234.3235.3236.3237.3238.3240.3244.3245.3250.3251.3253.3254.3257.3260.3266.3270.3272.3281.3286.3288.3289.3290.3292.3293.3296.3299.3300.3306.3307.3309.3314.3315.3316.3318.3323.3324.3328.3330.3331.3531.3631.3731.3831.4131.4331.4531.4631.4731.4831.5231.6931.7131.7235.7831.7931.8931.9731.10231.10631.10831.11031.11531.11631.13431.13632.14034.14133.14237.14332.15731.16831.16931.21233.21731.23031.25131.25931.26031.26631.26831.27731.27831.28031.28332.28731.28831.29631.30331.30532.30732.32531.33931.34231.34631.34731.36831.39131.39531.40632.41131.41531.43631.43731.43831.45931.47232.47531.48131.49231.49332.49431.50831.52831.54231.56831.56931.57131.57231.57531~dv; _gcl_au=1.1.2076337829.1778837429; __ps_r=https://www.google.com/; __ps_lu=https://www.vinted.co.uk/; __ps_did=pscrb_1dd00416-7dd1-4a95-cde6-02d00b73a748; __ps_fva=1778837429468; _ga=GA1.1.640137307.1778837429; _fbp=fb.2.1778837429681.75417560529669780; _pubcid=cf43ab08-88d4-45c2-8fe1-a8b7f031130b; _cc_id=1bfeeaec8cb5015f2fbe940b5f8bd647; panoramaId_expiry=1779442290017; panoramaId=76c5116cf82e9ff91d71b2a35b184945a70274d096752011c2f636ac71eb43b5; panoramaIdType=panoIndiv; __gads=ID=b883b2ed7f618376:T=1778918774:RT=1778918774:S=ALNI_MZ4lgjn55E95XCjU3LVwFUiqGueag; __gpi=UID=0000138e7a0c0c55:T=1778918774:RT=1778918774:S=ALNI_MbVFGR7KXgvAJ2wHQRMWkWO8YUPoQ; __eoi=ID=fd3805eaa42b07ee:T=1778918774:RT=1778918774:S=AA-AfjawYaZpJaLQHQRgvVs94-4_; refresh_token_web=eyJhbGciOiJQUzI1NiIsImtpZCI6IkU1N1lkcnVIcGxBanUyY05vMURvckgzajI3QnU1LXNfT1A1UHdQaWhuNU0ifQ.eyJhcHBfaWQiOjQsImF1ZCI6ImZyLmNvcmUuYXBpLnZpbnRlZC5jb20iLCJjbGllbnRfaWQiOiJ3ZWIiLCJleHAiOjE3NzkyMzc4NzksImlhdCI6MTc3OTE5NDY3OSwiaXNzIjoidmludGVkLWlhbS1zZXJ2aWNlIiwicHVycG9zZSI6InJlZnJlc2giLCJzY29wZSI6InB1YmxpYyIsInNpZCI6ImFmNDIyYTFkLTE3NzkxOTQ2NzkifQ.FsodjRkOLu8Icg8IVu0fLfC9utEzTArSz-i8tiWTPie1cJBxBjE6N87NABk9hn3mm_3p2o1c8TFrwiBv45ir5uW3M4WZP6D0-tn1Xaeg-veq3vdt8wY8WsQ-Ohoz2HVojAs6y7ah9haOHJSuanOftKQb94qDt78nafvTHUqJKIuJzPOxbszkI4G1WG3RQt2CCGAqLamR-c7uRkv9TM74ODYjYCWhF_HDrWyu3Yq5l-U7P6CeIuuxtnpi7rQuhIU8lIXZXhBe3o5BwpnT6e0-R4P0kci9eaFYrCW6I4gyVBeNOjpZtYI6dk6M3NArC0-CFmPEL40euP6XFySoBrLaEw; access_token_web=eyJhbGciOiJQUzI1NiIsImtpZCI6IkU1N1lkcnVIcGxBanUyY05vMURvckgzajI3QnU1LXNfT1A1UHdQaWhuNU0ifQ.eyJhcHBfaWQiOjQsImF1ZCI6ImZyLmNvcmUuYXBpLnZpbnRlZC5jb20iLCJjbGllbnRfaWQiOiJ3ZWIiLCJleHAiOjE3NzkyMzc4NzksImlhdCI6MTc3OTE5NDY3OSwiaXNzIjoidmludGVkLWlhbS1zZXJ2aWNlIiwicHVycG9zZSI6ImFjY2VzcyIsInNjb3BlIjoicHVibGljIiwic2lkIjoiYWY0MjJhMWQtMTc3OTE5NDY3OSJ9.w8zHwmIZokt2Aap92BlfQX6MQQh7bSN_LzKWKf-iiiT1BPv3p613mi3AoHZOJ82UFR3jQP4UfPqzhhC3ZRxbYzLoMXuosFRVArS-CuGyaWQyRRxj3EtcOpH5ZqhIgreuOdFUUP55-Tw2JY8fD1ItVxD_XCmD2qCXphKDmRNSuS-H113SnJiI24QLV58sUDOpsInSE9GVKyri30Lho-tQZTIwGx90Ek4r01aIaU90yMhfpi-lwLN6W6spjsrvuY-e6xbzz5-EwQrPf76UPayLNg0PvlIJvjO-n3-nkrdLACaTkqDZsaOX1io7Plc8LOrP_C0UgVjkrHPDSqZROCWHlw; __ps_sr=_; __ps_slu=https://www.vinted.co.uk/; OptanonConsent=isGpcEnabled=0&datestamp=Wed+May+20+2026+00%3A00%3A45+GMT%2B0100+(British+Summer+Time)&version=202602.1.0&browserGpcFlag=0&isIABGlobal=false&consentId=91761982-52b2-451b-bf75-13395b91c575&isAnonUser=1&hosts=&interactionCount=1&prevHadToken=0&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1%2CC0005%3A1%2CV2STACK42%3A1%2CC0035%3A1%2CC0038%3A1&genVendors=V5%3A1%2CV2%3A1%2CV1%3A1%2C&intType=1&crTime=1778837345403&geolocation=GB%3BENG&AwaitingReconsent=false; cf_clearance=Fy_D5UeOTp_6RbN2Adps1gwoaoC3xw53omhrAuWu_CM-1779231645-1.2.1.1-Sh.RAisSG4qApUyPT9urr4B3Ej7nh7QduCET.JCZLjmY6cnmpzKysHqlqRabYINnLBrF1GKiLfbHHRgwvJl6DBj2YZxTsFPxSTxVV7_Me.NB.689UMvfTGMQx_H1W5Rsy1mXPeg.OxdS8_FzcTHOHATK5QliN_UK2478A2G376dTFbQFnUNt1ReWOOeyP8VLaciM.AAVmoJq7zPEYZEPVh2tPYuK_B1Bb1LwhsCs19muID01U02zIWD9tHotPkAx.7jEKXMhlIaDfgNxPnbYASQqwaKpBDeQAPTZhO4gGISEhsyIkLPpSV8shwIxIuOlGcpYcNXSUt9ngJDSmS7JQKhSV6_U4dX6v6CnuYWfkGZqzrg42V.u_Dg.eWNvgHPEGUh.nxRXFtothTo11jMOUw6ZHUC798Uc3lBpX7tP6SY; __cf_bm=NzmCkEnQ9bXYL2o_mjKjwcIelgyYZ3jL9vExLHlI9bY-1779231645.6596467-1.0.1.1-_myD07CNoUU014z6QdQefOK4ecB4djxVUPkRWHFsapFeF1BBxyuuSoJ.XSdM3NwY4yWBw5v6ttbkNfRLPxQJwsLhQa_tbn71WJCgFMKoPGBCzWz4YWZP3GQFMlRjfRNL3DSZ6bYCYl.OmnMI4_msbQ; banners_ui_state=SUCCESS; _vinted_fr_session=RHBKRHEvMm02RWxldjhFSkRGOU5LQlVMaEJOVCt5Ukt3SUZVTkprNDNNTm9nS2N6dFhZems2aWpPTGszc3Jpa0dBRVZ0YUlKT0VmVXh3MGtsZVNxLzFxRzNaZ2E3ZHBPY2NhRHhra1VmZlV0OU85a2grQnlKcFVCcGMyOFVrMVpsbXdPUFBkMXQ3ZTZxbld1bkl0VVljOC9NYjlRQ3Z1dmZKTEN5aXZMMzNrZGdHRFJCdDY2N1lyVmh2ekdKMXFYRm1vdjBSSFVSUTVjb0ZPbFNWalp4WWNsaGJyRFUraFIwRzdQaVh4K3FvNG9rQUFOL0RsNHRRYmRuZmhxaVdlYi0tSWUrTmg1NFFtaHJQME1hSWgrVlB3Zz09--1d0c9e8dac27c4e6876a78c389f30241507628f5; cto_bundle=hOvUO182VSUyRm1ndG9qdHBoQ2xpQjJqMERTc3JzN0ZremtiVXElMkJtRCUyQkFxU2xwQ2dBZXR6dSUyRmdPJTJGJTJGMmtVaEc1JTJCMlI2anNRZ21iOHQxY0FJaUZ1SGVqUlpBOVJPV1pReERBMG15Y3p4YjdBdU9hSjhlQjZqdmRER05yQzl4cFdXMG4wa0FKJTJGTDFvbzFBJTJCRFhzZUxSdHJOMjNUWnclM0QlM0Q; _ga_C1K5578GF1=GS2.1.s1779230022$o11$g1$t1779231645$j59$l0$h0; _ga_ZJHK1N3D75=GS2.1.s1779230022$o12$g1$t1779231645$j59$l0$h0; datadome=jxmRzAhZyj9q6wplVlA4VyFeP2PjZj6xvxzIqoAxmCs_3mqitaeLsTk_0DnDq4wmNxDDFtFqis~Rjlb4AU3xXPXwtHO78PP6mJR9j95Hzn1v2quq8Y9K_LxKXGG11VIF; viewport_size=977"

# ── ANTHROPIC API KEY (image analysis) ───────────────────────────────────────
ANTHROPIC_API_KEY = "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"

# ── POLLING INTERVAL ──────────────────────────────────────────────────────────
CHECK_INTERVAL_MINUTES = 3

# ── SEARCH KEYWORDS ───────────────────────────────────────────────────────────
# Cast wide across the genres and publishers that keep paying off.
# The scorer and image analyser filter the noise — keyword volume is fine.
SEARCH_KEYWORDS = [

    # Genre — Natural History (strong consistent performer)
    "natural history book antique",
    "Victorian natural history",
    "illustrated natural history",
    "birds illustrated antique book",
    "botany illustrated Victorian",
    "zoology antique book",
    "entomology Victorian book",

    # Genre — Astronomy & Science
    "astronomy antique book",
    "Victorian astronomy",
    "illustrated astronomy book",
    "celestial atlas antique",
    "science Victorian illustrated",

    # Genre — Exploration & Voyages
    "exploration voyage antique book",
    "Victorian travel book",
    "illustrated voyage book",
    "African exploration book antique",
    "Arctic expedition book",
    "expedition illustrated Victorian",

    # Genre — Occult, Magic, Alchemy (undervalued, high flip potential)
    "occult book antique",
    "alchemy book old",
    "Victorian magic book",
    "witchcraft antique book",
    "esoteric Victorian book",
    "mysticism illustrated old book",
    "spiritualism Victorian",

    # Genre — General Victorian (catch-all for the right era)
    "Victorian first edition book",
    "antique cloth board book",
    "gilt Victorian book",
    "Victorian illustrated hardback",
    "decorative Victorian book",
    "old leather bound book",

    # Publisher-specific searches (Vinted sellers often list publisher)
    "John Murray antique book",
    "Macmillan Victorian book",
    "Chapman Hall antique",
    "Cassell Victorian book",
    "Longmans antique book",
    "Frederick Warne antique",
    "George Routledge antique",

    # Physical feature searches
    "colour plates antique book",
    "fold out map antique book",
    "first edition 1800s book",
    "antique book illustrated plates",
    "Victorian hardback illustrated",
]

# ── PRICE RANGE (£) ───────────────────────────────────────────────────────────
# Upper limit is generous — a seller listing a £200 book at £35 is still a flip.
# Raise MAX_PRICE further if you keep finding undervalued copies above £30.
MIN_PRICE =  1.00
MAX_PRICE = 20.00

# ── MINIMUM SCORE TO TRIGGER AN ALERT ─────────────────────────────────────────
# With this specificity of scoring, 3 is a reliable floor.
# Lower to 2 if you feel you're missing finds; raise to 4 to cut noise.
MIN_SCORE = 3

# ── CONDITIONS TO ACCEPT ──────────────────────────────────────────────────────
# "satisfactory" included — Victorian books in honest "satisfactory" condition
# are often still very sellable; assess via image.
GOOD_CONDITIONS = [
    "new with tags",
    "new without tags",
    "very good",
    "good",
    "satisfactory",
]

# ── GREEN FLAG PUBLISHERS ─────────────────────────────────────────────────────
# Each match scores +2. These houses published the collectible Victorian titles.
# Sound logic additions (★): other high-value Victorian imprints worth watching.
PUBLISHER_SIGNALS = [
    # Your confirmed performers
    "john murray",
    "george routledge",
    "routledge",
    "macmillan",
    "longmans green",
    "longmans",
    "cassell",
    "cassell & co",
    "chapman & hall",
    "chapman hall",
    "frederick warne",
    "warne",
    "sampson low",
    "isbister",
    "isbister & co",
    "richard bentley",
    "bentley",

    # ★ Sound logic additions — well-documented high-value Victorian imprints
    "smith elder",           # published Brontës, Thackeray
    "blackwood",             # William Blackwood — George Eliot, Conrad
    "kegan paul",            # strong on science and travel
    "trübner",               # Trübner & Co — academic, scarce
    "w h allen",
    "edward arnold",
    "methuen",               # late Victorian, many illustrated firsts
    "heinemann",             # 1890s onward, lots of illustrated fiction
    "o'donoghue",
    "bradbury agnew",        # Punch publishers — illustrated humour
    "henry holt",            # US imprint that co-published UK titles
    "harper brothers",       # Harper & Brothers Victorian co-editions
]

# ── EDITION & AGE SIGNALS ─────────────────────────────────────────────────────
# Presence in title or description scores +1 each (first edition scores +3 total).
AGE_SIGNALS = [
    # Edition markers
    "first edition",
    "1st edition",
    "first printing",
    "1st printing",
    "first published",

    # Era / age descriptors
    "victorian",
    "antique",
    "vintage",
    "rare",
    "scarce",
    "out of print",
    "collectible",
    "collectable",

    # Physical format (strong value indicators)
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

    # Illustration signals (see ILLUSTRATION_SIGNALS for bonus scoring)
    "illustrated",
    "plates",
    "engravings",
    "lithographs",
    "woodcuts",
    "chromolithograph",

    # Binding & condition positives
    "tight spine",
    "intact boards",
    "clean pages",

    # Bonus signals
    "presentation copy",
    "gift inscription",
    "inscribed",
    "signed",
    "named copy",
    "provenance",
    "bookplate",          # ★ owner bookplate (not library) can add value/interest
    "armorial",           # ★ armorial bookplate — collectible in itself
    "limited edition",
    "privately printed",  # ★ often scarce and overlooked
    "folio society",
    "oxford",
    "cambridge university press",
]

# ── MASSIVE BONUS ILLUSTRATION SIGNALS ───────────────────────────────────────
# Each match scores +2 (not +1) — these are the biggest value multipliers.
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

# ── SWEET SPOT YEAR RANGE ─────────────────────────────────────────────────────
YEAR_SWEET_SPOT_START = 1860
YEAR_SWEET_SPOT_END   = 1898   # post-1900 is a red flag — hard boundary
VALUABLE_BEFORE_YEAR  = 1900   # used by vinted.py year extraction logic

# ── TARGET GENRES ─────────────────────────────────────────────────────────────
# Used by scorer to recognise genre context in title/description.
TARGET_GENRE_SIGNALS = [
    # Natural History
    "natural history", "ornithology", "botany", "flora", "fauna",
    "zoology", "entomology", "geology", "conchology", "ichthyology",
    "fungi", "lichens", "mosses", "ferns", "wildflowers",

    # Astronomy & Science
    "astronomy", "celestial", "stellar", "telescope", "atlas of the heavens",
    "star atlas", "natural philosophy", "optics",

    # Exploration & Voyages
    "voyage", "voyages", "exploration", "expedition", "travels in",
    "journey to", "african", "arctic", "antarctic", "himalaya",
    "nile", "amazon", "pacific", "terra incognita",

    # Occult, Magic, Alchemy
    "occult", "alchemy", "alchemical", "magic", "magical",
    "witchcraft", "demonology", "kabbalah", "cabala", "hermetic",
    "rosicrucian", "freemasonry", "theosophy", "spiritualism",
    "astrology", "divination", "esoteric", "mysticism", "mystical",
    "folklore", "folk lore", "superstition",
]

# ── RED FLAGS — HARD WALK AWAY ────────────────────────────────────────────────
# Any match here subtracts points and may block the alert entirely.
BAD_TITLE_KEYWORDS = [
    # Your confirmed walk-aways
    "ex library",
    "ex-library",
    "ex libris",           # ★ sometimes used to mean ex-library on Vinted
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
    "reproduction",        # ★ facsimile reprints have little collector value
    "facsimile",
    "reprint",             # ★ modern reprints often misrepresented
    "modern reprint",
    "fascimile",
]

# ── POST-1900 HARD BLOCK ──────────────────────────────────────────────────────
# If a year >= this is detected in the title, the listing is skipped.
# Your rule: "no later than 1898" — 1900 used as the practical ceiling.
HARD_BLOCK_AFTER_YEAR = 1900