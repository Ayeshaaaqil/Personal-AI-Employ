This is a test document for the AI Employee system.

Purpose: Test the file drop workflow

Content:
- This file simulates a document that needs processing
- When dropped in the Inbox folder, the File System Watcher should detect it
- A metadata file should be created in Needs_Action
- The Orchestrator should trigger Claude Code to process it

Expected Actions:
1. Review the file content
2. Determine what action is needed
3. Create a plan in Plans folder
4. Execute the plan
5. Move to Done when complete

Test Date: 2026-03-05
