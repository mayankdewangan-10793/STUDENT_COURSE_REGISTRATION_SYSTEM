import os

FILE_NAME = "registrations.txt"
MAX_COURSES_PER_STUDENT = 3


class Course:
    def __init__(self, code, title, capacity):
        self.code = code
        self.title = title
        self.capacity = capacity
        self.students = []  # enrolled student IDs

    def seats_left(self):
        return self.capacity - len(self.students)

    def is_full(self):
        return self.seats_left() <= 0

    def enroll(self, student_id):
        self.students.append(student_id)

    def remove(self, student_id):
        self.students.remove(student_id)

    def __str__(self):
        return (f"{self.code} - {self.title} "
                f"(capacity {self.capacity}, enrolled {len(self.students)}, "
                f"seats left {self.seats_left()})")


class Student:
    def __init__(self, student_id, name):
        self.student_id = student_id
        self.name = name
        self.courses = []  # enrolled course codes

    def has_course(self, code):
        return code in self.courses

    def add_course(self, code):
        self.courses.append(code)

    def drop_course(self, code):
        self.courses.remove(code)


class RegistrationSystem:
    def __init__(self, filename=FILE_NAME):
        self.filename = filename
        # Courses kept in a dictionary: code -> Course (holds capacity + enrolled students)
        self.courses = {
            "CS101": Course("CS101", "Programming", 2),
            "MA101": Course("MA101", "Mathematics", 30),
            "PH101": Course("PH101", "Physics", 30),
        }
        self.students = {}  # student_id -> Student
        self.load()

    # ---------- File handling ----------
    def load(self):
        if not os.path.exists(self.filename):
            return
        with open(self.filename, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(",")
                sid, name = parts[0], parts[1]
                codes = parts[2].split(";") if len(parts) > 2 and parts[2] else []
                student = Student(sid, name)
                for code in codes:
                    if code in self.courses:
                        student.add_course(code)
                        self.courses[code].enroll(sid)
                self.students[sid] = student

    def save(self):
        with open(self.filename, "w") as f:
            for s in self.students.values():
                f.write(f"{s.student_id},{s.name},{';'.join(s.courses)}\n")

    # ---------- CRUD operations ----------
    def register(self, sid, name, code):
        code = code.upper()
        if code not in self.courses:
            return f"Course {code} does not exist."
        course = self.courses[code]
        student = self.students.get(sid)
        if student and student.has_course(code):
            return f"Student {sid} is already registered in {code}."
        if student and len(student.courses) >= MAX_COURSES_PER_STUDENT:
            return (f"Student {sid} cannot register for more than "
                    f"{MAX_COURSES_PER_STUDENT} courses.")
        if course.is_full():
            return f"Course {code} is full."
        if student is None:
            student = Student(sid, name)
            self.students[sid] = student
        student.add_course(code)
        course.enroll(sid)
        self.save()
        return (f"Registered: {student.name} ({sid}) in {code} - {course.title}. "
                f"Seats left: {course.seats_left()}")

    def drop(self, sid, code):
        code = code.upper()
        if code not in self.courses:
            return f"Course {code} does not exist."
        student = self.students.get(sid)
        if student is None:
            return f"Student {sid} not found."
        if not student.has_course(code):
            return f"Student {sid} is not registered in {code}."
        student.drop_course(code)
        course = self.courses[code]
        course.remove(sid)
        self.save()
        return f"{student.name} ({sid}) dropped {code}. Seats left: {course.seats_left()}"

    def view_student(self, sid):
        student = self.students.get(sid)
        if student is None:
            return f"Student {sid} not found."
        if not student.courses:
            return f"{student.name} ({sid}) has no registered courses."
        lines = [f"{student.name} ({sid}) is registered in:"]
        for code in student.courses:
            lines.append(f"  {code} - {self.courses[code].title}")
        return "\n".join(lines)

    def view_courses(self):
        return "\n".join(str(c) for c in self.courses.values())


MENU = """
===== Student Course Registration =====
1. Register
2. Drop course
3. View student
4. View course list
5. Exit"""

ALIASES = {
    "1": "register", "register": "register",
    "2": "drop", "drop": "drop", "drop course": "drop",
    "3": "view student", "view student": "view student",
    "4": "view courses", "view courses": "view courses",
    "view course list": "view courses", "course list": "view courses",
    "5": "exit", "exit": "exit",
}


def main():
    system = RegistrationSystem()
    while True:
        print(MENU)
        try:
            choice = ALIASES.get(input("Menu: ").strip().lower())
        except EOFError:
            break
        if choice == "register":
            sid = input("Student ID: ").strip()
            name = input("Name: ").strip()
            code = input("Course: ").strip()
            print(system.register(sid, name, code))
        elif choice == "drop":
            sid = input("Student ID: ").strip()
            code = input("Course: ").strip()
            print(system.drop(sid, code))
        elif choice == "view student":
            print(system.view_student(input("Student ID: ").strip()))
        elif choice == "view courses":
            print(system.view_courses())
        elif choice == "exit":
            print("Goodbye!")
            break
        else:
            print("Invalid menu choice. Please try again.")


if __name__ == "__main__":
    main()