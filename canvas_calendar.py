import os
from datetime import datetime, timedelta
from canvasapi import Canvas
from dotenv import load_dotenv

# Try to import rich, but don't fail if it's not available
try:
    from rich.console import Console
    from rich.table import Table
    from rich.prompt import Prompt
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

def get_canvas_credentials():
    """Get Canvas credentials from environment variables or user input."""
    load_dotenv()
    url = os.getenv('CANVAS_URL')
    token = os.getenv('CANVAS_TOKEN')
    
    if not url or not token:
        if RICH_AVAILABLE:
            print("Please enter your Canvas credentials:")
            url = Prompt.ask("Canvas URL (e.g., https://canvas.instructure.com)")
            token = Prompt.ask("Canvas API Token", password=True)
        else:
            url = input("Canvas URL (e.g., https://canvas.instructure.com): ")
            token = input("Canvas API Token: ")
        
        # Save credentials to .env file
        with open('.env', 'w') as f:
            f.write(f'CANVAS_URL={url}\n')
            f.write(f'CANVAS_TOKEN={token}\n')
    
    return url, token

def get_canvas_assignments():
    """Get assignments from Canvas for the next 10 weeks."""
    try:
        url, token = get_canvas_credentials()
        canvas = Canvas(url, token)
        return get_assignments(canvas)
    except Exception as e:
        print(f"Error getting assignments: {str(e)}")
        return []

def get_canvas_schedule():
    """Get class schedule from Canvas."""
    try:
        url, token = get_canvas_credentials()
        canvas = Canvas(url, token)
        courses = canvas.get_courses()
        
        schedule = []
        for course in courses:
            try:
                course_name = getattr(course, 'name', f'Course {course.id}')
                schedule.append({
                    'id': course.id,
                    'name': course_name,
                    'code': getattr(course, 'course_code', ''),
                    'term': getattr(course, 'term', {}).get('name', '')
                })
            except Exception as e:
                print(f"Error getting schedule for course {getattr(course, 'id', 'Unknown')}: {str(e)}")
        
        return schedule
    except Exception as e:
        print(f"Error getting schedule: {str(e)}")
        return []

def get_assignments(canvas):
    """Fetch assignments from all courses for the next 10 weeks."""
    assignments = []
    courses = canvas.get_courses()
    
    for course in courses:
        try:
            # Get course name, fallback to course ID if name is not available
            course_name = getattr(course, 'name', f'Course {course.id}')
            print(f"Fetching assignments for {course_name}...")
            
            course_assignments = course.get_assignments()
            for assignment in course_assignments:
                if assignment.due_at:
                    due_date = datetime.strptime(assignment.due_at, '%Y-%m-%dT%H:%M:%SZ')
                    if due_date <= datetime.now() + timedelta(weeks=10):
                        assignments.append({
                            'name': assignment.name,
                            'course': course_name,
                            'due_date': due_date.isoformat()  # Convert to ISO format for JSON
                        })
        except Exception as e:
            print(f"Error fetching assignments for course {getattr(course, 'id', 'Unknown')}: {str(e)}")
    
    if not assignments:
        print("\nNo assignments found for the next 10 weeks.")
    
    return sorted(assignments, key=lambda x: x['due_date'])

def display_calendar(assignments):
    """Display assignments in a calendar format."""
    if RICH_AVAILABLE:
        display_calendar_rich(assignments)
    else:
        display_calendar_simple(assignments)

def display_calendar_rich(assignments):
    """Display assignments in a calendar format using rich."""
    console = Console()
    
    # Group assignments by week
    current_week = None
    week_assignments = []
    
    for assignment in assignments:
        week_start = assignment['due_date'] - timedelta(days=assignment['due_date'].weekday())
        
        if current_week != week_start:
            if current_week is not None:
                display_week_rich(console, current_week, week_assignments)
            current_week = week_start
            week_assignments = []
        
        week_assignments.append(assignment)
    
    if week_assignments:
        display_week_rich(console, current_week, week_assignments)

def display_week_rich(console, week_start, assignments):
    """Display assignments for a specific week using rich."""
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

def display_calendar_simple(assignments):
    """Display assignments in a simple text format."""
    current_week = None
    week_assignments = []
    
    for assignment in assignments:
        week_start = assignment['due_date'] - timedelta(days=assignment['due_date'].weekday())
        
        if current_week != week_start:
            if current_week is not None:
                display_week_simple(current_week, week_assignments)
            current_week = week_start
            week_assignments = []
        
        week_assignments.append(assignment)
    
    if week_assignments:
        display_week_simple(current_week, week_assignments)

def display_week_simple(week_start, assignments):
    """Display assignments for a specific week in simple text format."""
    print(f"\nWeek of {week_start.strftime('%B %d, %Y')}")
    print("-" * 50)
    
    for day in range(7):
        current_day = week_start + timedelta(days=day)
        day_assignments = [a for a in assignments if a['due_date'].date() == current_day.date()]
        
        print(f"\n{current_day.strftime('%A')}:")
        if day_assignments:
            for assignment in day_assignments:
                print(f"  - {assignment['name']} ({assignment['course']})")
        else:
            print("  No assignments")
    print()

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
