TABLE_DDL = """
CREATE TABLE IF NOT EXISTS "{table_name}" (
    EMPLOYEE_ID INTEGER PRIMARY KEY,
    DEPARTMENT TEXT NOT NULL,
    STATUS TEXT NOT NULL CHECK (STATUS IN ('CODER', 'NON-CODER')),
    TITLE TEXT NOT NULL
)
"""

SEED_SQL = """
INSERT OR IGNORE INTO "{table_name}"
    (EMPLOYEE_ID, DEPARTMENT, STATUS, TITLE)
VALUES (?, ?, ?, ?)
"""

SEED_ROWS = (
    (1001, "MSW", "CODER", "SOFTWARE ENGINEER"),
    (1002, "MSW", "CODER", "DATA ENGINEER"),
    (1003, "MSW", "NON-CODER", "PROJECT MANAGER"),
    (1004, "MRM", "CODER", "SOFTWARE ENGINEER"),
    (1005, "MRM", "NON-CODER", "RECRUITER"),
    (1006, "SECURITY", "NON-CODER", "SECURITY OFFICER"),
    (1007, "SECURITY", "CODER", "SECURITY ENGINEER"),
    (1008, "MRM", "CODER", "DATA ENGINEER"),
    (1009, "SECURITY", "NON-CODER", "SECURITY ANALYST"),
    (1010, "MSW", "NON-CODER", "BUSINESS ANALYST"),
)

COLUMN_GUIDE = {
    "EMPLOYEE_ID": {
        "description": "Unique numeric identifier for one employee.",
        "possible_values": "Integer IDs from 1001 to 1010 in the demo data.",
    },
    "DEPARTMENT": {
        "description": "Organizational department where the employee works.",
        "possible_values": "MSW, MRM, SECURITY.",
    },
    "STATUS": {
        "description": "Whether the employee is classified as a coding role.",
        "possible_values": "CODER, NON-CODER.",
    },
    "TITLE": {
        "description": "Official job title of the employee.",
        "possible_values": (
            "SOFTWARE ENGINEER, DATA ENGINEER, PROJECT MANAGER, RECRUITER, "
            "SECURITY OFFICER, SECURITY ENGINEER, SECURITY ANALYST, "
            "BUSINESS ANALYST."
        ),
    },
}

EXAMPLE_QUESTIONS = (
    "How many coders?",
    "Data engineers in MRM",
    "How many?",
)
