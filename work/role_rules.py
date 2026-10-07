"""Ordered role-family rules for Analytics Jobs designations (first match wins).

Order = specific analytics -> technology guards -> specific non-analytics -> BA / product / sales ->
generic analytics -> generic others. Audited on independent random samples (see data_quality_log).
"""
ROLE = [
    ("Data Scientist / ML / AI", r"data scien|machine learning|\bml\b|deep learning|computer vision|\bnlp\b|artificial intelligence|\bai\b|pattern recognition|imaging scientist|recommendation (system|engine)"),
    ("Data Engineer / Big Data", r"data engineer|big data|hadoop|\betl\b|spark|data architect|data warehous|\bdwh\b|data platform|data lake|data model|informatica|teradata|snowflake|databricks"),
    ("Statistical Modelling / SAS", r"\bsas\b|statistic|biostat|clinical programm|(?<!financial )model(l)?ing|model (develop|valid|implement)|predictive|econometric|forecast"),
    ("Risk / Credit / Quant Analytics", r"risk|fraud|credit|underwrit|collection strategy|\baml\b|\bkyc\b|compliance|\bsox\b|regulat|\bquants?\b|quantitative|trading|market making|algorithmic|actuar|\bgrc\b"),
    # explicit data-analyst titles and BI-tool titles win over the technology / domain guards below
    ("Data Analyst / Analytics", r"\bdata analy"),
    ("BI / Reporting / MIS", r"business intelligence|tableau|power ?bi|qlik|business objects|\bsap bo\b|cognos|microstrategy"),
    ("Data Analyst / Analytics", r"(hr|people|workforce|claims?|supply chain|sales|pricing|operations|customer|business|product|retail) analytics"),
    ("Healthcare RCM / Medical Coding", r"medical cod|medical bill|\bar (caller|analyst|executive|follow)|ar follow|\brcm\b|revenue cycle|\bmbbs\b|pharmacovigilance|clinical (data|research)|patient coding|out-?patient|in-?patient|transcription"),
    ("Software / IT", r"\bsap\b|oracle|salesforce|peoplesoft|workday|taleo|successfactors|\berp\b|servicenow|\.net|dotnet|\bjava\b|j2ee|python developer|\bphp\b|angular|react|node\.?js|devops|selenium|\btest(ing|er)?\b|\bqa\b|android|\bios\b|full stack|web develop|usability|user research|\bux\b|\bui\b|cyber|security (engineer|analyst|architect)|network (engineer|analyst|admin)|(system|app|apps|ui|ux|web|solution) designer|communications engineer|unified communications"),
    ("HR / Recruitment", r"(^|[^,]\s)hr\b(?!\s*$)|^hr\b|hrba|human resource|recruit|talent|payroll|\bhrbp\b|compensation|benefits|rewards|learning and development|\bl&d\b|executive search|headhunt"),
    ("Customer Support / BPO", r"customer (support|service|care)|custome |\bbpo\b|call cent|contact cent|voice process|non[- ]?voice|back office|tele ?caller|tele ?marketing|data entry|chat process|customer success|technical support|process associate|insurance process|claims (processing|executive|associate|adjuster)|claim adjuster|call (analyst|calibration|verifier)|(?<!data )quality (analyst|auditor)"),
    ("Research / Market Research", r"(market|marketing|consumer|primary|secondary|equity|business) research|research analyst"),
    ("Core Engineering / Manufacturing", r"\br&d\b|ar&d|formulation|oral solid|analytical (development|lab)"),
    ("Education / Training", r"trainer|training (manager|executive|coordinator)|faculty|teacher|tutor|lecturer|professor|\bcourse\b|academic|curriculum|instructional"),
    ("Admin / Legal / Executive Assistance", r"legal|counsel|lawyer|paralegal|executive assistant|personal assistant|\bsecretary\b|admin(istration)? (executive|manager|assistant)|office manager|front office|receptionist|tender"),
    ("Business Analyst", r"business analy|\bba\b|functional analy|product analy|system(s)? analy|business system"),
    ("Product / Project Management", r"product (manag|head|owner|lead)|project manag|program(me)? manag|scrum|delivery manag|\bpmo\b|program control"),
    ("Sales / Business Development", r"sales|business development|account manager|key account|\bbde\b|\bbdm\b|presales|inside sales|client acquisition|relationship manager|modern trade|general trade"),
    ("BI / Reporting / MIS", r"\bbi\b|business intelligence|tableau|power ?bi|qlik|\bmis\b|reporting|reports|dashboard|cognos|business objects|microstrategy|analytics developer|visualization"),
    ("Marketing / Web Analytics", r"marketing analy|web analy|digital analy|google analytics|adobe analytics|customer analy|campaign analy|pricing analy|market mix|\bmmm\b|tag management"),
    ("Finance / Accounts / Audit", r"financ|account|\bcfo\b|audit|\bia\b|\btax|treasury|\bfp ?& ?a\b|fpna|costing|controller|billing|\bca\b|chartered|budget|fp and a|reconcil|investment bank|\btlm\b|fund accounting|financial model"),
    ("Marketing / Digital / Media", r"\bseo\b|\bsem\b|\bsmo\b|digital marketing|social media|content|copywrit|\bppc\b|marketing|brand|campaign|growth|category (head|manag)|e[- ]?commerce|\bmedia\b|communications|\bevent|public relation|\bpr\b|advertis|search engine|\bad (trafficker|ops|operations|analyst)|designer|graphic|design and presentation|creative"),
    ("Core Engineering / Manufacturing", r"asic|vlsi|\brtl\b|fpga|firmware|embedded|mechanical|civil|structural|nvh|electrical|chemist|\bqc\b|quality control|plant|manufactur|production|automobile|automotive|hvac|instrumentation|process engineer|piping|metallurg|\bsafety\b|\behs\b|composite|aerospace|\bmrb\b|quantity surveyor|analytical lab"),
    ("Software / IT", r"developer|development engineer|software|programmer|\bit\b|network|infra|cloud|front ?end|back ?end|web design|database|\bdba\b|mobile app|security|siem|pega|\becm\b|snaplogic|spring|ext js|javascript|\botm\b|mule|\besb\b|abap|tibco|middleware|system admin|linux|unix|technical architect|solution architect|as ?400|system(s)? integration|\bengineer|\bengineering|\brpa\b"),
    ("Research / Market Research", r"research"),
    ("Operations / Supply Chain", r"process analyst|operations analyst|customer operations|order management|order to cash|procure|purchase|operation|supply chain|logistic|process excellence|six sigma|\blean\b|warehouse|inventory|vendor|facility|property|transport"),
    ("Data Analyst / Analytics", r"data analy|analytics|\banalyst\b|insights"),
    ("Strategy / Consulting", r"strateg|consult|advisory|planning|corporate development"),
]
ANALYTICS = {"Data Scientist / ML / AI", "Data Engineer / Big Data", "Statistical Modelling / SAS", "Risk / Credit / Quant Analytics",
             "BI / Reporting / MIS", "Marketing / Web Analytics", "Business Analyst", "Data Analyst / Analytics", "Research / Market Research"}
TITLE_NOISE_EXTRA = [r"\btop it (mnc|company)\b", r"\b(an? |the )?it (mnc|company|major|firm)\b", r"\bleading (it )?mnc\b", r"\bmnc\b",
                     r"\bcmmi level \d\b", r"\bsal(ary)? upto [\w ]+", r"\b\d+\s*-\s*\d+\s*yrs?\b", r"\bfemales? only\b",
                     r"\bnight shift\b", r"\bday shift\b", r"\binterviews?\b", r"\bdrive\b"]
