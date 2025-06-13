import time
from datetime import datetime
from pathlib import Path

class TestStep:
    def __init__(self, number, description):
        self.number = number
        self.description = description
        self.status = "⏳"  # Pending
        self.start_time = None
        self.end_time = None
        self.error = None
    
    def start(self):
        self.start_time = time.time()
        self.status = "🔄"  # In Progress
        print(f"\n➡️ Step {self.number}: {self.description}...")
        
    def complete(self, success=True, error=None):
        self.end_time = time.time()
        self.status = "✅" if success else "❌"
        self.error = error
        if success:
            print(f"   ✅ Completed in {self.duration:.2f}s")
        else:
            print(f"   ❌ Failed: {error}")
        
    @property
    def duration(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

def setup_result_directories():
    """Create directories for test results if they don't exist"""
    base_dir = Path(__file__).parent / "test_results"
    success_dir = base_dir / "success"
    error_dir = base_dir / "error"
    
    success_dir.mkdir(parents=True, exist_ok=True)
    error_dir.mkdir(parents=True, exist_ok=True)
    
    return success_dir, error_dir

def save_test_artifacts(is_success, report_content, screenshot_path=None):
    """Save test report and screenshot in appropriate directory"""
    success_dir, error_dir = setup_result_directories()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    
    # Determine target directory
    target_dir = success_dir if is_success else error_dir
    
    # Save report
    report_path = target_dir / f"test_report_{timestamp}.txt"
    report_path.write_text(report_content, encoding='utf-8')
    
    # Return the screenshot path if it's already in the correct directory
    if screenshot_path:
        screenshot_file = Path(screenshot_path)
        if screenshot_file.parent == target_dir:
            return str(report_path), str(screenshot_file)
    
    return str(report_path), screenshot_path

def create_test_report(test_steps, final_status, error_message=None, screenshot_path=None):
    """Generate a detailed test report with all steps and results"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create the report content
    report_lines = [
        "╔═══════════════════════════════════════════════════════════════",
        "║             StyleNest E-commerce Testing Report               ",
        "╚═══════════════════════════════════════════════════════════════",
        "",
        f"📅 Test Execution Date: {timestamp}",
        "📍 Test Environment: Local Development",
        f"🌐 Base URL: http://localhost:8080",
        "",
        "🎯 Test Summary",
        "--------------",
        f"Final Status: {'✅ PASSED' if final_status else '❌ FAILED'}",
        "",
        "📋 Detailed Step Results:",
        "----------------------"
    ]
    
    # Add each step result
    completed_steps = [step for step in test_steps if step.status != "⏳"]
    for step in completed_steps:
        duration = f"{step.duration:.2f}s" if step.duration else "N/A"
        report_lines.append(f"{step.status} Step {step.number}: {step.description}")
        if step.duration:
            report_lines.append(f"   ⏱️ Duration: {duration}")
        if step.error:
            report_lines.append(f"   ⚠️ Error: {step.error}")
        report_lines.append("")
    
    # Add test statistics
    total_duration = sum(step.duration or 0 for step in completed_steps)
    passed_steps = sum(1 for step in completed_steps if step.status == "✅")
    total_steps = len(completed_steps)
    
    report_lines.extend([
        "📊 Test Statistics",
        "----------------",
        f"Total Steps Executed: {total_steps}",
        f"Steps Passed: {passed_steps}",
        f"Steps Failed: {total_steps - passed_steps}",
        f"Total Duration: {total_duration:.2f} seconds",
        ""
    ])
    
    # Add error message if test failed
    if error_message:
        report_lines.extend([
            "❌ Error Details",
            "--------------",
            error_message,
            ""
        ])
    
    report_lines.append("═══════════════ End of Test Report ═══════════════")
    
    # Convert report lines to a single string
    report_content = "\n".join(report_lines)
    
    # Save artifacts to appropriate directory
    report_path, new_screenshot_path = save_test_artifacts(final_status, report_content, screenshot_path)
    
    # Print locations of saved files
    print(f"\nTest Report saved: {report_path}")
    if new_screenshot_path:
        print(f"Screenshot saved: {new_screenshot_path}")
    
    return report_path, new_screenshot_path
