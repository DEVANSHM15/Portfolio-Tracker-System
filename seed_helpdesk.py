from database import db, HelpDeskQA

def seed_helpdesk_data():
    # Pre-defined Q&A data
    qa_data = [
        {"question": "How do I upload documents?", "answer": "You can upload documents by navigating to the 'Submit Activity' section and selecting the file you want to upload.", "category": "Uploads"},
        {"question": "How are points calculated?", "answer": "Points are calculated based on the type of activity you submit. Each activity has a specific point value.", "category": "General"},
        {"question": "What activities can I track?", "answer": "You can track various activities such as journal submissions, event participation, and community service.", "category": "Activities"},
        {"question": "How do I delete an upload?", "answer": "To delete an upload, go to your submitted activities and select the delete option next to the activity.", "category": "Uploads"},
        {"question": "Where can I see my points?", "answer": "You can view your points on your student dashboard.", "category": "General"},
    ]

    # Add Q&A to the database
    for qa in qa_data:
        new_qa = HelpDeskQA(question=qa["question"], answer=qa["answer"], category=qa["category"])
        db.session.add(new_qa)

    db.session.commit()
    print("Help desk data seeded successfully.")

if __name__ == "__main__":
    from app import app
    with app.app_context():
        seed_helpdesk_data()
