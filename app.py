
import json
import hashlib

import streamlit as st

from workflow import process_invoice

from database import (
    initialize_database,
    save_event,
    get_events,
    save_invoice,
    update_invoice_status,
    get_invoice_archive,
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Invoice Processing",
    page_icon="🧾",
    layout="wide",
)


# --------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------

initialize_database()


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "processing_result" not in st.session_state:
    st.session_state["processing_result"] = None

if "decision" not in st.session_state:
    st.session_state["decision"] = "Pending"

if "file_signature" not in st.session_state:
    st.session_state["file_signature"] = None

if "invoice_id" not in st.session_state:
    st.session_state["invoice_id"] = None


# --------------------------------------------------
# HELPER: SAVE HISTORY EVENT
# --------------------------------------------------

def add_history_event(invoice_id, action, details):
    save_event(invoice_id, action, details)


# --------------------------------------------------
# APPLICATION HEADER
# --------------------------------------------------

st.title("🧾 AI Invoice Processing & Approval")

st.write(
    "Upload an invoice PDF to extract, validate "
    "and review invoice information using AI."
)

st.divider()


# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload your invoice (PDF)",
    type=["pdf"],
)

if uploaded_file is not None:

    file_content = uploaded_file.getvalue()

    file_signature = hashlib.sha256(
        file_content
    ).hexdigest()

    if st.session_state["file_signature"] != file_signature:

        invoice_id = file_signature[:16]

        st.session_state["file_signature"] = file_signature
        st.session_state["invoice_id"] = invoice_id
        st.session_state["processing_result"] = None
        st.session_state["decision"] = "Pending"

        add_history_event(
            invoice_id,
            "Invoice uploaded",
            f"File: {uploaded_file.name}"
        )

    invoice_id = st.session_state["invoice_id"]

    st.success(f"Uploaded: {uploaded_file.name}")


    # --------------------------------------------------
    # PROCESS INVOICE
    # --------------------------------------------------

    if st.button("Process Invoice", type="primary"):

        add_history_event(
            invoice_id,
            "Processing started",
            "Invoice sent for AI extraction."
        )

        with st.spinner("AI is processing your invoice..."):

            try:

                result = process_invoice(uploaded_file)

                st.session_state["processing_result"] = result
                st.session_state["decision"] = "Pending"

                invoice_data = result["invoice_data"]
                validation = result["validation"]

                # Save invoice in database
                save_invoice(
                    invoice_id,
                    uploaded_file.name,
                    invoice_data
                )

                # Update initial invoice status
                if validation["valid"]:

                    update_invoice_status(
                        invoice_id,
                        "Pending approval"
                    )

                else:

                    update_invoice_status(
                        invoice_id,
                        "Validation failed"
                    )

                # Save extraction event
                add_history_event(
                    invoice_id,
                    "AI extraction completed",
                    f"Invoice: {invoice_data.get('invoice_number')}"
                )

                # Save validation result
                if validation["valid"]:

                    add_history_event(
                        invoice_id,
                        "Validation passed",
                        "All validation checks passed."
                    )

                else:

                    add_history_event(
                        invoice_id,
                        "Validation failed",
                        "; ".join(validation["errors"])
                    )

                # Save warnings
                for warning in validation["warnings"]:

                    add_history_event(
                        invoice_id,
                        "Validation warning",
                        warning
                    )

            except Exception as error:

                add_history_event(
                    invoice_id,
                    "Processing failed",
                    str(error)
                )

                st.error(f"Processing failed: {error}")


# --------------------------------------------------
# DISPLAY PROCESSING RESULTS
# --------------------------------------------------

if (
    uploaded_file is not None
    and st.session_state["processing_result"] is not None
):

    result = st.session_state["processing_result"]

    invoice_data = result["invoice_data"]
    validation = result["validation"]

    invoice_id = st.session_state["invoice_id"]

    st.divider()

    st.subheader("Extracted Invoice Data")

    st.json(invoice_data)

    st.subheader("Validation Result")

    if validation["valid"]:
        st.success("Invoice passed validation.")
    else:
        st.error("Invoice failed validation.")

    for error in validation["errors"]:
        st.error(error)

    for warning in validation["warnings"]:
        st.warning(warning)


    # --------------------------------------------------
    # APPROVAL WORKFLOW
    # --------------------------------------------------

    st.divider()

    st.subheader("Approval Workflow")

    if validation["errors"]:

        st.error("Manual clarification required.")

        st.info(
            "Approval is blocked until the errors are resolved."
        )

    else:

        if any(
            "€5,000" in warning
            for warning in validation["warnings"]
        ):

            st.warning("Additional approval required.")

        else:

            st.info("Standard human review required.")

        decision = st.session_state["decision"]

        if decision == "Pending":

            st.write(
                "Please review the invoice and make a decision."
            )

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "✅ Approve Invoice",
                    use_container_width=True
                ):

                    st.session_state["decision"] = "Approved"

                    update_invoice_status(
                        invoice_id,
                        "Approved"
                    )

                    add_history_event(
                        invoice_id,
                        "Invoice approved",
                        "Human reviewer approved the invoice."
                    )

            with col2:

                if st.button(
                    "❌ Reject Invoice",
                    use_container_width=True
                ):

                    st.session_state["decision"] = "Rejected"

                    update_invoice_status(
                        invoice_id,
                        "Rejected"
                    )

                    add_history_event(
                        invoice_id,
                        "Invoice rejected",
                        "Human reviewer rejected the invoice."
                    )

        decision = st.session_state["decision"]

        st.subheader("Approval Decision")

        if decision == "Approved":

            st.success(
                "Invoice approved by human reviewer."
            )

        elif decision == "Rejected":

            st.error(
                "Invoice rejected by human reviewer."
            )

        else:

            st.info("Waiting for human review.")


    # --------------------------------------------------
    # WORKFLOW HISTORY
    # --------------------------------------------------

    st.divider()

    st.subheader("📋 Workflow History")

    history = get_events(invoice_id)

    if history:

        st.caption(
            "Persistently stored workflow events for this invoice."
        )

        st.dataframe(
            history,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info("No history events available yet.")


    # --------------------------------------------------
    # DOWNLOAD PROCESSING REPORT
    # --------------------------------------------------

    report = {
        "invoice_id": invoice_id,
        "invoice": invoice_data,
        "validation": validation,
        "approval_decision": st.session_state["decision"],
        "workflow_history": history,
    }

    st.divider()

    st.download_button(
        label="Download Processing Report (JSON)",
        data=json.dumps(
            report,
            indent=4,
            ensure_ascii=False
        ),
        file_name="invoice_processing_report.json",
        mime="application/json",
    )


# --------------------------------------------------
# INVOICE ARCHIVE
# --------------------------------------------------

st.divider()

st.title("🗂️ Invoice Archive")

st.caption(
    "Overview of all invoices stored in the database."
)

archive = get_invoice_archive()

if archive:

    archive_display = [
        {
            "Invoice Number": invoice["invoice_number"],
            "Vendor": invoice["vendor"],
            "Invoice Date": invoice["invoice_date"],
            "Total Amount (€)": invoice["total_amount"],
            "Status": invoice["status"],
            "Uploaded At": invoice["uploaded_at"],
            "Filename": invoice["filename"],
        }
        for invoice in archive
    ]

    st.metric(
        "Total Invoices",
        len(archive)
    )

    st.dataframe(
        archive_display,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info("No invoices have been archived yet.")
