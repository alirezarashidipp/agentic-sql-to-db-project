COLUMN_GUIDE = {
    "EMPLOYEE_ID": {
        "description": "Unique numeric identifier for one employee.",
        "possible_values": "Integer IDs from 1001 to 1100 in the demo data.",
    },
    "EMPLOYEE_NAME": {
        "description": "Synthetic full name of the employee.",
        "possible_values": (
            "100 fictional demo names, such as AVA CARTER and LEO KOWALSKI."
        ),
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
