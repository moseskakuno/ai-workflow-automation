# AI Invoice Processing & Approval Workflow

An AI-powered invoice processing and approval application built with Python, Streamlit, and the OpenAI API.

This project automates key steps of invoice processing, from extracting invoice information from PDF documents to validating financial data, identifying potential issues, and managing human approval decisions.

The application demonstrates how AI can be integrated into a structured business workflow with validation rules, risk handling, database persistence, and human-in-the-loop approval.

## 🚀 Live Demo

**GitHub Repository:**
[https://github.com/moseskakuno/ai-workflow-automation](https://github.com/moseskakuno/ai-workflow-automation)

**Application:**
Deployed using Streamlit Community Cloud.

## 📌 Project Overview

Manual invoice processing can be time-consuming and error-prone. Businesses need to extract invoice information, verify financial calculations, identify inconsistencies, and ensure that invoices are approved by the appropriate person.

This application addresses these challenges through an AI-powered workflow.

Users can upload an invoice as a PDF file. The AI extracts relevant invoice information, while a separate validation layer checks the extracted data against predefined business rules.

Invoices that pass validation can proceed to human approval. Invoices containing errors are blocked until clarification or correction is provided.

The application also maintains a workflow history and an invoice archive using SQLite.

## ✨ Key Features

- **PDF Invoice Upload:** Upload invoice documents directly through the Streamlit interface.
- **AI-Powered Data Extraction:** Extract structured invoice information using the OpenAI API.
- **Automatic Data Validation:** Check required fields, numerical values, and invoice calculations.
- **Error Detection:** Identify inconsistencies between net amounts, tax amounts, and total amounts.
- **Risk Assessment:** Flag invoices requiring additional attention.
- **Rule-Based Approval Routing:** Apply business rules to determine the next processing step.
- **Human-in-the-Loop Approval:** Allow human reviewers to approve or reject invoices.
- **Workflow History:** Record processing events and decisions with timestamps.
- **Invoice Archive:** Store and display processed invoice information.
- **JSON Report Export:** Download invoice processing results for further analysis.

## 🔄 Workflow Architecture

The application follows a structured invoice processing pipeline:

1. **Invoice Upload**
   The user uploads a PDF invoice.

2. **Text Extraction**
   The application extracts readable text from the PDF.

3. **AI Data Extraction**
   The OpenAI API analyzes the invoice and extracts structured information.

4. **Data Validation**
   The validation layer checks required fields, numerical values, and financial calculations.

5. **Risk Assessment**
   The workflow identifies potential issues and applies predefined business rules.

6. **Approval Routing**
   Depending on the validation results and invoice amount, the invoice is assigned to the appropriate review process.

7. **Human Approval**
   A human reviewer makes the final approval or rejection decision.

8. **Database Storage**
   Invoice information and workflow events are stored in SQLite.

## 🧠 Business Rules

The application uses predefined validation and routing rules.

| Condition                                                    | Workflow Action                          |
| ------------------------------------------------------------ | ---------------------------------------- |
| All required fields are present and calculations are correct | Proceed to human review                  |
| Invoice amount exceeds €5,000                                | Additional approval required             |
| Required information is missing                              | Manual review required                   |
| Net amount + tax does not equal total amount                 | Block approval and request clarification |
| Potentially suspicious information                           | Flag for additional review               |

**Important:** AI extraction and business validation are separate steps. The AI extracts information, while deterministic Python rules perform the financial checks.

## 🛠️ Technology Stack

| Technology                | Purpose                                    |
| ------------------------- | ------------------------------------------ |
| Python                    | Core application logic                     |
| Streamlit                 | Interactive web application                |
| OpenAI API                | AI-powered invoice data extraction         |
| SQLite                    | Invoice archive and workflow history       |
| PyPDF                     | PDF text extraction                        |
| python-dotenv             | Local environment variable management      |
| JSON                      | Structured AI output and report export     |
| Git & GitHub              | Version control and source code management |
| Streamlit Community Cloud | Application deployment                     |

## 📂 Project Structure

```text
ai-workflow-automation/
│
├── app.py                 # Streamlit user interface
├── ai_processor.py        # AI-powered invoice extraction
├── workflow.py            # Workflow orchestration
├── validators.py          # Invoice validation rules
├── database.py            # SQLite database operations
│
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── .gitignore             # Excluded files and secrets
│
└── workflow_history.db    # Local database (generated at runtime)
```

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/moseskakuno/ai-workflow-automation.git

cd ai-workflow-automation
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=your_available_model_name
```

Replace the placeholder values with your own API credentials and an API model available to your OpenAI project.

**Never commit your `.env` file or expose your API key publicly.**

### 5. Run the Application

```bash
streamlit run app.py
```

The application will be available locally at:

```text
http://localhost:8501
```

## ☁️ Deployment

The application can be deployed using Streamlit Community Cloud.

Deployment steps:

1. Push the project to a GitHub repository.
2. Sign in to Streamlit Community Cloud.
3. Connect the GitHub repository.
4. Select the `main` branch.
5. Set `app.py` as the main application file.
6. Configure the required environment variables in Streamlit Secrets.
7. Deploy the application.

Example Streamlit Secrets configuration:

```toml
OPENAI_API_KEY = "your_openai_api_key"
OPENAI_MODEL = "your_available_model_name"
```

The application supports both local `.env` configuration and Streamlit Cloud Secrets.

## 🧪 Testing & Validation

The application has been tested with valid and invalid invoice scenarios.

### Test Case 1: Valid Invoice

**Input:**

| Field          |       Value |
| -------------- | ----------: |
| Vendor         | Muster GmbH |
| Invoice Number | RE-2026-004 |
| Net Amount     |      €1,000 |
| Tax Amount     |        €190 |
| Total Amount   |      €1,190 |

**Expected Result:**

- AI extraction completed successfully.
- Financial validation passed.
- Invoice proceeded to human approval.
- Human reviewer approved the invoice.
- Workflow events were stored in the database.

**Result:** Passed.

### Test Case 2: Invalid Invoice

**Input:**

| Field          |  Value |
| -------------- | -----: |
| Net Amount     | €1,000 |
| Tax Amount     |   €190 |
| Declared Total | €1,250 |

**Expected Result:**

- AI extracts the invoice information.
- Validation detects the incorrect calculation.
- The invoice fails validation.
- Manual clarification is required.
- Approval is blocked until the error is resolved.

**Validation Error:**

```text
Net amount plus tax does not match total amount.
```

**Result:** Passed.

### Test Case 3: High-Value Invoice

**Scenario:** An invoice exceeds the €5,000 approval threshold.

**Expected Result:**

- Financial validation is performed.
- The workflow identifies the high-value invoice.
- An additional approval requirement is flagged.

**Result:** Tested in the local validation workflow.

## 🔐 Security & Data Handling

Security is an important consideration when working with financial documents and API credentials.

The project follows these principles:

- API credentials are stored in environment variables or Streamlit Secrets.
- `.env` files are excluded from Git using `.gitignore`.
- Virtual environments and local database files are excluded from version control.
- SQL queries use parameterized statements.
- Invoice approval requires human review.
- The application does not execute payments or transfer money.

**Data persistence note:** The current implementation uses SQLite. On Streamlit Community Cloud, the local filesystem is not guaranteed to persist across application restarts or redeployments. A managed external database such as PostgreSQL would be recommended for production use.

Users should only upload documents they are authorized to process. The application is a demonstration project and is not a certified accounting or compliance system.

## 🚧 Future Improvements

Potential improvements include:

- Integration with PostgreSQL for persistent cloud storage.
- OCR support for scanned PDF invoices.
- Duplicate invoice detection.
- Advanced fraud and anomaly detection.
- Configurable approval thresholds.
- Multi-level approval workflows.
- User authentication and role-based access control.
- Automated email notifications.
- Integration with accounting and ERP systems.
- More comprehensive automated tests using pytest.

## 🎯 Learning Objectives

This project was developed to explore and demonstrate practical skills in:

- Integrating AI APIs into Python applications.
- Extracting structured information from unstructured documents.
- Building modular Python applications.
- Implementing deterministic business validation rules.
- Designing multi-step workflow automation.
- Managing approval processes with human oversight.
- Working with SQLite databases.
- Building interactive applications with Streamlit.
- Managing source code with Git and GitHub.
- Deploying AI-powered applications to the cloud.

## 👨‍💻 Author

**Moses Ochieng Akuno**

Web Developer | Python Developer | AI Automation Enthusiast

GitHub: https://github.com/moseskakuno/ai-workflow-automation

This project is part of my practical portfolio, demonstrating how Python, AI APIs, and workflow automation can be combined to solve real-world business problems.

A portfolio project demonstrating practical applications of:

- Generative AI
- OpenAI API Integration
- AI-Powered Document Processing
- PDF Data Extraction
- Automated Data Validation
- Business Process Automation
- Rule-Based Workflow Management
- Risk Assessment and Error Detection
- Human-in-the-Loop Approval Workflows
- Database Management with SQLite
- Python Application Development
---

*Built with Python, Streamlit, SQLite, and the OpenAI API.*
