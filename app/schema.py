TABLE_NAME = "data"


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


# Update these golden cases with COLUMN_GUIDE when the configured dataset changes.
EVAL_CASES = {
    "sql": (
        {
            "id": "coder-count",
            "question": "How many coders are there?",
            "reference_sql": (
                f'SELECT COUNT(*) FROM "{TABLE_NAME}" '
                'WHERE "STATUS" = \'CODER\''
            ),
            "compare": "scalar",
        },
        {
            "id": "department-counts",
            "question": "How many employees are in each department?",
            "reference_sql": (
                f'SELECT "DEPARTMENT", COUNT(*) FROM "{TABLE_NAME}" '
                'GROUP BY "DEPARTMENT"'
            ),
            "compare": "grouped",
        },
        {
            "id": "mrm-data-engineers",
            "question": "List the names of data engineers in MRM.",
            "reference_sql": (
                f'SELECT "EMPLOYEE_NAME" FROM "{TABLE_NAME}" '
                'WHERE "TITLE" = \'DATA ENGINEER\' '
                'AND "DEPARTMENT" = \'MRM\''
            ),
            "compare": "unordered",
        },
        {
            "id": "smallest-employee-ids",
            "question": (
                "List the five smallest employee IDs in ascending order."
            ),
            "reference_sql": (
                f'SELECT "EMPLOYEE_ID" FROM "{TABLE_NAME}" '
                'ORDER BY "EMPLOYEE_ID" ASC LIMIT 5'
            ),
            "compare": "ordered",
        },
    ),
    "rejected": (
        {
            "id": "missing-subject",
            "question": "How many?",
            "expected_status": "incomplete",
        },
        {
            "id": "undefined-best",
            "question": "Who are the best employees?",
            "expected_status": "incomplete",
        },
        {
            "id": "missing-column",
            "question": "What is the average employee salary?",
            "expected_status": "invalid",
        },
        {
            "id": "write-request",
            "question": "Delete every employee.",
            "expected_status": "invalid",
        },
    ),
    "answers": (
        {
            "id": "scalar-answer",
            "question": "How many employees are there?",
            "sql": f'SELECT COUNT(*) AS total FROM "{TABLE_NAME}"',
            "rows": [{"total": 3}],
            "reference_answer": "There are 3 employees.",
        },
        {
            "id": "grouped-answer",
            "question": "How many employees are in each department?",
            "sql": (
                f'SELECT "DEPARTMENT", COUNT(*) AS total FROM "{TABLE_NAME}" '
                'GROUP BY "DEPARTMENT"'
            ),
            "rows": [
                {"DEPARTMENT": "MRM", "total": 2},
                {"DEPARTMENT": "SECURITY", "total": 1},
            ],
            "reference_answer": (
                "MRM has 2 employees and SECURITY has 1 employee."
            ),
        },
    ),
}
