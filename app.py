from flask import Flask, render_template, request, redirect, url_for, flash 
import datetime
import json
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'library_secret_key'

# Load initial data
try:
    with open('data.json', 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    data = {"books": [], "members": [], "transactions": [], "staff_members":[]}

# Save data function
def save_data():
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=5)
        
@app.context_processor
def inject_now():
    from datetime import datetime
    return {"now": datetime.now()}
# Routes
@app.route("/")
def home():
    return render_template("home.html")

# Sample data structure

@app.route("/staff", methods=["GET", "POST"])
def staff():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        role = request.form.get("role")
        phone = request.form.get("phone")
        
        # Input validation
        if "@" not in email or "." not in email:
            flash("Invalid email format!", "error")
        elif len(phone) != 10 or not phone.isdigit():
            flash("Phone number must be exactly 10 digits!", "error")
        else:
            # Add new staff member
            new_staff = {
                "id": len(data["staff_members"]) + 1,
                "name": name,
                "email": email,
                "role": role,
                "phone": phone
            }
            data["staff_members"].append(new_staff)
            save_data()
            flash("Staff member added successfully!", "success")
            return redirect(url_for("staff"))

    return render_template("staff.html", staff_members=data["staff_members"])

@app.route("/books", methods=["GET", "POST"])
def books():
    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        genre = request.form.get("genre")
        pub_year = int(request.form.get("pub_year"))
        available_copies = int(request.form.get("available_copies"))
        isbn = request.form.get("isbn")
        rating = int(request.form.get("rating"))

        # Validations
        if any(book["isbn"] == isbn for book in data["books"]):
            flash("ISBN must be unique!", "error")
        elif not (1900 <= pub_year <= datetime.now().year):
            flash("Invalid publication year!", "error")
        elif not (1 <= rating <= 5):
            flash("Rating must be between 1 and 5!", "error")
        else:
            # Generate a new Member ID (auto-generated)
            new_book_id = len(data["members"]) + 1
            
       # else:
            new_book = {
                "id": new_book_id,
                "title": title,
                "author": author,
                "genre": genre,
                "pub_year": pub_year,
                "available_copies": available_copies,
                "isbn": isbn,
                "rating": rating
            }
            data["books"].append(new_book)
            save_data()
            flash("Book added successfully!", "success")
            return redirect(url_for("books"))
    
    #return render_template("books.html", books=data["books"])
    return render_template("books.html", books=data["books"], now=datetime.now())


@app.route("/members", methods=["GET", "POST"])
def members():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        membership_type = request.form.get("membership_type")
        membership_start_date = datetime.now().strftime('%Y-%m-%d')
        max_books_allowed = int(request.form.get("max_books_allowed"))

        # Check if email is unique
        if any(member["email"] == email for member in data["members"]):
            flash("Email must be unique!", "error")
        # Validate phone number length (must be 10 digits)
        elif len(phone) != 10:
            flash("Phone number must be 10 digits!", "error")
        else:
            # Generate a new Member ID (auto-generated)
            new_member_id = len(data["members"]) + 1

            # Determine Max Books Allowed based on Membership Type
            max_books_allowed = {"Basic": 2, "Premium": 5, "Elite": 10}[membership_type]

            # Create a new member dictionary
            new_member = {
                "id": new_member_id,
                "name": name,
                "email": email,
                "phone": phone,
                "membership_type": membership_type,
                "membership_start_date": membership_start_date,
                "max_books_allowed": max_books_allowed
            }

            # Add the new member to the data list
            data["members"].append(new_member)

            # Save the data
            save_data()

            flash("Member added successfully!", "success")
            return redirect(url_for("members"))

    return render_template("members.html", members=data["members"])



@app.route("/transactions", methods=["GET", "POST"])
def transactions():
    if request.method == "POST":
        # Get form data
        member_id = int(request.form.get("member"))
        book_id = int(request.form.get("book"))
        issue_date = request.form.get("issue_date")
        return_date = request.form.get("return_date")
        status = request.form.get("status")
        
        # Lookup book and member
        book = next((b for b in data["books"] if b["id"] == book_id), None)
        member = next((m for m in data["members"] if m["id"] == member_id), None)

        # Validate return date
        if return_date <= issue_date:
            flash("Return date must be greater than the issue date!", "error")
            return redirect(url_for("transactions"))

        if book is None or member is None:
            flash("Invalid member or book selection!", "error")
        elif book["available_copies"] <= 0:
            flash("No copies available to issue!", "error")
        else:
            transaction_id = len(data["members"]) + 1

            # Deduct a copy from available books
            book["available_copies"] -= 1            
            # Calculate fine (if overdue)
            fine_amount = 0
            if status == "Overdue":
                fine_days = (datetime.strptime(return_date, "%Y-%m-%d") - datetime.strptime(issue_date, "%Y-%m-%d")).days - 14  # Assuming 14 days allowed
                fine_amount = max(0, fine_days * 5)  # $5 per overdue day

            # Add transaction
            new_transaction = {
                "id": transaction_id,
                "member": member["name"],
                "book": book["title"],
                "issue_date": issue_date,
                "return_date": return_date,
                "status": status,
                "fine_amount": fine_amount,
            }
            data["transactions"].append(new_transaction)
            save_data()
            flash("Transaction recorded successfully!", "success")
            return redirect(url_for("transactions"))

    return render_template(
        "transactions.html",
        transactions=data["transactions"],
        books=data["books"],
        members=data["members"],
        now=datetime.now,
    )

if __name__ == "__main__":
    app.run(debug=True)
