import json
import os

LEGAL_SEED_DATA = [
    {
        "id": "BNS_137_IPC_363",
        "act": "Bharatiya Nyaya Sanhita (BNS) / Indian Penal Code (IPC)",
        "section": "Section 137 BNS / Section 363 IPC",
        "title": "Kidnapping and Abduction",
        "type": "statute",
        "content": "Whoever kidnaps any person from India or from lawful guardianship, shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine. Section 137 BNS governs offences of kidnapping, abduction, and unlawful restraint.",
        "keywords": ["section 137", "bns 137", "kidnapping", "abduction", "unlawful restraint", "guardianship", "ipc 363"],
        "court": "Statute",
        "year": "2023"
    },
    {
        "id": "BNS_303_IPC_378",
        "act": "Bharatiya Nyaya Sanhita (BNS) / Indian Penal Code (IPC)",
        "section": "Section 303 BNS / Section 378 IPC",
        "title": "Theft and Possession of Stolen Property",
        "type": "statute",
        "content": "Whoever, intending to take dishonestly any movable property out of the possession of any person without that person's consent, moves that property in order to such taking, commits theft. Punishable under Section 303 BNS with imprisonment up to three years or fine.",
        "keywords": ["theft", "stolen property", "dishonest intention", "movable property", "bns 303", "ipc 378", "section 303"],
        "court": "Statute",
        "year": "2023"
    },
    {
        "id": "BNS_318_IPC_420",
        "act": "Bharatiya Nyaya Sanhita (BNS) / Indian Penal Code (IPC)",
        "section": "Section 318 BNS / Section 420 IPC",
        "title": "Cheating and Dishonestly Inducing Delivery of Property",
        "type": "statute",
        "content": "Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person... shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine.",
        "keywords": ["cheating", "fraud", "financial fraud", "property", "bns 318", "ipc 420", "section 318"],
        "court": "Statute",
        "year": "2023"
    },
    {
        "id": "BNS_101_IPC_302",
        "act": "Bharatiya Nyaya Sanhita (BNS) / Indian Penal Code (IPC)",
        "section": "Section 101 BNS / Section 302 IPC",
        "title": "Punishment for Murder",
        "type": "statute",
        "content": "Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine. Under Section 101 of BNS 2023, murder is defined where an act by which death is caused is done with the intention of causing death.",
        "keywords": ["murder", "homicide", "death penalty", "life imprisonment", "intent", "bns 101", "ipc 302", "section 101"],
        "court": "Statute",
        "year": "2023"
    },
    {
        "id": "BNSS_479_CRPC_437",
        "act": "Bharatiya Nagarik Suraksha Sanhita (BNSS) / CrPC",
        "section": "Section 479 BNSS / Section 437 CrPC",
        "title": "Bail Provisions for Undertrial Prisoners",
        "type": "statute",
        "content": "Where a person has, during the period of investigation, inquiry or trial under this Sanhita of an offence, undergone detention for a period extending up to one-half of the maximum period of imprisonment, he shall be released by the Court on bail on his personal bond.",
        "keywords": ["bail", "undertrial prisoner", "personal bond", "anticipatory bail", "bnss 479", "crpc 437", "section 479"],
        "court": "Statute",
        "year": "2023"
    },
    {
        "id": "NI_138",
        "act": "Negotiable Instruments Act 1881",
        "section": "Section 138",
        "title": "Dishonour of Cheque for Insufficiency of Funds",
        "type": "statute",
        "content": "Where any cheque drawn by a person on an account maintained by him with a banker for payment of any amount of money is returned by the bank unpaid, such person shall be deemed to have committed an offence and shall be punished with imprisonment up to two years or fine up to twice the cheque amount.",
        "keywords": ["cheque bounce", "dishonour of cheque", "demand notice", "banker", "section 138", "ni act"],
        "court": "Statute",
        "year": "1881"
    },
    {
        "id": "BNS_356_IPC_499",
        "act": "Bharatiya Nyaya Sanhita (BNS) / Indian Penal Code (IPC)",
        "section": "Section 356 BNS / Section 499 IPC",
        "title": "Defamation (Criminal & Civil)",
        "type": "statute",
        "content": "Whoever, by words either spoken or intended to be read, or by signs or by visible representations, makes or publishes any imputation concerning any person intending to harm the reputation of such person, commits defamation. Punishable with simple imprisonment up to two years or fine.",
        "keywords": ["defamation", "reputation", "libel", "slander", "bns 356", "ipc 499", "section 356"],
        "court": "Statute",
        "year": "2023"
    },
    {
        "id": "HMA_13",
        "act": "Hindu Marriage Act 1955",
        "section": "Section 13",
        "title": "Divorce and Grounds for Dissolution of Marriage",
        "type": "statute",
        "content": "Any marriage solemnized may, on a petition presented by either the husband or the wife, be dissolved by a decree of divorce on grounds of cruelty, desertion for a period of not less than two years, adultery, or conversion.",
        "keywords": ["divorce", "cruelty", "desertion", "alimony", "maintenance", "section 13", "hindu marriage act"],
        "court": "Statute",
        "year": "1955"
    },
    {
        "id": "TPA_106",
        "act": "Transfer of Property Act 1882",
        "section": "Section 106",
        "title": "Duration of Leases and Termination Notice",
        "type": "statute",
        "content": "In the absence of a contract or local law to the contrary, a lease of immovable property for agricultural or manufacturing purposes shall be deemed to be a lease from year to year, terminable by six months' notice, and a lease for any other purpose shall be deemed to be a lease from month to month, terminable by fifteen days' notice.",
        "keywords": ["lease", "tenant", "landlord", "eviction", "rent", "termination notice", "section 106", "tpa"],
        "court": "Statute",
        "year": "1882"
    },
    {
        "id": "ICA_73",
        "act": "Indian Contract Act 1872",
        "section": "Section 73",
        "title": "Compensation for Loss or Damage Caused by Breach of Contract",
        "type": "statute",
        "content": "When a contract has been broken, the party who suffers by such breach is entitled to receive, from the party who has broken the contract, compensation for any loss or damage caused to him thereby, which naturally arose in the usual course of things from such breach.",
        "keywords": ["breach of contract", "damages", "compensation", "liquidated damages", "section 73", "contract act"],
        "court": "Statute",
        "year": "1872"
    },
    {
        "id": "CONS_ART_21",
        "act": "Constitution of India",
        "section": "Article 21",
        "title": "Protection of Life and Personal Liberty",
        "type": "statute",
        "content": "No person shall be deprived of his life or personal liberty except according to procedure established by law. Article 21 covers fundamental rights including right to privacy, right to clean environment, right to speedy trial, and right to legal aid.",
        "keywords": ["fundamental rights", "personal liberty", "privacy", "speedy trial", "article 21", "constitution"],
        "court": "Supreme Court of India",
        "year": "1950"
    },
    {
        "id": "CONS_ART_32",
        "act": "Constitution of India",
        "section": "Article 32",
        "title": "Remedies for Enforcement of Fundamental Rights (Writs)",
        "type": "statute",
        "content": "The right to move the Supreme Court by appropriate proceedings for the enforcement of the rights conferred by Part III is guaranteed. The Supreme Court shall have power to issue directions or orders or writs, including habeas corpus, mandamus, prohibition, quo warranto and certiorari.",
        "keywords": ["writs", "habeas corpus", "mandamus", "supreme court", "article 32", "constitutional remedies"],
        "court": "Supreme Court of India",
        "year": "1950"
    },
    {
        "id": "CPA_35",
        "act": "Consumer Protection Act 2019",
        "section": "Section 35",
        "title": "Manner in which Complaint shall be made to District Commission",
        "type": "statute",
        "content": "A complaint in relation to any goods sold or delivered or agreed to be sold or delivered or any service provided or agreed to be provided may be filed with a District Commission by a consumer. Complaints can be filed online via e-Daakhil portal.",
        "keywords": ["consumer complaint", "defective product", "deficiency of service", "district commission", "e-daakhil", "cpa 35"],
        "court": "Statute",
        "year": "2019"
    },
    {
        "id": "IT_66D",
        "act": "Information Technology Act 2000",
        "section": "Section 66D",
        "title": "Punishment for Cheating by Personation by Using Computer Resource",
        "type": "statute",
        "content": "Whoever by means of any communication device or computer resource cheats by personation, shall be punished with imprisonment of either description for a term which may extend to three years and shall also be liable to fine which may extend to one lakh rupees.",
        "keywords": ["cybercrime", "phishing", "online impersonation", "cyber fraud", "it act 66d", "section 66d"],
        "court": "Statute",
        "year": "2000"
    },
    {
        "id": "CASE_PUTTASWAMY_2017",
        "act": "Landmark Judgments",
        "section": "Right to Privacy Case",
        "title": "Justice K.S. Puttaswamy (Retd.) v. Union of India (2017) 10 SCC 1",
        "type": "judgment",
        "content": "A 9-judge Bench of the Supreme Court unanimously affirmed that the Right to Privacy is a fundamental right under Article 21 of the Constitution of India. The Court held that privacy includes informational privacy, bodily autonomy, and spatial privacy.",
        "keywords": ["privacy", "puttaswamy", "fundamental right", "article 21", "data protection", "aadhaar"],
        "court": "Supreme Court of India",
        "year": "2017",
        "judges": ["J. S. Khehar", "D. Y. Chandrachud", "S. A. Bobde", "R. F. Nariman"],
        "ratio_decidendi": "Right to privacy is an intrinsic part of the right to life and personal liberty under Article 21 and Part III of the Constitution."
    },
    {
        "id": "CASE_DK_BASU_1997",
        "act": "Landmark Judgments",
        "section": "Arrest Guidelines",
        "title": "D.K. Basu v. State of West Bengal (1997) 1 SCC 416",
        "type": "judgment",
        "content": "The Supreme Court issued mandatory guidelines to be followed by law enforcement during arrest and detention to prevent custodial violence and torture. Guidelines require arresting officers to wear clear identification, prepare a memo of arrest, inform relatives, and arrange medical examination every 48 hours.",
        "keywords": ["arrest guidelines", "custodial violence", "police arrest", "dk basu", "legal rights of accused"],
        "court": "Supreme Court of India",
        "year": "1997",
        "judges": ["Kuldip Singh", "A.S. Anand"],
        "ratio_decidendi": "Custodial violence and abuse of police power violates Article 21. Specific procedural safeguards must be complied with during every arrest."
    },
    {
        "id": "CASE_ARNESH_KUMAR_2014",
        "act": "Landmark Judgments",
        "section": "Automatic Arrest Prevention",
        "title": "Arnesh Kumar v. State of Bihar (2014) 8 SCC 273",
        "type": "judgment",
        "content": "The Supreme Court directed that police officers should not automatically arrest accused persons in offences punishable with imprisonment up to 7 years without satisfying the necessity of arrest under Section 41 CrPC (Section 35 BNSS).",
        "keywords": ["arnesh kumar", "automatic arrest", "498a", "bail guidelines", "crpc 41", "bnss 35"],
        "court": "Supreme Court of India",
        "year": "2014",
        "judges": ["Chandramauli Kr. Prasad", "Pinaki Chandra Ghose"],
        "ratio_decidendi": "Arrest should be the exception and not the rule for offences punishable with less than 7 years imprisonment."
    },
    {
        "id": "BNSS_35_CRPC_41",
        "act": "Bharatiya Nagarik Suraksha Sanhita (BNSS) / CrPC",
        "section": "Section 35 BNSS / Section 41 CrPC",
        "title": "When Police May Arrest Without Warrant",
        "type": "statute",
        "content": "Any police officer may without an order from a Magistrate and without a warrant arrest any person who commits a cognizable offence in the presence of a police officer, or against whom a reasonable complaint has been made or credible information received.",
        "keywords": ["arrest without warrant", "cognizable offence", "police powers", "bnss 35", "crpc 41", "section 35"],
        "court": "Statute",
        "year": "2023"
    },
    {
        "id": "RTI_6",
        "act": "Right to Information Act 2005",
        "section": "Section 6",
        "title": "Request for Obtaining Information",
        "type": "statute",
        "content": "A person who desires to obtain any information under this Act shall make a request in writing or through electronic means in English or Hindi or in the official language of the area to the Central Public Information Officer (CPIO) or State Public Information Officer (SPIO). Response must be provided within 30 days.",
        "keywords": ["rti", "right to information", "cpio", "public authority", "government transparency", "section 6"],
        "court": "Statute",
        "year": "2005"
    }
]

def get_legal_corpus():
    return LEGAL_SEED_DATA
