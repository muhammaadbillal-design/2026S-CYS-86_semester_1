CORRECT_MARKS = 4
WRONG_MARKS = -1
SKIP_MARKS = 0

questions = [
        {"question": "What is the value of sin(90°)?", "choices": ["A)0", "B)1", "C)-1", "D)0.5"], "answer": "B"},
        {"question": "Solve: x² - 9 = 0. What is x?", "choices": ["A)±3", "B)±9", "C)±4", "D)±6"], "answer": "A"},
        {"question": "What is the derivative of x³?", "choices": ["A)x²", "B)3x", "C)3x²", "D)x⁴/4"], "answer": "C"},
        {"question": "If log₂(8) = x, what is x?", "choices": ["A)2", "B)4", "C)3", "D)8"], "answer": "C"},
        {"question": "What is the SI unit of force?", "choices": ["A)Joule", "B)Newton", "C)Watt", "D)Pascal"], "answer": "B"},
        {"question": "Speed of light in vacuum is approximately?", "choices": ["A)3×10⁶ m/s", "B)3×10⁸ m/s", "C)3×10¹⁰ m/s", "D)3×10⁴ m/s"], "answer": "B"},
        {"question": "Which law states F = ma?", "choices": ["A)Newton 1st law", "B)Newton 3rd law", "C)Newton 2nd law", "D)Ohm's law"], "answer": "C"},
        {"question": "What does CPU stand for?", "choices": ["A)Central Process Unit", "B)Core Processing Unit", "C)Central Processing Unit", "D)Control Process Unit"], "answer": "C"},
        {"question": "Which data type stores True/False in Python?", "choices": ["A)int", "B)str", "C)float", "D)bool"], "answer": "D"},
        {"question": "What is the time complexity of binary search?", "choices": ["A)O(n)", "B)O(n²)", "C)O(log n)", "D)O(1)"], "answer": "C"},
]

all_results = []


# ---------------- RULES MODULE ----------------
def exam_rules():

    while True:

        print("\n========== EXAM INSTRUCTIONS ==========")
        print("1. Read Rules")
        print("2. Start Exam")
        print("3. Exit To Main Menu")

        choice = input("Enter choice: ")

        if choice == "1":

            print("\n========== RULES ==========")
            print("1. Each correct answer gives +4 marks")
            print("2. Each wrong answer gives -1 marks")
            print("3. Skipped questions give 0 marks")
            print("4. Enter S to skip any question")
            print("5. Enter SUBMIT to submit test early")
            print("6. Skipped questions will appear again at the end")
            print("7. Do not enter invalid options")

        elif choice == "2":
            student_exam()
            break

        elif choice == "3":
            print("Returning to Main Menu...")
            break

        else:
            print("Invalid Choice")


# ---------------- ADMIN PORTAL ----------------
def admin_portal():

    username = input("Enter Admin Username: ")
    password = input("Enter Password: ")

    if username == "ecat_admin" and password == "ecat@2026":

        print("Login Successful\n")

        while True:

            print("\n1. View Questions")
            print("2. Add Question")
            print("3. Delete Question")
            print("4. View Results")
            print("5. Exit")

            choice = input("Choose: ")

            if choice == "1":

                for i, q in enumerate(questions):
                    print(i + 1, q["question"], q["choices"], "Ans:", q["answer"])

            elif choice == "2":

                q_text = input("Enter question: ")

                choices = []

                for opt in ["A", "B", "C", "D"]:

                    option = input(f"{opt}) ")
                    choices.append(f"{opt}){option}")

                ans = input("Correct answer (A/B/C/D): ").upper()

                questions.append({
                    "question": q_text,
                    "choices": choices,
                    "answer": ans
                })

                print("Question Added Successfully!")

            elif choice == "3":

                num = int(input("Enter question number to delete: "))

                if 1 <= num <= len(questions):

                    questions.pop(num - 1)
                    print("Question Deleted!")

                else:
                    print("Invalid Number")

            elif choice == "4":

                print("\n========== RESULTS ==========")

                if len(all_results) == 0:
                    print("No Results Found")

                else:

                    for r in all_results:
                        print("\nName:", r["name"])
                        print("Roll No:", r["roll"])
                        print("Correct:", r["correct"])
                        print("Wrong:", r["wrong"])
                        print("Score:", r["score"])
                        print("Percentage:", r["percentage"], "%")
                        print("Grade:", r["grade"])

            elif choice == "5":

                print("Exiting Admin Portal...")
                break

            else:
                print("Invalid Choice")

    else:
        print("Wrong Credentials!")


# ---------------- STUDENT EXAM ----------------
def student_exam():

    name = input("Enter Name: ")
    roll = input("Enter Roll No: ")

    correct = 0
    wrong = 0

    skipped_questions = []

    print("\n========== TEST STARTED ==========")

    # FIRST ROUND
    for i, q in enumerate(questions):

        print("\nQ", i + 1, q["question"])

        for c in q["choices"]:
            print(c)

        ans = input("Answer (A/B/C/D/S/SUBMIT): ").upper()

        # Submit early
        if ans == "SUBMIT":
            break

        # Skip question
        elif ans == "S":
            skipped_questions.append((i, q))
            continue

        # Correct answer
        elif ans == q["answer"]:
            correct += 1

        # Wrong answer
        else:
            wrong += 1

    # ---------------- SKIPPED QUESTIONS ----------------
    if len(skipped_questions) > 0:

        print("\n===================================")
        print("NOW ATTEMPTING SKIPPED QUESTIONS")
        print("===================================")

        for item in skipped_questions:

            index = item[0]
            q = item[1]

            print("\nSkipped Q", index + 1, q["question"])

            for c in q["choices"]:
                print(c)

            ans = input("Answer (A/B/C/D or S to leave): ").upper()

            if ans == "S":
                continue

            elif ans == q["answer"]:
                correct += 1

            else:
                wrong += 1

    # ---------------- RESULT ----------------
    score = (correct * CORRECT_MARKS) + (wrong * WRONG_MARKS)

    total = len(questions) * CORRECT_MARKS

    percentage = (score / total) * 100

    if percentage >= 80:
        grade = "EXCELLENT"

    elif percentage >= 65:
        grade = "GOOD"

    elif percentage >= 50:
        grade = "AVERAGE"

    else:
        grade = "BELOW AVERAGE"

    result = {
        "name": name,
        "roll": roll,
        "correct": correct,
        "wrong": wrong,
        "score": score,
        "percentage": round(percentage, 2),
        "grade": grade
    }

    all_results.append(result)

    print("\n========== FINAL RESULT ==========")
    print("Name:", name)
    print("Roll No:", roll)
    print("Correct Answers:", correct)
    print("Wrong Answers:", wrong)
    print("Score:", score)
    print("Percentage:", round(percentage, 2), "%")
    print("Grade:", grade)


# ---------------- STUDENT PORTAL ----------------
def student_portal():

    username = input("Enter Username: ")
    password = input("Enter Password: ")

    if username == "student" and password == "student123":

        print("Login Successful")
        exam_rules()

    else:
        print("Wrong Credentials!")


# ---------------- MAIN MENU ----------------
def main():

    while True:

        print("\n========== ECAT SYSTEM ==========")
        print("1. Admin Portal")
        print("2. Student Portal")
        print("3. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            admin_portal()

        elif choice == "2":
            student_portal()

        elif choice == "3":
            print("Program Closed")
            break

        else:
            print("Invalid Choice")


# ---------------- RUN PROGRAM ----------------
main()