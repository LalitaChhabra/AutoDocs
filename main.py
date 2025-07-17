#!/usr/bin/env python3
"""
AutoDocs Main Interface

This script provides a simple command-line interface to the AutoDocs orchestrator.
You can use it to record clips, process them, and generate documentation.

Usage examples:
    python main.py                          # Interactive mode
    python main.py --quick                  # Quick single clip recording
    python main.py --gui                    # Launch GUI interface
"""

import argparse
import sys
from pathlib import Path

from autodocs_orchestrator import AutoDocsOrchestrator, quick_record_and_process
from gui_launcher import run_app


def interactive_mode():
    """Interactive command-line interface"""
    print("🚀 Welcome to AutoDocs!")
    print("=" * 50)
    
    orchestrator = AutoDocsOrchestrator()
    
    while True:
        print("\nWhat would you like to do?")
        print("1. Record a new clip")
        print("2. Process recorded clips")
        print("3. Generate final document")
        print("4. View session summary")
        print("5. Load existing session")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        try:
            if choice == "1":
                record_clip_interactive(orchestrator)
            elif choice == "2":
                process_clips_interactive(orchestrator)
            elif choice == "3":
                generate_document_interactive(orchestrator)
            elif choice == "4":
                show_session_summary(orchestrator)
            elif choice == "5":
                load_session_interactive(orchestrator)
            elif choice == "6":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-6.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")


def record_clip_interactive(orchestrator: AutoDocsOrchestrator):
    """Interactive clip recording"""
    print("\n📹 Record New Clip")
    print("-" * 30)
    
    title = input("Enter clip title (or press Enter for auto-generated): ").strip()
    if not title:
        title = None
    
    duration_input = input("Enter duration in seconds (10-30, default 15): ").strip()
    try:
        duration = int(duration_input) if duration_input else 15
        if duration < 10 or duration > 30:
            print("⚠️  Duration should be between 10-30 seconds. Using 15 seconds.")
            duration = 15
    except ValueError:
        print("⚠️  Invalid duration. Using 15 seconds.")
        duration = 15
    
    print(f"\n🔴 Starting recording in 3 seconds...")
    print("Position your screen and get ready!")
    import time
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    try:
        clip = orchestrator.record_clip(duration=duration, title=title)
        print(f"\n✅ Clip recorded successfully!")
        print(f"   Title: {clip['title']}")
        print(f"   Duration: {clip['duration']}s")
        print(f"   Files: {clip['audio_file']}, {clip['gif_file']}")
        
        # Ask if user wants to process immediately
        process_now = input("\n🔄 Process this clip now? (y/n): ").strip().lower()
        if process_now in ['y', 'yes']:
            orchestrator.process_clip(clip['id'])
            print("✅ Clip processed successfully!")
            
    except Exception as e:
        print(f"❌ Recording failed: {str(e)}")


def process_clips_interactive(orchestrator: AutoDocsOrchestrator):
    """Interactive clip processing"""
    unprocessed = [c for c in orchestrator.clips if c['status'] == 'recorded']
    
    if not unprocessed:
        print("\n✅ No clips need processing.")
        return
    
    print(f"\n🔄 Found {len(unprocessed)} clips to process")
    print("-" * 40)
    
    for clip in unprocessed:
        print(f"   {clip['id']}. {clip['title']} ({clip['duration']}s)")
    
    choice = input("\nProcess (a)ll clips or (s)pecific clip? (a/s): ").strip().lower()
    
    try:
        if choice in ['a', 'all']:
            orchestrator.process_all_clips()
            print("✅ All clips processed!")
        elif choice in ['s', 'specific']:
            clip_id = int(input("Enter clip ID: "))
            orchestrator.process_clip(clip_id)
            print(f"✅ Clip {clip_id} processed!")
        else:
            print("❌ Invalid choice.")
            
    except Exception as e:
        print(f"❌ Processing failed: {str(e)}")


def generate_document_interactive(orchestrator: AutoDocsOrchestrator):
    """Interactive document generation"""
    if not orchestrator.clips:
        print("\n⚠️  No clips recorded yet. Record some clips first.")
        return
    
    processed_clips = [c for c in orchestrator.clips if c['status'] == 'processed']
    if not processed_clips:
        print("\n⚠️  No processed clips found. Process clips first.")
        return
    
    print(f"\n📄 Generate Document")
    print("-" * 30)
    print(f"Processed clips: {len(processed_clips)}")
    
    doc_format = input("Choose format - (w)ord, (m)arkdown, or (h)tml? (w/m/h): ").strip().lower()
    
    try:
        if doc_format in ['w', 'word']:
            doc_path = orchestrator.generate_word_document()
            print(f"✅ Word document generated: {doc_path}")
        elif doc_format in ['m', 'markdown']:
            doc_path = orchestrator.generate_markdown_document()
            print(f"✅ Markdown document generated: {doc_path}")
        elif doc_format in ['h', 'html']:
            doc_path = orchestrator.generate_html_document()
            print(f"✅ HTML document generated: {doc_path}")
        else:
            print("❌ Invalid format choice.")
            
    except Exception as e:
        print(f"❌ Document generation failed: {str(e)}")


def show_session_summary(orchestrator: AutoDocsOrchestrator):
    """Show session summary"""
    summary = orchestrator.get_session_summary()
    
    print(f"\n📊 Session Summary")
    print("-" * 30)
    print(f"Session ID: {summary['session_id']}")
    print(f"Total clips: {summary['total_clips']}")
    print(f"Processed clips: {summary['processed_clips']}")
    print(f"Error clips: {summary['error_clips']}")
    print(f"Session directory: {summary['session_dir']}")
    
    if orchestrator.clips:
        print(f"\nClips:")
        for clip in orchestrator.clips:
            status_emoji = {"recorded": "🔴", "processed": "✅", "error": "❌"}.get(clip['status'], "❓")
            print(f"   {status_emoji} {clip['id']}. {clip['title']} ({clip['duration']}s) - {clip['status']}")


def load_session_interactive(orchestrator: AutoDocsOrchestrator):
    """Interactive session loading"""
    print(f"\n📂 Load Existing Session")
    print("-" * 30)
    
    session_dir = input("Enter session directory path: ").strip()
    if not session_dir:
        print("❌ No directory specified.")
        return
    
    try:
        orchestrator.load_session(session_dir)
        print(f"✅ Session loaded successfully!")
        show_session_summary(orchestrator)
    except Exception as e:
        print(f"❌ Failed to load session: {str(e)}")


def quick_mode():
    """Quick single clip mode"""
    print("🚀 Quick Recording Mode")
    print("=" * 30)
    print("This will record a 15-second clip and generate a document.")
    
    input("Press Enter when ready to start recording...")
    
    try:
        doc_path = quick_record_and_process(duration=15, title="Quick Tutorial")
        print(f"✅ Quick tutorial complete!")
        print(f"📄 Document saved: {doc_path}")
    except Exception as e:
        print(f"❌ Quick recording failed: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="AutoDocs - Automated Tutorial Documentation")
    parser.add_argument("--quick", action="store_true", help="Quick single clip recording")
    parser.add_argument("--gui", action="store_true", help="Launch GUI interface")
    
    args = parser.parse_args()
    
    if args.gui:
        print("🚀 Launching GUI interface...")
        run_app()
    elif args.quick:
        quick_mode()
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
