# UNIPROT related description
UNIPROT_AC_DESC = "UniProt accession, e.g. P00520"
UNIPROT_ID_DESC = "UniProt identifier, e.g. ABL1_MOUSE"
UNIPROT_QUAL_DESC = "UniProtKB accession number (AC) or entry name (ID)"
TEMPLATE_DESC = (
    "Template is 4 letter PDB code, or 4 letter code with "
    "assembly ID and chain for SMTL entries"
)
UNP_CHECKSUM_DESC = "CRC64 checksum of the UniProt sequence"
ENSEMBL_QUAL_DESC = "Ensembl identifier."

# RESPONSE MESSAGES
NO_JOB_FOUND_MESSAGE = (
    "No search job found for the given sequence, please submit the job again!"
)
SEARCH_IN_PROGRESS_MESSAGE = "Search in progress, please try after sometime!"
JOB_SUBMISSION_ERROR_MESSAGE = "Error in submitting the job, please retry!"
JOB_FAILED_ERROR_MESSAGE = (
    "Failed to process the search request, please submit the sequence again!"
)
