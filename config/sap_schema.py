"""SAP Excel Schema Definition"""

SAP_COLUMNS = [
    "BELNR", "BUDAT", "BLDAT", "BLART", "BUKRS", "WAERS", "BSCHL", "HKONT",
    "BUKRS_BSEG", "KOSTL", "AUFNR", "VBUND", "WRBTR", "MWSKZ", "SGTXT",
    "ZUONR", "Projekt-Nr", "Steuerbetrag", "MENGE", "MEINS", "Bewegungsart",
    "BZDAT", "Betrag in HW", "UMSKZ", "ZFBDT", "Kopftext", "MWST", "Tage",
    "Artikel", "Steuer", "WERK", "WWRPL", "WWRPM", "WWSPL", "WWOTL"
]

SAP_FIELD_DESCRIPTIONS = {
    "BELNR": "Accounting Document Number",
    "BUDAT": "Posting Date (YYYY-MM-DD)",
    "BLDAT": "Document Date (YYYY-MM-DD)",
    "BLART": "Document Type (e.g., KR for Vendor Invoice)",
    "BUKRS": "Company Code",
    "WAERS": "Currency Key (e.g., AED, USD)",
    "BSCHL": "Posting Key",
    "HKONT": "G/L Account Number",
    "BUKRS_BSEG": "Company Code at line-item level",
    "KOSTL": "Cost Center",
    "AUFNR": "Internal Order Number",
    "VBUND": "Trading Partner",
    "WRBTR": "Amount in Document Currency (numeric)",
    "MWSKZ": "Tax Code",
    "SGTXT": "Line Item Text/Description",
    "ZUONR": "Assignment Number",
    "Projekt-Nr": "Project Number",
    "Steuerbetrag": "Tax Amount (numeric)",
    "MENGE": "Quantity (numeric)",
    "MEINS": "Unit of Measure (e.g., EA, KG, HRS)",
    "Bewegungsart": "Movement Type",
    "BZDAT": "Baseline Date (YYYY-MM-DD)",
    "Betrag in HW": "Amount in Local Currency (numeric)",
    "UMSKZ": "Special G/L Indicator",
    "ZFBDT": "Terms of Payment Date (YYYY-MM-DD)",
    "Kopftext": "Document Header Text",
    "MWST": "VAT/Tax Indicator",
    "Tage": "Payment Days (numeric, calculated)",
    "Artikel": "Article/Item Description",
    "Steuer": "Tax Type",
    "WERK": "Plant",
    "WWRPL": "Work Center/Work Place",
    "WWRPM": "Work Center Person/Machine",
    "WWSPL": "Storage Location/Supply Area",
    "WWOTL": "Work Order/Operation Location"
}

# Fields typically present in invoice PDFs
PDF_PRESENT_FIELDS = [
    "BELNR", "BLDAT", "WAERS", "KOSTL", "WRBTR", "SGTXT", "ZUONR",
    "Steuerbetrag", "MENGE", "MEINS", "BZDAT", "ZFBDT", "Betrag in HW",
    "Kopftext", "MWST", "Artikel", "Steuer"
]

# Fields inferred or calculated
INFERRED_FIELDS = ["BUDAT", "BLART", "BUKRS", "BSCHL", "HKONT", "MWSKZ", "Tage"]

# Fields typically not present
OPTIONAL_FIELDS = [
    "AUFNR", "VBUND", "Projekt-Nr", "Bewegungsart", "UMSKZ",
    "WERK", "WWRPL", "WWRPM", "WWSPL", "WWOTL"
]

# Default values for missing fields
DEFAULT_VALUES = {
    "BLART": "KR",  # Vendor Invoice
    "BUKRS": "013",  # Default company code
    "BSCHL": "40",  # Line item posting key (use 31 for total line)
    "HKONT": "K0551",  # Default GL account for line items (use 5373979 for total)
    "BUKRS_BSEG": "013",  # Company code at line level
    "MWSKZ": "U4",  # Default tax code (0%)
    "MEINS": "each",  # Default unit of measure
    "AUFNR": "",
    "VBUND": "",
    "Projekt-Nr": "",
    "Bewegungsart": "",
    "UMSKZ": "",
    "WERK": "",
    "WWRPL": "",
    "WWRPM": "",
    "WWSPL": "",
    "WWOTL": ""
}
