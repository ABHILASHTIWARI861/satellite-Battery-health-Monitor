"""
Test Word Paragraph Replacement via win32com
Finds paragraphs matching unique keywords (< 255 chars) and updates Range.Text
"""

import win32com.client
import os

word = win32com.client.Dispatch("Word.Application")
word.Visible = False
word.DisplayAlerts = False

try:
    doc = word.Documents.Open(os.path.abspath(r"C:\Users\LENOVO\OneDrive\Desktop\test_copy.docx"))
    
    # Test finding paragraph containing "implemented with Next.js"
    found = False
    for p in doc.Paragraphs:
        txt = p.Range.Text
        if "Next.js" in txt:
            print("Found Frontend paragraph:", txt[:60])
            p.Range.Text = "The mission control frontend is implemented with Vanilla HTML5, Modern CSS3 (Cyberpunk Glassmorphism), and Vanilla JavaScript (ES6+), communicating with an asynchronous FastAPI backend via bidirectional /ws/telemetry WebSockets. The interface features a real-time HTML5 Canvas 3D Spacecraft Visualizer that dynamically renders satellite orbit orientation, solar panel sun-tracking, and active RCS thruster plumes.\r"
            found = True
            break
            
    print("Replaced Frontend paragraph:", found)
    doc.Save()
    doc.Close()
finally:
    word.Quit()
print("Done test.")
