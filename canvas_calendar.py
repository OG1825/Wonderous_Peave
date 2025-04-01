import os
from datetime import datetime, timedelta
from canvasapi import Canvas
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from dotenv import load_dotenv

def get_canvas_credentials():
    """Get Canvas credentials from environment variables or user input."""
    load_dotenv()
    url = os.getenv('CANVAS_URL')
    token = os.getenv('CANVAS_TOKEN')
    
    if not url or not token:
        print("Please enter your Canvas credentials:")
        url = Prompt.ask("Canvas URL (e.g., https://canvas.instructure.com)")
        token = Prompt.ask("Canvas API Token", password=True)
        
        # Save credentials to .env file
        with open('.env', 'w') as f:
            f.write(f'CANVAS_URL={url}\n')
            f.write(f'CANVAS_TOKEN={token}\n')
    
    return url, token

def get_assignments(canvas):
    """Fetch assignments from specific courses for the next 10 weeks."""
    assignments = []
    target_courses = ['ENG 30', 'ECON 3', 'SYN 1', 'MGT 45']
    courses = canvas.get_courses()
    
    for course in courses:
        try:
            # Get course name, fallback to course ID if name is not available
            course_name = getattr(course, 'name', f'Course {course.id}')
            
            # Only process if the course name contains one of our target courses
            if any(target in course_name.upper() for target in target_courses):
                print(f"Fetching assignments for {course_name}...")
                
                course_assignments = course.get_assignments()
                for assignment in course_assignments:
                    if assignment.due_at:
                        due_date = datetime.strptime(assignment.due_at, '%Y-%m-%dT%H:%M:%SZ')
                        if due_date <= datetime.now() + timedelta(weeks=10):
                            assignments.append({
                                'name': assignment.name,
                                'course': course_name,
                                'due_date': due_date
                            })
        except Exception as e:
            print(f"Error fetching assignments for course {getattr(course, 'id', 'Unknown')}: {str(e)}")
    
    if not assignments:
        print("\nNo assignments found for the specified courses (ENG 30, ECON 3, SYN 1, MGT 45)")
        print("Please check if the course names match exactly with your Canvas courses.")
    
    return sorted(assignments, key=lambda x: x['due_date'])

def display_calendar(assignments):
    """Display assignments in a calendar format using rich."""
    console = Console()
    
    # Group assignments by week
    current_week = None
    week_assignments = []
    
    for assignment in assignments:
        week_start = assignment['due_date'] - timedelta(days=assignment['due_date'].weekday())
        
        if current_week != week_start:
            if current_week is not None:
                display_week(console, current_week, week_assignments)
            current_week = week_start
            week_assignments = []
        
        week_assignments.append(assignment)
    
    if week_assignments:
        display_week(console, current_week, week_assignments)

def display_week(console, week_start, assignments):
    """Display assignments for a specific week."""
    table = Table(title=f"Week of {week_start.strftime('%B %d, %Y')}")
    table.add_column("Day", style="cyan")
    table.add_column("Assignments", style="green")
    
    for day in range(7):
        current_day = week_start + timedelta(days=day)
        day_assignments = [a for a in assignments if a['due_date'].date() == current_day.date()]
        
        if day_assignments:
            assignments_text = "\n".join([
                f"{a['name']} ({a['course']})"
                for a in day_assignments
            ])
        else:
            assignments_text = "No assignments"
        
        table.add_row(
            current_day.strftime('%A'),
            assignments_text
        )
    
    console.print(table)
    console.print()

def main():
    """Main function to run the Canvas calendar application."""
    try:
        url, token = get_canvas_credentials()
        
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        print(f"\nConnecting to Canvas at {url}...")
        canvas = Canvas(url, token)
        
        # Test the connection by trying to get user info
        try:
            user = canvas.get_current_user()
            print(f"Successfully connected as: {user.name}")
        except Exception as e:
            print("\nError: Could not connect to Canvas. Please check:")
            print("1. Your Canvas URL is correct (e.g., https://youruniversity.instructure.com)")
            print("2. Your API token is valid and has the correct permissions")
            print("3. You have an active internet connection")
            print("\nTo get a new API token:")
            print("1. Log into Canvas in your web browser")
            print("2. Go to Account > Settings")
            print("3. Scroll to 'Approved Integrations'")
            print("4. Click 'New Access Token'")
            print("5. Give it a name and copy the token")
            return
        
        print("\nFetching assignments...")
        assignments = get_assignments(canvas)
        
        if not assignments:
            print("No assignments found for the next 10 weeks.")
            return
        
        print("\nYour assignments for the next 10 weeks:")
        display_calendar(assignments)
        
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        print("\nPlease check your credentials and try again.")
        print("You can delete the .env file to start fresh:")
        print("rm .env")

if __name__ == "__main__":
    main() 
